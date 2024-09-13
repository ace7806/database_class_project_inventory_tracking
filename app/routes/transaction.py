from app import app
from app.handlers.transaction import TransactionHandler
from flask import Flask, jsonify, request
#this will contain all routes for all types of transactions ("incoming", "outgoing", "exchange")

#-----incoming_transaction-----
@app.route('/los-cangri/incoming', methods=['GET', 'POST'])
def getAllIncoming():
    if request.method == "POST":
        print("REQUEST: ",request.json)
        return TransactionHandler().insert_incoming(request.json)
    return TransactionHandler().get_all_incoming()

@app.route('/los-cangri/incoming/<int:incid>', methods=['GET','PUT','DELETE']) 
def get_incoming_by_id(incid):
    if request.method == 'GET':
        return TransactionHandler().get_incoming_by_id(incid)
    elif request.method == 'PUT':
        return TransactionHandler().update_incoming(incid, request.json)
    elif request.method == 'DELETE':
        return TransactionHandler().delete_incoming(incid)
    else:
        return jsonify(Error = "Not implemented"), 501
#-----end incoming_transaction-----

#-----outgoing_transaction-----
@app.route('/los-cangri/outgoing', methods=['GET', 'POST'])
def getAllOutgoing():
    if request.method == "POST":
        print("REQUEST: ",request.json)
        return TransactionHandler().insert_outgoing(request.json)
    return TransactionHandler().get_all_outgoing()

@app.route('/los-cangri/outgoing/<int:outid>', methods=['GET','PUT','DELETE']) 
def get_outgoing_by_id(outid):
    if request.method == 'GET':
        return TransactionHandler().get_outgoing_by_id(outid)
    elif request.method == 'PUT':
        return TransactionHandler().update_outgoing(outid, request.json)
    elif request.method == 'DELETE':
        return TransactionHandler().delete_outgoing(outid)
    else:
        return jsonify(Error = "Not implemented"), 501
#-----end outgoing_transaction-----

#-----transfer_transaction-----
@app.route('/los-cangri/exchange', methods=['GET', 'POST'])
def getAllExchange():
    if request.method == "POST":
        print("REQUEST: ",request.json)
        return TransactionHandler().insert_exchange(request.json)
    return TransactionHandler().get_all_exchange()

@app.route('/los-cangri/exchange/<int:tranid>', methods=['GET','PUT','DELETE']) 
def get_exchange_by_id(tranid):
    if request.method == 'GET':
        return TransactionHandler().get_exchange_by_id(tranid)
    elif request.method == 'PUT':
        return TransactionHandler().update_exchange(tranid, request.json)
    elif request.method == 'DELETE':
        return TransactionHandler().delete_exchange(tranid)
    else:
        return jsonify(Error = "Not implemented"), 501
#-----end incoming_transaction-----