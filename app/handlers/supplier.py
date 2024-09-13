from unittest import result
from flask import jsonify
from app.dao.supplier import SupplierDAO
from app.dao.parts import PartsDAO
from app.dao.warehouse import WarehouseDAO
from app.dao.user import UserDAO


class SupplierHandler:
    # -----Helper methods-----
    def build_part_dict(self, row):
        result = {}
        result['pid'] = row[0]
        result['pprice'] = row[1]
        result['ptype'] = row[2]
        result['pname'] = row[3]
        return result

    def build_most_dict(self, rows):
        keys = ['sid', 'count']
        return dict(zip(keys, rows))

    def build_supplier_attributes(self, sid, sname, scity, sphone, semail):
        return {
            'sid': sid,
            'sname': sname,
            'scity': scity,
            'semail': semail,
            'sphone': sphone
        }

    def build_supplier_dict(self, rows):
        keys = ['sid', 'scity', 'sname', 'sphone', 'semail']
        return dict(zip(keys, rows))

    def build_supplies_attributes(self, supid, stock, sid, pid):
        return {
            'supid': supid,
            'stock': stock,
            'sid': sid,
            'pid': pid,
        }

    # -----Helper methods END-----

    # works!, if more attributes are added, add them in ORDER to the keys array in build_supplier_dict
    def get_all_suppliers(self):
        dao = SupplierDAO()
        all_suppliers = dao.get_all_suppliers()
        result = []

        for row in all_suppliers:
            result.append(self.build_supplier_dict(row))
        return jsonify(Suppliers=result)

    # works!, if more attributes are added, add them in ORDER to the keys array in build_supplier_attributes
    def insert_supplier(self, json):  # works
        KEYS_LENGTH = 4
        if len(json) == KEYS_LENGTH:
            sname = json.get('sname', None)
            scity = json.get('scity', None)
            sphone = json.get('sphone', None)
            semail = json.get('semail', None)
            # Check every info is being sent by json
            if sname and scity and sphone and semail:
                dao = SupplierDAO()
                sid = dao.insert(sname, scity, sphone, semail)
                result = self.build_supplier_attributes(sid, sname, scity, sphone, semail)
                return jsonify(Supplier=result), 201
        return jsonify(Error="Unexpected/Missing attributes in request."), 400

    # works!
    def get_supplier_by_id(self, sid):
        dao = SupplierDAO()
        row = dao.get_supplier_by_ID(sid)
        if not row:
            return jsonify(Error="Supplier not found"), 404
        else:
            supplier = self.build_supplier_dict(row[0])  # note: get_supplier_by_ID returns a list of rows
            print(row)
            print(supplier)
            return jsonify(Supplier=supplier)

    # works!
    def update_supplier(self, sid, json):
        KEYS_LENGTH = 4  # keep this updated with the number of attributes that are allowed to be edited
        dao = SupplierDAO()
        if not dao.get_supplier_by_ID(sid):
            return jsonify(Error='Supplier not found'), 404
        if len(json) != KEYS_LENGTH:
            return jsonify(Error=f'Malformed data: got {len(json)}'), 400
        sname = json.get('sname', None)
        scity = json.get('scity', None)
        semail = json.get('semail', None)
        sphone = json.get('sphone', None)

        if not isinstance(sname,str): return jsonify("sname missing or not valid"), 400
        if not isinstance(scity,str): return jsonify("scity missing or not valid"), 400
        if not isinstance(semail,str): return jsonify("semail missing or not valid"), 400
        if not isinstance(sphone,str): return jsonify("sphone missing or not valid"), 400
                           
        if sname and scity and semail and sphone:
            dao.update(sid, scity, sname, sphone, semail)
            result = self.build_supplier_attributes(sid, sname, scity, sphone, semail)
            return jsonify(Supplier=result), 200
        return jsonify(Error='Attributes were not set properly'), 400

    # works!
    def delete_supplier(self, sid):
        dao = SupplierDAO()
        response = dao.delete(sid)
        if response == -1:
            return jsonify(Error=f"Supplier {sid} cannot be deleted because it is still referenced in transaction or supplies."), 400
        elif response:
            return jsonify(DeletedStatus='OK', row=response), 200
        else:
            return jsonify(Error="Supplier not found"), 404

    # unused
    # #works!
    # def get_supplier_by_name(self, sname):
    #     dao = SupplierDAO()
    #     supplier_by_city = dao.get_supplier_by_name(sname)
    #     if not supplier_by_city:
    #         return jsonify(Error = "No suppliers with that name"), 404
    #     result = []
    #     for row in supplier_by_city:
    #         result.append(self.build_supplier_dict(row))
    #     return jsonify(SuppliersByName=result)

    # #works!
    # def get_supplier_by_city(self, scity):
    #     dao = SupplierDAO()
    #     supplier_by_city = dao.get_supplier_by_city(scity)
    #     if not supplier_by_city:
    #         return jsonify(Error = "No suppliers in that city"), 404
    #     result = []
    #     for row in supplier_by_city:
    #         result.append(self.build_supplier_dict(row))
    #     return jsonify(SuppliersByCity=result)

    # get all supplied parts
    def get_supplied_parts(self, sid):
        dao = SupplierDAO()
        if not sid or not dao.get_supplier_by_ID(sid): return jsonify(Error='Supplier not found'), 404
        parts = dao.get_supplied_parts_by_sid(sid)
        result = []
        for row in parts:
            part_dict = self.build_part_dict(row)
            result.append(part_dict)

        return jsonify(Parts=result)

    # associate a part with a supplier
    def supply_part(self, sid, json):
        if len(json) != 2: return jsonify(Error="Malformed post request"), 400
        stock = json["stock"]
        pid = json["pid"]
        dao = SupplierDAO()
        parts_dao = PartsDAO()

        if not isinstance(sid,int) or not dao.get_supplier_by_ID(sid): return jsonify(Error='Supplier not found'), 404 #404 because you get the sid from the url
        if not isinstance(pid, int) or not parts_dao.getPartById(pid): return jsonify(Error='Part not found'), 400
        if not isinstance(stock, int) or stock <= 0: return jsonify(
            Error='Malformed request, stock must be a postive integer'), 400
        if dao.get_supply_by_sid_and_pid(sid, pid): return jsonify(Error='Supplier already supplies the part'), 400

        supid = dao.supplyPart(stock, sid, pid)
        supplies_dict = self.build_supplies_attributes(supid, stock, sid, pid)
        return jsonify(Supplies=supplies_dict), 201

    # update supplier stock
    def update_supply_stock(self, sid, json):
        if len(json) != 2: return jsonify(Error="Malformed post request"), 400
        stock = json["stock"]
        pid = json["pid"]
        dao = SupplierDAO()
        parts_dao = PartsDAO()

        if not isinstance(sid, int) or not dao.get_supplier_by_ID(sid): return jsonify(Error='Supplier not found'), 404
        if not isinstance(pid, int) or not parts_dao.getPartById(pid): return jsonify(Error='Part not found'), 400
        if not isinstance(stock, int) or stock < 0: return jsonify(Error='Malformed request'), 400

        supid = dao.get_supply_by_sid_and_pid(sid, pid)
        if not supid: return jsonify(Error='Supplies not found'), 400
        dao.update_supply_stock_by_supid(supid, stock)
        supplies_dict = self.build_supplies_attributes(supid, stock, sid, pid)

        return jsonify(Supplies=supplies_dict)

    def get_top_suppliers_for_warehouse(self, wid, json, amount=3):
        dao = SupplierDAO()
        if not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Warehouse not found'), 404
        uid = json.get('User_id', None)
        user_warehouse_tuple = UserDAO().getUserWarehouse(uid)
        if not user_warehouse_tuple:
            return jsonify(Error='User not found'), 404
        if user_warehouse_tuple[0] != wid:
            return jsonify(Error='User has no access to warehouse.'), 403
        supplier_list = dao.get_top_suppliers_for_warehouse(wid, amount)
        # TODO check if right result
        result = [self.build_most_dict(row) for row in supplier_list]
        return jsonify(Suppliers=result)
