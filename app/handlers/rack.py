from flask import jsonify
from app.handlers.warehouse import WarehouseHandler
from app.dao.rack import RackDAO
from app.dao.warehouse import WarehouseDAO
from app.dao.parts import PartsDAO
from app.dao.user import UserDAO


class RackHandler:
    def build_rack_dict(self, rows):
        keys = ['rid', 'capacity', 'wid', 'quantity', 'pid']
        return dict(zip(keys, rows))

    def build_rack_attributes(self, rid, capacity, quantity, pid, wid):
        return {
            'rid': rid,
            'capacity': capacity,
            'quantity': quantity,
            'pid': pid,
            'wid': wid
        }

    def build_bottom_material(self, rows):
        keys = ['ptype', 'count']
        return dict(zip(keys, rows))

    def get_all_racks(self):
        dao = RackDAO()
        rack_list = dao.get_all_racks()
        if rack_list:
            result = [self.build_rack_dict(row) for row in rack_list]
            return jsonify(Racks=result)
        else:
            return jsonify("No racks found."), 404

    def get_rack_by_id(self, rid):
        dao = RackDAO()
        row = dao.get_rack_by_id(rid)
        if not row:
            return jsonify(Error="Rack not found"), 404
        else:
            row = row[0]
            rack = self.build_rack_dict(row)
            return jsonify(Rack=rack)

    def get_warehouse_rack_lowstock(self, wid, json, amount=5):
        dao = RackDAO()
        if not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Warehouse not found'), 404
        uid = json.get('User_id', None)
        user_warehouse_tuple = UserDAO().getUserWarehouse(uid)
        if not user_warehouse_tuple:
            return jsonify(Error='User not found'), 404
        if user_warehouse_tuple[0] != wid:
            return jsonify(Error='User has no access to warehouse.'), 403
        rack_list = dao.get_warehouse_racks_lowstock(wid, amount)
        result = [self.build_rack_dict(row) for row in rack_list]
        return jsonify(Racks=result)

    def get_most_expensive_racks(self, wid, json, amount=5):
        dao = RackDAO()
        if not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Warehouse not found'), 404
        uid = json.get('User_id', None)
        user_warehouse_tuple = UserDAO().getUserWarehouse(uid)
        if not user_warehouse_tuple:
            return jsonify(Error='User not found'), 404
        if user_warehouse_tuple[0] != wid:
            return jsonify(Error='User has no access to warehouse.'), 403
        rack_list = dao.get_most_expensive_racks(wid)
        result = [{"rid":row[0], "total_price":row[1]} for row in rack_list]
        return jsonify(Racks=result)

    def get_warehouse_rack_bottom_material(self, wid, json, amount=3):
        dao = RackDAO()
        if not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Warehouse not found'), 404
        uid = json.get('User_id', None)
        user_warehouse_tuple = UserDAO().getUserWarehouse(uid)
        if not user_warehouse_tuple:
            return jsonify(Error='User not found'), 404
        if user_warehouse_tuple[0] != wid:
            return jsonify(Error='User has no access to warehouse'), 403
        rack_list = dao.get_warehouse_rack_bottom_material(wid, amount)
        result = [self.build_bottom_material(row) for row in rack_list]
        return jsonify(Racks=result)

    def insert_rack(self, json):
        capacity = json.get('capacity', None)
        wid = json.get('wid', None)
        quantity = json.get('quantity', None)
        pid = json.get('pid', None)

        if not wid:
            return jsonify('Warehouse ID not provided'), 400
        if not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Provided warehouse ID not found.'), 404
        if not pid:
            return jsonify(Error='Part ID not provided.'), 400
        if not PartsDAO().getPartById(pid):
            return jsonify(Error='Part does not exist'), 404
        # note: isinstance() already handles None values
        if not isinstance(capacity, int) or capacity <= 0:
            return jsonify(Error='Rack capacity invalid.'), 400
        if not isinstance(quantity, int) or quantity > capacity or quantity < 0:
            return jsonify(Error="Rack quantity invalid."), 400
        
        dao = RackDAO()
        in_warehouse = dao.rack_in_warehouse_validation(wid, pid)
        if in_warehouse:
            return jsonify(Error=f"A Rack with part {pid} is already in Warehouse {wid}."), 400
        
        rid = dao.insert(capacity, quantity, pid, wid)
        result = self.build_rack_attributes(rid, capacity, quantity, pid, wid)
        return jsonify(Rack=result), 201


    # Assume that if quantity field is not set, user meant for it to be 0
    def update_rack(self, rid, json):
        KEYS_LENGTH = 4
        dao = RackDAO()
        if not dao.get_rack_by_id(rid):
            return jsonify(Error='Rack not found'), 404

        if len(json) != KEYS_LENGTH:
            return jsonify(Error=f'Malformed data: got {len(json)}'), 400
        
        capacity = json.get('capacity', None)
        wid = json.get('wid', None)
        quantity = json.get('quantity', None)
        pid = json.get('pid', None)

        if not isinstance(wid, int) or not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Provided warehouse ID not found.'), 400

        if RackDAO().get_rack_warehouse(rid)[0] != wid:
            return jsonify(f"Rack does not exist in warehouse id: {wid}"), 400

        if not isinstance(pid, int):
            return jsonify(Error='Part ID not provided.'), 400

        if not PartsDAO().getPartById(pid):
            return jsonify(Error='Part does not exist'), 404
        
        if RackDAO().get_rack_part(rid)[0] != pid:
            return jsonify(f"Rack does not hold part id {pid}"), 400

        if not isinstance(capacity, int) or capacity <= 0:
            return jsonify(Error='Rack capacity invalid.'), 400

        if not isinstance(quantity, int) or quantity > capacity or quantity < 0:
            return jsonify(Error="Rack quantity invalid."), 400

        flag = dao.update(rid, capacity, quantity, pid, wid)
        if not flag:
            return jsonify(Error="Update could not be completed."), 400

        result = self.build_rack_attributes(rid, capacity, quantity, pid, wid)
        return jsonify(Rack=result)


    def delete_rack(self, rid):
        dao = RackDAO()
        if not dao.get_rack_by_id(rid):
            return jsonify(Error="Rack not found"), 404
        if len(dao.get_parts_in_rack(rid)) == 0:
            return jsonify(Error="Cannot delete non empty rack")
        response = dao.delete(rid)
        if response == -1:
            return jsonify(Error=f"Rack {rid} cannot be deleted because it is still referenced in transaction."), 400
        elif response:
            return jsonify(DeletedStatus='OK', row=response), 200
