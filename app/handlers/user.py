from flask import jsonify
from app.dao.user import UserDAO
from app.dao.warehouse import WarehouseDAO


# Leamsi working here
class UserHandler:

    def build_user_dict(self, row):
        result = {}
        result['uid'] = row[0]
        result['fname'] = row[1]
        result['lname'] = row[2]
        result['uemail'] = row[3]
        result['uphone'] = row[4]
        result['wid'] = row[5]
        return result

    def build_user_attributes(self, uid, fname, lname, uemail, uphone, wid):
        result = {}
        result['uid'] = uid
        result['fname'] = fname
        result['lname'] = lname
        result['uemail'] = uemail
        result['uphone'] = uphone
        result['wid'] = wid
        return result

    def getAllUsers(self):
        dao = UserDAO()
        user_list = dao.getAllUsers()
        result_list = []
        for row in user_list:
            result = self.build_user_dict(row)
            result_list.append(result)
        return jsonify(User=result_list)

    def getUserById(self, uid):
        dao = UserDAO()
        row = dao.getUserById(uid)
        if not row:
            return jsonify(Error="User Not Found"), 404
        else:
            user = self.build_user_dict(row)
            return jsonify(User=user)

    def searchUsers(self, args):
        fname = args.get("fname")
        lname = args.get("lname")
        uemail = args.get("uemail")
        uphone = args.get("uphone")

        dao = UserDAO()
        user_list = []
        if (len(args) == 2) and fname and lname:
            user_list = dao.getUserByFullName(fname, lname)
        elif (len(args) == 1) and fname:
            user_list = dao.getUserByFirstName(fname)
        elif (len(args) == 1) and lname:
            user_list = dao.getUserByLastName(lname)
        elif (len(args) == 1) and uemail:
            user_list = dao.getUserByEmail(uemail)
        elif (len(args) == 1) and uphone:
            user_list = dao.getUserByPhone(uphone)
        else:
            return jsonify(Error="Malformed query string"), 400

        result_list = []
        for row in user_list:
            result = self.build_user_dict(row)
            result_list.append(result)
        return jsonify(User=result_list)

    def insertUserJson(self, json):
        if len(json) != 5: return jsonify(Error="Malformed Post request"), 400
        fname = json['fname']
        lname = json['lname']
        uemail = json['uemail']
        uphone = json['uphone']
        wid = json['wid']
        warehouse_dao = WarehouseDAO()
        if not isinstance(wid,int) or not warehouse_dao.get_warehouse_by_id(wid):
            return jsonify(Error = 'Warehouse does not exist'), 400

        if fname and lname and uemail and uphone and wid:
            dao = UserDAO()
            uid = dao.insert(fname, lname, wid, uemail, uphone)
            result = self.build_user_attributes(uid, fname, lname, uemail, uphone, wid)
            return jsonify(User=result), 201
        else:
            return jsonify(Error="Unexpected attributes in post request"), 400

    def deleteUser(self, uid):
        dao = UserDAO()
        if not dao.getUserById(uid):
            return jsonify(Error="User not found."), 404
        else:
            dao.delete(uid)
            return jsonify(DeleteStatus="OK"), 200

    def updateUser(self, uid, json):
        dao = UserDAO()
        if not dao.getUserById(uid):
            return jsonify(Error="User not found."), 404
        else:
            print(len(json),json)
            if len(json) != 5:
                return jsonify(Error="Malformed update request"), 400
            else:
                fname = json['fname']
                lname = json['lname']
                uemail = json['uemail']
                uphone = json['uphone']
                wid = json['wid']
                warehouse_dao = WarehouseDAO()
                if not isinstance(wid, int) or not warehouse_dao.get_warehouse_by_id(wid):
                    return jsonify(Error = 'Warehouse does not exist'), 400
                if fname and lname and uemail and uphone and wid:
                    dao.update(uid, fname, lname, wid, uemail, uphone)
                    result = self.build_user_attributes(uid, fname, lname, uemail, uphone, wid)
                    return jsonify(User=result), 200
                else:
                    return jsonify(Error="Unexpected attributes in update request"), 400

    def getUserReceivesMost(self, wid, json, amount=3):
        dao = UserDAO()
        if not WarehouseDAO().get_warehouse_by_id(wid):
            return jsonify(Error='Warehouse not found'), 404
        uid = json.get('User_id', None)
        user_warehouse_tuple = UserDAO().getUserWarehouse(uid)
        if not user_warehouse_tuple:
            return jsonify(Error = 'User not found'), 404
        if user_warehouse_tuple[0] != wid:
            return jsonify(Error = 'User has no access to warehouse'), 403
        user_list = dao.getUserReceivesMost(wid, amount)
        result = [dict(zip(['uid','count'],row)) for row in user_list]
        return jsonify(Users=result)
    
    def getUsersWithMostTransactions(self, amount = 3):
        dao = UserDAO()
        user_list = dao.getUsersWithMostTransactions(amount)
        result = [dict(zip(['uid','count'],row)) for row in user_list]
        return jsonify(Users = result)


