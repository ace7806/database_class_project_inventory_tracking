from app import app
from app.handlers.supplier import SupplierHandler
from flask import Flask, jsonify, request

# Currently implemented: (CRUD OPERATIONS)
# create (insert) a new supplier
# Read supplier data by
#     1. getting all suppliers
#     2. getting suppliers by id
#     3. getting suppliers by name, or city (not in specs nor a statistic but still)
# update supplier data
# delete supplier by id

@app.route('/los-cangri/supplier', methods=['GET', 'POST'])
def getAllSuppliers():
    if request.method == "POST":
        print("REQUEST: ",request.json)
        return SupplierHandler().insert_supplier(request.json)
    return SupplierHandler().get_all_suppliers()

@app.route('/los-cangri/supplier/<int:sid>',
           methods=['GET','PUT','DELETE'])
def get_supplier_by_id(sid):
    if request.method == 'GET':
        return SupplierHandler().get_supplier_by_id(sid)
    elif request.method == 'PUT':
        return SupplierHandler().update_supplier(sid, request.json)
    elif request.method == 'DELETE':
        return SupplierHandler().delete_supplier(sid)
    else:
        return jsonify(Error = "Not implemented"), 501


@app.route('/los-cangri/supplier/<int:sid>/parts', methods=['GET','PUT','POST'])
def associate_supplier_with_part(sid):
    if request.method == 'GET':
        return SupplierHandler().get_supplied_parts(sid)
    elif request.method == 'POST':
        return SupplierHandler().supply_part(sid, request.json)
    elif request.method == 'PUT':
        return SupplierHandler().update_supply_stock(sid, request.json)
    else:
        return jsonify(Error = "Not implemented"), 501
#unused 
# @app.route('/supplier/<string:sname>')
# def get_supplier_by_name(sname):
#     if request.method == 'GET':
#         print(sname)
#         return SupplierHandler().get_supplier_by_name(str(sname))
#     else:
#         return jsonify(Error = "Not implemented"), 501
    
# @app.route('/supplier/<string:scity>')
# def get_supplier_by_city(scity):
#     if request.method == 'GET':
#         return SupplierHandler().get_supplier_by_city(str(scity))
#     else:
#         return jsonify(Error = "Not implemented"), 501
