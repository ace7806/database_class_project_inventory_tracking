from flask import jsonify
from app.dao.transaction import TransactionDAO
from app.dao.rack import RackDAO
from app.dao.warehouse import WarehouseDAO
from app.dao.user import UserDAO
from app.dao.parts import PartsDAO
from app.dao.supplier import SupplierDAO
from datetime import datetime


class TransactionHandler:
    #KEYS
    incoming_keys = ['tid','incid', 'sid', 'tdate','tquantity','pid','uid','wid']
    outgoing_keys = ['tid', 'outid','obuyer', 'tdate', 'tquantity','pid','uid','wid']
    exchange_keys = ['tid', 'tranid','taction', 'tdate', 'tquantity','pid','uid','wid']
    profit_yield = 1.10

    def validate_tdate(self, tdate):
        try:
            if tdate=='now()': return True
            else:
            # Validate the date format (PostgreSQL default format is 'YYYY-MM-DD')
                datetime.strptime(tdate, '%Y-%m-%d')
                return True
        except ValueError:
            # The date format is incorrect
            return False
            


    def build_attributes_dict(self, attr_array, ttype):
        keys = []
        if ttype == "incoming":
            keys = self.incoming_keys
        elif ttype ==  "outgoing":
            keys = self.outgoing_keys
        elif ttype == "exchange":
            keys = self.exchange_keys
        return dict(zip(keys, attr_array))

    #Only really used for incoming transactions as per spec
    def build_least_cost_dict(self, rows):
        keys = ['date','amount']
        return dict(zip(keys, rows))
    
    def validate_outgoing(self, pid, uid, wid, tquantity, obuyer):
        
        if not isinstance(pid, int):
            raise ValueError('pid needs to be a positive number')
        if not isinstance(uid, int):
            raise ValueError('uid needs to be a positive number')
        if not isinstance(wid, int):
            raise ValueError('wid needs to be a positive number')
        if not isinstance(tquantity, int):
            raise ValueError('tquantity needs to be a positive number')

      
        if tquantity <=0: raise ValueError('tquantity shouldnt be less than zero')

        part_dao = PartsDAO()
        supplier_dao = SupplierDAO()
        rack_dao = RackDAO()
        user_dao = UserDAO()
        warehouse_dao = WarehouseDAO()

        part_row = part_dao.getPartById(pid)
        rid = rack_dao.get_rid_from_wid_and_pid(wid,pid)
        user_row = user_dao.getUserById(uid)
        warehouse_row = warehouse_dao.get_warehouse_by_id(wid)

        if not warehouse_row:
            raise ValueError('Provided WID invalid')
        if not part_row:
            raise ValueError('Provided PID invalid')
        if not rid:
            raise ValueError(f'Warehouse {wid}, does not have a rack with part {pid}')
        if not user_row:
            raise ValueError('Provided UID invalid')

        #validate user belongs to warehouse
        user_wid = user_dao.getUserWarehouse(uid)[0]
        if user_wid != wid:
            raise ValueError('User does work for given warehouse')
        
        if not obuyer:
            raise ValueError('Buyer is not set')

        rack_dao = RackDAO()
        curr_quantity = rack_dao.get_rack_quantity(rid)
        if curr_quantity < tquantity:
            raise ValueError('Unable to complete transaction; Not enough parts in rack')

        return True


    def validate_incoming(self, pid, sid, uid, wid, tquantity):
        """
        Checks entities exist and that the transaction is overall valid.
        """
        if not isinstance(pid, int):
            raise ValueError('pid needs to be a positive number')
        if not isinstance(sid, int):
            raise ValueError('sid needs to be a positive number')
        if not isinstance(uid, int):
            raise ValueError('uid needs to be a positive number')
        if not isinstance(wid, int):
            raise ValueError('wid needs to be a positive number')
        if not isinstance(tquantity, int):
            raise ValueError('tquantity needs to be a positive number')

                 
        part_dao = PartsDAO()
        supplier_dao = SupplierDAO()
        rack_dao = RackDAO()
        user_dao = UserDAO()
        warehouse_dao = WarehouseDAO()

        part_row = part_dao.getPartById(pid)
        supplier_row = supplier_dao.get_supplier_by_ID(sid)
        # find rack
        rid = rack_dao.get_rid_from_wid_and_pid(wid,pid)
        user_row = user_dao.getUserById(uid)
        warehouse_row = warehouse_dao.get_warehouse_by_id(wid)

        if not part_row:
            raise ValueError('Provided PID invalid')
        if not supplier_row:
            raise ValueError('Provided SID invalid')
        if not rid:
            raise ValueError(f'No rack with pid:{pid} was found in warehouse {wid}')
        if not user_row:
            raise ValueError('Provided UID invalid')
        if not warehouse_row:
            raise ValueError('Provided WID invalid')
        
        if tquantity <=0: raise ValueError('tquantity shouldnt be less than zero')

        supid = supplier_dao.get_supply_by_sid_and_pid(sid,pid)
        if not supid:
            raise ValueError('Provided supplier does not provide this part')

        #validate user belongs to warehouse
        user_wid = user_dao.getUserWarehouse(uid)[0]
        if user_wid != wid:
            raise ValueError('User does work for given warehouse')
        
        if rack_dao.get_rack_warehouse(rid)[0] != wid:
            raise ValueError('Rack does not exist in warehouse')

        rack_pid = rack_dao.get_rack_part(rid)[0]
        if rack_pid != pid:
           raise ValueError('Rack does not hold provided part')

        supplier_stock = supplier_dao.get_supplier_supplies_stock_by_supid(supid)
        if supplier_stock < tquantity:
           raise ValueError('Supplier does not have enough stock')

        rack_capacity = rack_dao.get_rack_capacity(rid)
        curr_rack_quantity = rack_dao.get_rack_quantity(rid)
        if (rack_capacity-curr_rack_quantity) < tquantity:
           raise ValueError('Rack cannot hold quantity provided; not enough space.')

        warehouse_budget = warehouse_dao.get_warehouse_budget(wid)
        total_cost = tquantity*part_dao.get_part_price(pid)

        if warehouse_budget < total_cost:
           raise ValueError('Warehouse budget is not enough for transaction')

        return True


    #----------------------CRUD for incoming----------------------
    #READ-----
    def get_all_incoming(self):
        dao = TransactionDAO()
        all_incoming = dao.get_all_incoming()
        result = []
        for row in all_incoming:
            result.append(self.build_attributes_dict(row,"incoming"))
        return jsonify(incoming=result)
    
    def get_incoming_by_id(self, incid):
        dao = TransactionDAO()
        row = dao.get_incoming_by_id(incid)
        if not row:
            return jsonify(Error = "Incoming transaction not found"), 404
        else:
            incoming = self.build_attributes_dict(row[0], "incoming") #note: dao.get_incoming_by_id returns a list of rows
            return jsonify(Incoming = incoming)
    

    def get_warehouse_least_cost(self, wid, json, amount=3):
        dao = TransactionDAO()
        if not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Warehouse not found'), 404
        uid = json.get('User_id', None)
        user_warehouse_tuple = UserDAO().getUserWarehouse(uid)
        if not user_warehouse_tuple:
            return jsonify(Error='User has no access to warehouse'), 403
        if user_warehouse_tuple[0] != wid: #added this validation
            return jsonify(Error='User has no access to warehouse.'), 403
        transaction_list = dao.get_warehouse_least_cost(wid, amount)
        result = [self.build_least_cost_dict(row) for row in transaction_list]
        return jsonify(Dates=result)

    #CREATE-----
    def insert_incoming(self, json):
        KEYS_LENGTH = 5 #modify to fit all needed attr
        if len(json) != 5 and len(json)!= 6:
            return jsonify(Error='Incorrent amount of keys sent in POST'), 400
        pid = json.get('pid')
        sid = json.get('sid')
        uid = json.get('uid')
        wid = json.get('wid')
        tquantity = json.get('tquantity')
        tdate = json.get('tdate', 'now()')

        try:
            self.validate_incoming(pid, sid, uid, wid, tquantity)
        except ValueError as e:
            return jsonify(Error = e.args[0]), 400

        if not self.validate_tdate(tdate): return jsonify('tdate not valid'), 400
        transaction_dao = TransactionDAO()
        incoming_dao = TransactionDAO()
        warehouse_dao = WarehouseDAO()
        rack_dao = RackDAO()
        supplier_dao = SupplierDAO()
        rid = rack_dao.get_rid_from_wid_and_pid(wid,pid)
        tid = transaction_dao.insert_transaction(tquantity, pid, wid, uid, tdate)
        
        #create entry in incoming transactions
        incid = incoming_dao.insert_incoming(sid, tid)
        tdate = incoming_dao.get_transaction_date(tid)
        attr_array = [tid, incid, sid, tdate, tquantity, pid, uid, wid]

        warehouse_budget = warehouse_dao.get_warehouse_budget(wid)
        new_budget = warehouse_budget - PartsDAO().get_part_price(pid)*tquantity

        wid = warehouse_dao.set_warehouse_budget(wid, new_budget)

        new_quantity = rack_dao.get_rack_quantity(rid) + tquantity
        rid = rack_dao.set_rack_quantity(rid, new_quantity)

        new_stock = supplier_dao.get_supplier_supplies_stock_by_sid_and_pid(sid, pid) - tquantity
        sid, pid = supplier_dao.edit_supplies_stock_by_sid_and_pid(sid, pid, new_stock)

        result = self.build_attributes_dict(attr_array, 'incoming')
        return jsonify(Incoming=result), 201


    #UPDATE-----
    def update_incoming(self, incid, json):
        if len(json)!=7: return jsonify(Error="Unexpected/Missing attributes in request.")
        dao = TransactionDAO()
        tquantity = json.get('tquantity', None)
        ttotal = json.get('ttotal', None)
        pid = json.get('pid', None)
        sid = json.get('sid', None)
        rid = json.get('rid', None)
        uid = json.get('uid', None)
        wid = json.get('wid', None)
        if incid and tquantity and ttotal and pid and sid and rid and uid and wid and dao.get_incoming_by_id(incid):
            tid = dao.get_tid_from_incoming(incid)
            dao.update_transaction(tquantity, ttotal, pid, sid, rid, uid, tid)
            dao.update_incoming(wid, tid)
            tdate = dao.get_transaction_date(tid)
            attr_array = [tid, incid, tdate, tquantity, ttotal, pid, sid, rid, uid, wid]
            result = self.build_attributes_dict(attr_array, "incoming")
            return jsonify(Incoming=result)
        else:
            return jsonify(Error="Unexpected/Missing attributes in request.")
    

    #DELETE (ONLY FOR DEBUGGING)
    def delete_incoming(self, incid):
        dao = TransactionDAO()
        if not dao.get_incoming_by_id(incid):
            return jsonify(Error="Incoming transaction not found."), 404
        else:
            tid = dao.get_tid_from_incoming(incid)
            print("incoming id: " + str(incid))
            print("transaction id: "+ str(tid))
            ret_incid = dao.delete_incoming(incid)
            ret_tid = dao.delete_transaction(tid)
            print("Removed incoming: "+str(incid)+" and Transaction: "+str(tid))
            return jsonify(DeleteStatus="OK"), 200
    
    #----------------------CRUD for outgoing----------------------

    #READ-----
    def get_all_outgoing(self):
        dao = TransactionDAO()
        all_outgoing = dao.get_all_outgoing()
        result = []
        for row in all_outgoing:
            result.append(self.build_attributes_dict(row, "outgoing"))
        return jsonify(Outgoing=result)

    def get_outgoing_by_id(self, outid):
        dao = TransactionDAO()
        row = dao.get_outgoing_by_id(outid)
        if not row:
            return jsonify(Error = "Outgoing transaction not found"), 404
        else:
            outgoing = self.build_attributes_dict(row[0],"outgoing")
            return jsonify(Outgoing = outgoing)

    #CREATE-----
    def insert_outgoing(self, json):
        """
        Create outgoing transaction.
        Mutates outgoingt, transaction, warehouse,
        and rack related to transaction
        """
        KEYS_LENGTH = 5
        if len(json) != 5 and len(json)!= 6:
            return jsonify(Error='Incorrent amount of keys sent in POST'), 400

        tquantity = json.get('tquantity', None)
        obuyer = json.get('obuyer', None)
        pid = json.get('pid', None)
        uid = json.get('uid', None)
        wid = json.get('wid', None)
        tdate = json.get('tdate', 'now()')
        
        try:
            self.validate_outgoing(pid, uid, wid, tquantity, obuyer)
        except ValueError as e:
            return jsonify(Error = e.args[0]), 400

        if not self.validate_tdate(tdate): return jsonify('tdate not valid'), 400
        rid = RackDAO().get_rid_from_wid_and_pid(wid,pid)
        #mutations
        transaction_dao = outgoing_dao = TransactionDAO()
        tid = transaction_dao.insert_transaction(tquantity, pid, wid, uid, tdate)
        outid = outgoing_dao.insert_outgoing(obuyer, tid)
        tdate = transaction_dao.get_transaction_date(tid)
        attr_array = [tid,outid, obuyer, tdate, tquantity, pid, uid, wid]

        #update tables
        warehouse_dao = WarehouseDAO()
        pprice = PartsDAO().get_part_price(pid)
        new_budget = warehouse_dao.get_warehouse_budget(wid) + pprice*tquantity*self.profit_yield
        wid = warehouse_dao.set_warehouse_budget(wid, new_budget)

        new_quantity = RackDAO().get_rack_quantity(rid) - tquantity
        rid = RackDAO().set_rack_quantity(rid, new_quantity)

        result = self.build_attributes_dict(attr_array, "outgoing")
        return jsonify(Outgoing=result), 201



    #UPDATE-----
    def update_outgoing(self, outid, json):
        if len(json)!=8: return jsonify(Error="Unexpected/Missing attributes in request.")
        dao = TransactionDAO()
        tquantity = json.get('tquantity', None)
        ttotal = json.get('ttotal', None)
        pid = json.get('pid', None)
        sid = json.get('sid', None)
        rid = json.get('rid', None)
        uid = json.get('uid', None)
        wid = json.get('wid', None)
        obuyer = json.get('obuyer', None)
        if outid and tquantity and ttotal and pid and sid and rid and uid and wid and obuyer and dao.get_outgoing_by_id(outid):
            tid = dao.get_tid_from_outgoing(outid)
            dao.update_transaction(tquantity, ttotal, pid, sid, rid, uid, tid)
            dao.update_outgoing(outid, obuyer, wid)
            tdate = dao.get_transaction_date(tid)
            attr_array = [tid,outid, obuyer, wid, tdate, tquantity, ttotal, pid, sid, rid, uid]
            result = self.build_attributes_dict(attr_array, "outgoing")
            return jsonify(Incoming=result)
        else:
            return jsonify(Error="Unexpected/Missing attributes in request.")

    #----------------------CRUD for exchange----------------------
    
    #READ-----
    def get_all_exchange(self):
        dao = TransactionDAO()
        all_exchange = dao.get_all_exchange()
        result = []
        for row in all_exchange:
            result.append(self.build_attributes_dict(row, "exchange"))
        return jsonify(exchange=result)
    
    def get_exchange_by_id(self, tranid):
        dao = TransactionDAO()
        row = dao.get_exchange_by_id(tranid)
        if not row:
            return jsonify(Error = "Exchange transaction not found"), 404
        else:
            result = self.build_attributes_dict(row[0], "exchange")
            return jsonify(exchange = result)
    

    #CREATE-----
    def validate_exchange(self, tquantity,ttotal,pid,sid, outgoing_rid, incoming_rid, outgoing_uid, incoming_uid, outgoing_wid, incoming_wid):
        part_dao = PartsDAO()
        supplier_dao = SupplierDAO()
        rack_dao = RackDAO()
        user_dao = UserDAO()
        warehouse_dao = WarehouseDAO()

        part_row = part_dao.getPartById(pid)
        supplier_row = supplier_dao.get_supplier_by_ID(sid)

        outgoing_rack_row = rack_dao.get_rack_by_id(outgoing_rid)
        incoming_rack_row = rack_dao.get_rack_by_id(incoming_rid)
        
        outgoing_user_row = user_dao.getUserById(outgoing_uid)
        incoming_user_row = user_dao.getUserById(incoming_uid)

        outgoing_warehouse_row = warehouse_dao.get_warehouse_by_id(outgoing_wid)
        incoming_warehouse_row = warehouse_dao.get_warehouse_by_id(incoming_wid)
        
        if not part_row:
            raise ValueError('Provided PID invalid')
        if not supplier_row:
            raise ValueError('Provided SID invalid')
        if not outgoing_rack_row:
            raise ValueError('Provided outgoing RID invalid')
        if not incoming_rack_row:
            raise ValueError('Provided incoming RID invalid')
        if not outgoing_user_row:
            raise ValueError('Provided outgoing UID invalid')
        if not incoming_user_row:
            raise ValueError('Provided incoming UID invalid')
        if not outgoing_warehouse_row:
            raise ValueError('Provided outgoing WID invalid')
        if not incoming_warehouse_row:
            raise ValueError('Provided incoming WID invalid')
        
        supid = supplier_dao.get_supply_by_sid_and_pid(sid,pid)
        if not supid:
            raise ValueError('Provided supplier does not provide this part')

        #validate user belongs to warehouse
        outgoing_user_wid = user_dao.getUserWarehouse(outgoing_uid)[0]
        if outgoing_user_wid != outgoing_wid:
            raise ValueError('User does work for given outgoing warehouse')

        incoming_user_wid = user_dao.getUserWarehouse(incoming_uid)[0]
        if incoming_user_wid != incoming_wid:
            raise ValueError('User does work for given incoming warehouse')

        outgoing_rack_pid = rack_dao.get_rack_part(outgoing_rid)[0]
        if outgoing_rack_pid != pid:
           raise ValueError('Outgoing Rack does not hold provided part')

        incoming_rack_pid = rack_dao.get_rack_part(incoming_rid)[0]
        if incoming_rack_pid != pid:
           raise ValueError('Incoming Rack does not hold provided part')
        return True


    def insert_exchange(self, json):
        if len(json) != 6 and len(json)!= 7:
            return jsonify(Error='Incorrent amount of keys sent in POST'), 400
        tquantity = json.get('tquantity', None)
        pid = json.get('pid', None)
        sending_wid = json.get('sending_wid', None)
        receiving_wid = json.get('receiving_wid', None)
        sending_uid = json.get('sending_uid', None)
        receiving_uid = json.get('receiving_uid', None)
        tdate = json.get('tdate', 'now()')

        if not self.validate_tdate(tdate): return jsonify('tdate not valid'), 400
        if not isinstance(tquantity, int) or tquantity <=0: return jsonify(Error = 'tquantity should be present as a positive int'), 400
        if sending_wid==receiving_wid: return jsonify('same warehouse transfers are not allowed'), 400
        tdao = TransactionDAO()
        rdao = RackDAO()
        outgoing_arr_val = tdao.is_exchange_sending_valid(tquantity,sending_uid, sending_wid, pid)
        incoming_arr_val = tdao.is_exchange_receiving_valid(tquantity, receiving_uid, receiving_wid, pid)

        if not outgoing_arr_val: return jsonify(Error = 'invalid outgoing entities'), 400
        elif not outgoing_arr_val[0][0]: return jsonify(Error = 'not enough part quantity inside outgoing rack'), 400

        if not incoming_arr_val: return jsonify(Error = 'invalid incoming entities'), 400
        elif not incoming_arr_val[0][0]: return jsonify(Error = 'not enough capacity'), 400

        sending_rid = rdao.get_rid_from_wid_and_pid(sending_wid,pid)
        receiving_rid = rdao.get_rid_from_wid_and_pid(receiving_wid,pid)
        receiving_rack_quant = rdao.get_rack_quantity(receiving_rid)
        sending_rack_quant = rdao.get_rack_quantity(sending_rid)

        sending_new_quantity = sending_rack_quant - tquantity
        rdao.set_rack_quantity(sending_rid, sending_new_quantity)

        receiving_new_quantity = receiving_rack_quant + tquantity
        rdao.set_rack_quantity(receiving_rid, receiving_new_quantity)

        sending_tid = tdao.insert_transaction(tquantity, pid, sending_wid, sending_uid, tdate)
        sending_tranid = tdao.insert_exchange("sending", sending_tid)
        sending_tdate = tdao.get_transaction_date(sending_tid)

        receiving_tid = tdao.insert_transaction(tquantity, pid, receiving_wid, receiving_uid, tdate)
        receiving_tranid = tdao.insert_exchange('receiving', receiving_tid)
        receiving_tdate = tdao.get_transaction_date(receiving_tid)
        
        sending_attr_array = [sending_tid,sending_tranid, "sending", sending_tdate, tquantity, pid, sending_uid, sending_wid]
        receiving_attr_array = [receiving_tid,receiving_tranid, 'receiving', receiving_tdate, tquantity, pid, receiving_uid, receiving_wid]

        sending_result = self.build_attributes_dict(sending_attr_array, "exchange")
        receiving_result = self.build_attributes_dict(receiving_attr_array, "exchange")
   
        result = [sending_result,receiving_result]
        return jsonify(exchange=result), 201
    
    #UPDATE-----
    def update_exchange(self, tid, json):
        return
