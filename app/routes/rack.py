from app import app
from app.handlers.rack import RackHandler
from flask import jsonify, request


@app.route('/los-cangri/rack', methods=['GET', 'POST'])
def getAllRacks():
    if request.method == 'POST':
        print(request.json)
        return RackHandler().insert_rack(request.json)
    return RackHandler().get_all_racks()


@app.route('/los-cangri/rack/<int:rid>',
           methods=['GET', 'PUT', 'DELETE'])
def get_rack_by_id(rid):
    if request.method == 'GET':
        return RackHandler().get_rack_by_id(rid)
    elif request.method == 'PUT':
        return RackHandler().update_rack(rid, request.json)
    elif request.method == 'DELETE':
        return RackHandler().delete_rack(rid)
    else:
        return jsonify(Error="Not implemented"), 501
