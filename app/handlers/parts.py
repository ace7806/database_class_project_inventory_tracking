from flask import jsonify
from app.dao.parts import PartsDAO


class PartHandler:
    def build_part_dict(self, row):
        result = {}
        result['pid'] = row[0]
        result['pprice'] = row[1]
        result['ptype'] = row[2]
        result['pname'] = row[3]
        return result

    def build_part_attributes(self, pid, pprice, ptype, pname):
        result = {}
        result['pid'] = pid
        result['pprice'] = pprice
        result['ptype'] = ptype
        result['pname'] = pname
        return result

    def getAllParts(self):
        dao = PartsDAO()
        parts_list = dao.getAllParts()
        result_list = []
        for row in parts_list:
            result = self.build_part_dict(row)
            result_list.append(result)
        return jsonify(Parts=result_list)

    def getPartById(self, pid):
        dao = PartsDAO()
        row = dao.getPartById(pid)
        if not row:
            return jsonify(Error="Part Not Found"), 404
        else:
            part = self.build_part_dict(row)
            return jsonify(Part=part)

    def searchParts(self, args):
        pprice = args.get("pprice")
        ptype = args.get("ptype")
        pname = args.get("pname")
        dao = PartsDAO()
        parts_list = []
        if (len(args) == 2) and pprice and ptype:
            parts_list = dao.getPartsByPriceAndType(pprice, ptype)
        elif (len(args) == 1) and pprice:
            parts_list = dao.getPartsByPrice(pprice)
        elif (len(args) == 1) and ptype:
            parts_list = dao.getPartsByType(ptype)
        elif (len(args) == 1) and pname:
            parts_list = dao.getPartsByName(pname)
        else:
            return jsonify(Error="Malformed query string"), 400

        result_list = []
        for row in parts_list:
            result = self.build_part_dict(row)
            result_list.append(result)
        return jsonify(Parts=result_list)

    def insert_part(self, json):
        pprice = json.get('pprice')
        pname = json.get('pname')
        ptype = json.get('ptype')
        if pprice is None:
            return jsonify(Error = 'Part price not provided.'), 400
        if pname is None or len(pname) == 0:
            return jsonify(Error = 'Part name not provided.'), 400
        if ptype is None or len(ptype) == 0:
            return jsonify(Error = 'Part type not provided.'), 400
        if len(pname) > 100 or len(ptype) > 100:
            return jsonify(Error = 'Part name/type too long.'), 400
        if not isinstance(pprice, (int,float)) and not pprice.isnumeric() or pprice <= 0:
            return jsonify(Error = 'Part price not valid.'), 400
        if not isinstance(ptype, str) or not ptype.isascii():
            return jsonify(Error = 'Part type not valid.'), 400
        if not isinstance(pname, str) or not ptype.isascii():
            return jsonify(Error = 'Part name not valid.'), 400
        dao = PartsDAO()
        pid = dao.insert(pprice, ptype, pname)
        result = self.build_part_attributes(pid, pprice, ptype, pname)
        return jsonify(Part=result), 201

    def deletePart(self, pid):
        dao = PartsDAO()
        result = dao.delete(pid)
        if result == -1:
            return jsonify(Error=f"Part {pid} cannot be deleted because it is still referenced elsewhere."), 400
        elif result:
            return jsonify(DeleteStatus="OK"), 200
        return jsonify(Error="Part not found."), 404

    def update_part(self, pid, json):
        #assume that part types/names can have numbers in them
        #something like red40
        dao = PartsDAO()
        if not dao.getPartById(pid):
            return jsonify(Error="Part not found."), 404
        pprice = json.get('pprice')
        pname = json.get('pname')
        ptype = json.get('ptype')
        if not pprice:
            return jsonify(Error = 'Part price not provided.'), 400
        if pname is None or len(pname) == 0:
            return jsonify(Error = 'Part name not provided.'), 400
        if ptype is None or len(ptype) == 0:
            return jsonify(Error = 'Part type not provided.'), 400
        if len(pname) > 100 or len(ptype) > 100:
            return jsonify(Error = 'Part name/type too long.'), 400
        if not isinstance(pprice, (int,float)) or pprice <=0:
            return jsonify(Error = 'Part price not valid.'), 400
        if not isinstance(ptype, str) or not ptype.isascii():
            return jsonify(Error = 'Part type not valid.'), 400
        if not isinstance(pname, str) or not ptype.isascii():
            return jsonify(Error = 'Part name not valid.'), 400
        dao.update(pid, pprice, ptype, pname)
        result = self.build_part_attributes(pid, pprice, ptype, pname)
        return jsonify(Part=result), 200
