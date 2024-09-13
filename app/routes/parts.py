from app import app
from app.handlers.parts import PartHandler
from flask import Flask, jsonify, request


@app.route('/lol/part', methods=['GET', 'POST'])
def getAllParts():
    if request.method == 'POST':
        print("REQUEST: ", request.json)
        return PartHandler().insert_part(request.json)
    else:
        if not request.args:
            return PartHandler().getAllParts()
        else:
            return PartHandler().searchParts(request.args)


@app.route('/los-cangri/part/<int:pid>', methods=['GET', 'PUT', 'DELETE'])
def getPartById(pid):
    if request.method == 'GET':
        return PartHandler().getPartById(pid)
    elif request.method == 'PUT':
        return PartHandler().update_part(pid, request.json)
    elif request.method == 'DELETE':
        return PartHandler().deletePart(pid)
    else:
        return jsonify(Error="Method not allowed."), 405
