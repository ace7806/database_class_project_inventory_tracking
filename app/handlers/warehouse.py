from flask import jsonify
from app.dao.warehouse import WarehouseDAO
from app.dao.user import UserDAO
from app.dao.rack import RackDAO
#TODO(xavier)
class WarehouseHandler:
    def build_warehouse_dict(self, rows):
        keys = ['wid', 'budget', 'wname', 'wcity', 'wemail', 'wphone']
        return dict(zip(keys, rows))

    def build_warehouse_attributes(self, wid, wname, wcity, wemail, wphone, budget):
        return {
                'wid':wid,
                'budget': budget,
                'wname':wname,
                'wcity':wcity,
                'wemail':wemail,
                'wphone':wphone
                }

    #Used for routes where we want wid and a count of most something
    def build_most_dict(self, rows):
        keys = ['wid', 'count']
        return dict(zip(keys, rows))

    def get_all_warehouses(self):
        dao = WarehouseDAO()
        warehouse_list = dao.get_all_warehouses()
        result = [self.build_warehouse_dict(row) for row in warehouse_list]
        return jsonify(Warehouses=result)

    def get_warehouse_by_id(self, wid):
        dao = WarehouseDAO()
        row = dao.get_warehouse_by_id(wid)
        if not row:
            return jsonify(Error = "Warehouse not found"), 404
        else:
            row = row[0]
            warehouse = self.build_warehouse_dict(row)
            return jsonify(Warehouse = warehouse)

    def get_warehouse_by_name(self, wname):
        dao = WarehouseDAO()
        row = dao.get_warehouse_by_name(wname)
        if not row:
            return jsonify(Error = "Warehouse not found"), 404
        else:
            warehouse = self.build_warehouse_dict(row)
            return jsonify(Warehouse = warehouse)

    #amount specified in project specs
    def get_warehouse_most_racks(self,amount=10):
        dao = WarehouseDAO()
        rack_list = dao.get_warehouse_most_racks(amount)
        if not rack_list:
            return jsonify(Error = 'Warehouses not found'), 404
        else:
            result = [self.build_most_dict(row) for row in rack_list]
            return jsonify(Warehouses=result)

    def get_warehouse_most_incoming(self, amount=5):
        dao = WarehouseDAO()
        warehouse_list = dao.get_warehouse_most_incoming(amount)
        result = [self.build_most_dict(row) for row in warehouse_list]
        return jsonify(Warehouses=result)

    def get_warehouse_least_outgoing(self, amount=3):
        dao = WarehouseDAO()
        warehouse_list = dao.get_warehouse_least_outgoing(amount)
        #use most even though its least, works the same(bad name)
        result = [self.build_most_dict(row) for row in warehouse_list]
        return jsonify(Warehouses=result)

    def get_warehouse_most_deliver(self, amount=5):
        dao = WarehouseDAO()
        warehouse_list = dao.get_warehouse_most_deliver(amount)
        result = [self.build_most_dict(row) for row in warehouse_list]
        return jsonify(Warehouses=result)

    def get_most_city_transactions(self, amount=3):
        dao = WarehouseDAO()
        city_list = dao.get_most_city_transactions(amount)
        result = [dict(zip(['city','count'], row)) for row in city_list]
        return jsonify(Citites=result)

    def get_warehouse_profit(self, wid, json):
        dao = WarehouseDAO()
        if not dao.get_warehouse_by_id(wid):
            return jsonify(Error='Warehouse not found'), 404
        uid = json.get('User_id', None)
        user_warehouse_tuple = UserDAO().getUserWarehouse(uid)
        if not user_warehouse_tuple:
            return jsonify(Error='User not found'), 404
        if user_warehouse_tuple[0] != wid:
            return jsonify(Error='User has no access to warehouse.'), 403
        profits = dao.get_warehouse_profit(wid)
        result = [dict(zip(['year','profit'], row)) for row in profits]
        return jsonify(Profits=result)

    def insert_warehouse(self, json):
        wname = json.get('wname', None)
        wcity = json.get('wcity', None)
        wemail = json.get('wemail',None)
        wphone = json.get('wphone', None)
        budget = json.get('budget', None)
        if wname and wcity and wemail and wphone and budget and isinstance(budget, int) and budget > 0:
            dao = WarehouseDAO()
            wid = dao.insert(wname, wcity, wemail, wphone, budget, )
            result = self.build_warehouse_attributes(wid, wname, wcity,
                                                     wemail, wphone, budget)
            return jsonify(Warehouse=result), 201
        return jsonify(Error="Unexpected/Missing attributes in request."), 400

    def update_warehouse(self, wid, form):
        KEYS_LENGTH = 5
        dao = WarehouseDAO()
        if not dao.get_warehouse_by_id(wid):
            return jsonify(Error='Warehouse not found'), 404
        if len(form) != KEYS_LENGTH:
            return jsonify(Error=f'Malformed data: got {len(form)}'), 400
        wname = form.get('wname', None)
        wcity = form.get('wcity', None)
        wemail = form.get('wemail',None)
        wphone = form.get('wphone', None)
        budget = form.get('budget', None)

        #Assuming if other fields weren't set it was on purpose
        if wname and wcity and wemail and wphone and isinstance(budget, int) and budget>=0:
            dao.update(wid, wname, wcity, wemail, wphone, budget)
            result = self.build_warehouse_attributes(wid,
                                                wname,
                                                wcity,
                                                wemail,
                                                wphone,
                                                budget
                                                )
            return jsonify(Warehouse=result), 200
        return jsonify(Error='Attributes were not set properly'), 400

    def delete_warehouse(self, wid):
        dao = WarehouseDAO()
        if not dao.get_warehouse_by_id(wid):
            return jsonify(Error="Warehouse not found"), 404
        response = dao.delete(wid)
        if response == -1:
            return jsonify(Error=f"Warehouse {wid} is treated as foreign key elsewhere; cannot be deleted."), 400
        return jsonify(DeletedStatus='OK',row=response), 200

    def get_warehouse_parts(self, wid, json):
        
        ware_dao = WarehouseDAO()
        warehouse = ware_dao.get_warehouse_by_id(wid)
        
        if not warehouse:
            return jsonify(Error="Warehouse not found"), 404
        uid = json.get('User_id', None)
        user_warehouse_tuple = UserDAO().getUserWarehouse(uid)
        if not user_warehouse_tuple:
            return jsonify(Error='User not found'), 404
        if user_warehouse_tuple[0] != wid:
            return jsonify(Error='User has no access to warehouse.'), 403

        rack_dao = RackDAO()
        parts = rack_dao.get_parts_in_warehouse(wid)
        keys = ['ptype', 'pname', 'pid']
        result = [dict(zip(keys,row)) for row in parts]
        return jsonify(Parts_in_warehouse=result), 201



