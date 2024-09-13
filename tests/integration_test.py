import sys
from flask import Flask
import psycopg2
import pytest
sys.path.append("/root/projects/inventory-tracking-app-los-cangris") #replace with location of project
from app.config import dbconfig


#override dbconfig variables so that one ca hook up their local database
dbconfig.host = "localhost"
dbconfig.dbname = "testdb"
dbconfig.user = "postgres"
dbconfig.password = "postgres"
dbconfig.port = "5432"

base_url = '/los-cangri/'

# List of tables to truncate
tables_to_truncate = [
    'supplies', 'incomingt', 'outgoingt',
    'transaction', '"user"', 'supplier', 'rack', 'parts',
    'transfert', 'warehouse'
]

def reset_db():
    try:
        with psycopg2.connect(user=dbconfig.user, password=dbconfig.password, host=dbconfig.host, dbname=dbconfig.dbname, port=dbconfig.port) as conn:
            with conn.cursor() as cursor:
                for table in tables_to_truncate:
                    query = f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"
                    cursor.execute(query)
                    print(f"Truncated table {table}")
        return True
    except Exception as e:
        print(e)
        return False        

@pytest.fixture(scope="module")
def app():
    from app import app
    app.config.update({
        "TESTING": True,
    })
    
    reset_db() # start with a clean slate
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_server_running(client):
    response = client.get(base_url)
    assert b"lol" in response.data

def helper_test_posts(client, endpoint, post_data, expected_status, expected_response_structure):
    response = client.post(endpoint, json=post_data)
    assert response.status_code == expected_status, response.data

    if expected_status == 201:
        response_data = response.json
        for key, fields in expected_response_structure.items():
            #validate response structure
            assert key in response_data
            for field in fields:
                assert field in response_data[key]
                #validate data
                if field in post_data and field !='tdate':
                    assert response_data[key][field] == post_data[field]
        return True

def validate_updates(client, endpoint, update_data, expected_status, expected_response_structure):
    response = client.put(endpoint,json=update_data)
    assert response.status_code == expected_status, response.data

    if expected_status == 200:
        response_data = response.json
        for key, fields in expected_response_structure.items():
            #validate response structure
            assert key in response_data
            for field in fields:
                assert field in response_data[key]
                #validate data
                if field in update_data:
                    assert response_data[key][field] == update_data[field]
        return True

# @pytest.mark.order(0)
@pytest.mark.parametrize("data, status_code", [
    ({"pprice": 100.0, "ptype": "Steel", "pname": "Bolt"}, 201),  # Successful case
    ({"pprice": 1.0, "ptype": "wood", "pname": "stick"}, 201),  # Successful case
    ({"pprice": 4.0, "ptype": "memes", "pname": "lolazo"}, 201),  # Successful case
    ({"pprice": 100.0, "ptype": "yolo", "pname": "this part was created for a test in exchange"}, 201),  # Successful case
    ({"pprice": 100.0, "pname": "Bolt"}, 400),  # Missing 'ptype'
    ({"pprice": "100.0", "ptype": "Steel", "pname": "Bolt"}, 400),  # Incorrect data type
    ({"pprice": -50.0, "ptype": "Steel", "pname": "Bolt"}, 400),  # Invalid value
    ({"pprice": 0.0, "ptype": "Steel", "pname": "Bolt"}, 400)  # Invalid value
])
def test_post_parts(client, data, status_code):
    expected_structure = {"Part": ["pid", "pname", "pprice", "ptype"]}
    endpoint = base_url+'part'
    helper_test_posts(client,endpoint,data,status_code, expected_structure)

# @pytest.mark.order(0)
@pytest.mark.parametrize("data, status_code", [
    ({"wname":"Transaction_Warehouse", "wcity":"Aguada", "wemail":"db@test", "wphone":"787-0DB-TEST", "budget":500}, 201),  # Successful case
    ({"wname":"Big Balling Warehouse", "wcity":"San Juan", "wemail":"juan@test", "wphone":"787-1DB-TEST", "budget":100000}, 201),  # Successful case
    ({"wname":"Transaction_Warehouse", "wcity":"Aguada", "wemail":"db@test", "budget":500}, 400),  # missing 'wphone'
    ({"wname":"Transaction_Warehouse", "wcity":"Aguada", "wemail":"db@test", "wphone":"787-0DB-TEST", "budget":'500'}, 400),  # Incorrect data type
    ({"wname":"Transaction_Warehouse", "wcity":"Aguada", "wemail":"db@test", "wphone":"787-0DB-TEST", "budget":-500}, 400),  # Invalid value
    ({"wname":"Transaction_Warehouse", "wcity":"Aguada", "wemail":"db@test", "wphone":"787-0DB-TEST", "budget":0}, 400),  # Invalid value
    
])
def test_post_warehouse(client, data, status_code):
    expected_structure = {"Warehouse": ["wid", "wname", "wcity", "wemail", "wphone", "budget"]}
    endpoint = base_url+'warehouse'
    helper_test_posts(client,endpoint,data,status_code, expected_structure)

# @pytest.mark.order(1)
@pytest.mark.parametrize("data, status_code", [
    ({"pid":1, "pprice": 100.0, "ptype": "Steel", "pname": "Bolt"}, 200),  # Successful case
    ({"pid":99999, "pprice": 100.0, "ptype": "Steel", "pname": "Bolt"}, 404),  # Pid doesnt exist
])   
def test_get_part(client, data, status_code):
    response = client.get(base_url+f'part/{data["pid"]}')
    assert response.status_code == status_code

    if status_code==200:
        part_data = response.json.get("Part", {})
        assert part_data.get("pname") == data["pname"]
        assert part_data.get("pprice") == data["pprice"]
        assert part_data.get("ptype") == data["ptype"]
        assert part_data.get("pid") == data["pid"]

@pytest.mark.parametrize("rack_data, status_code", [
    ({"capacity": 100, "wid": 1, "quantity": 12, "pid": 1}, 201),  # Successful case
    ({"capacity": 100, "wid": 1, "quantity": 12, "pid": 1}, 400),  # rack already exists in warehouse
    ({"capacity": 0, "wid": 2, "quantity": 12, "pid": 1}, 400),  # Invalid capacity
    ({"capacity": -100, "wid": 2, "quantity": 12, "pid": 1}, 400),  # Invalid capacity
    ({"capacity": "100", "wid": 2, "quantity": 12, "pid": 1}, 400),  # Invalid capacity
    ({"capacity": 100, "quantity": 12, "pid": 1}, 400),  # Missing 'wid'
    ({"capacity": 100, "wid": 2, "quantity": 12}, 400),  # Missing 'pid'
    ({"capacity": 100, "wid": 2, "quantity": 5, "pid": 99}, 404),  # pid doesnt exist
    ({"capacity": 100, "wid": 99, "quantity": 5, "pid": 1}, 404),  # wid doesnt exist
    ({"capacity": 100, "wid": 2, "quantity": -5, "pid": 1}, 400),  # Invalid quantity
    ({"capacity": 100, "wid": 2, "quantity": "10", "pid": 1}, 400),  # Invalid quantity
    ({"capacity": 100, "wid": 2, "quantity": 1000, "pid": 1}, 400),  # Invalid quantity - capacity is smaller than qaunt
    ({"capacity": 100, "wid": 2, "quantity": 0, "pid": 1}, 201),  # Successful case
    ({"capacity": 100, "wid": 2, "quantity": 99, "pid": 2}, 201),  # Successful case
    ({"capacity": 15, "wid": 1, "quantity": 10, "pid": 3}, 201),  # Successful case
    ({"capacity": 15, "wid": 1, "quantity": 10, "pid": 4}, 201),  # Successful case
    ({"capacity": 15, "wid": 2, "quantity": 10, "pid": 4}, 201),  # Successful case
])
def test_post_rack(client, rack_data, status_code):
    endpoint = base_url+'rack'
    expected_structure = {"Rack": ["rid", "capacity", "quantity", "pid", "wid"]}
    helper_test_posts(client, endpoint, rack_data, status_code, expected_structure)

@pytest.mark.parametrize("data, status_code", [
    ({ "fname": "Cristian", "lname": "Seguinot", "uemail": "db@test", "uphone":"787-0DB-TEST", "wid": 1 }, 201),  # Successful case
    ({ "fname": "derp", "lname": "bot", "uemail": "db@upr.edu", "uphone":"1-800-plz-work", "wid": 1 }, 201),  # Successful case
    ({ "fname": "Chad", "lname": "derp", "uemail": "OS@upr.edu", "uphone":"1-800-ayuda", "wid": 2 }, 201),  # Successful case
    ({ "fname": "Cristian", "lname": "Seguinot", "uemail": "db@test", "uphone":"787-0DB-TEST", "wid": 99 }, 400),  # Invalid wid
    ({ "fname": "Cristian", "lname": "Seguinot", "uemail": "db@test", "uphone":"787-0DB-TEST", "wid": "1" }, 400),  # Invalid wid
    ({ "fname": "Cristian", "lname": "Seguinot", "uemail": "db@test", "uphone":"787-0DB-TEST"}, 400),  # Missing 'wid'
    ({ "fname": "Cristian", "lname": "Seguinot", "uphone":"787-0DB-TEST", "wid": 1 }, 400),  # Missing 'umail'
])
def test_post_user(client, data, status_code):
    endpoint = base_url+'user'
    expected_structure = {"User": ["uid", "fname", "lname", "uemail", "uphone", "wid"]}
    helper_test_posts(client, endpoint, data, status_code, expected_structure)

@pytest.mark.parametrize("data, status_code", [
    ({ "sname":"Berrios Imports", "scity":"Moca", "sphone":"787-0DB-TEST", "semail":"test@gmail.com" }, 201),  # Successful case
    ({ "sname":"Zalic", "scity":"trujillo", "sphone":"787-000-000", "semail":"12" }, 201),  # Successful case
    ({ "scity":"Moca", "sphone":"787-0DB-TEST", "semail":"test@gmail.com" }, 400),  # Missing 'sname'
    ({ "sname":"Berrios Imports", "scity":"Moca", "semail":"test@gmail.com" }, 400),  # Missing 'scity'
])
def test_post_suppliers(client, data, status_code):
    endpoint = base_url + 'supplier'
    expected_structure = {"Supplier": ["sid", "sname", "scity", "sphone", "semail"]}
    helper_test_posts(client, endpoint, data, status_code, expected_structure)

@pytest.mark.parametrize("sid, data, status_code", [
    (1, {"stock":10, "pid":1}, 201),  # Successful case
    (1, {"stock":100, "pid":1}, 400),  # Supplier already supplies part
    (1, {"stock":10, "pid":2}, 201),  # Successful case
    (2, {"stock":0, "pid":2}, 400),  # Invalid stock
    (2, {"stock":-10, "pid":2}, 400),  # Invalid stock
    (2, {"stock":10, "pid":99}, 400),  # pid doesnt exist therefore is invalid
    (2, {"stock":10, "pid":"2"}, 400),  # Invalid pid
    (2, {"stock":"10", "pid":2}, 400),  # Invalid stock
    (2, {"stock":10, "pid":2}, 201),  # Successful case
    (2, {"stock":10, "pid":1}, 201),  # Successful case
    (9, {"stock":10, "pid":1}, 404),  # sid doesnt exist therefore cant find supplier
])
def test_supply_parts(client, sid, data, status_code):
    endpoint = base_url + f'supplier/{sid}/parts'
    expected_structure = {"Supplies": ["supid", "pid", "sid", "stock"]}
    helper_test_posts(client, endpoint, data, status_code, expected_structure)


"""
how to test transactions
- do a post
- check post 
- check if enities were affected correctly
"""

@pytest.mark.parametrize("data, status_code", [
    ({"tquantity":2,"pid":1,"sid":1,"uid":1,"wid":1, "tdate":"2022-2-1"}, 201),  # Successful case
    # test warehouse budget
    ({"tquantity":3,"pid":1,"sid":1,"uid":1,"wid":1}, 201),  # Successful case, note: warehouse budget is now 0
    ({"tquantity":3,"pid":1,"sid":1,"uid":1,"wid":1}, 400),  # Warehouse doesnt have enough budget
    # test rack quantity
    ({"tquantity":1,"pid":2,"sid":2,"uid":3,"wid":2}, 201),  # Successful case, note: rack had qauntity at 99, and now is 100
    ({"tquantity":1,"pid":2,"sid":2,"uid":3,"wid":2}, 400),  # rack is too full, note: quantity is 100 and capacity caps at 100, therefore we couldnt add one more part
    # test stock
    ({"tquantity":5,"pid":1,"sid":1,"uid":3,"wid":2}, 201),  # Successful case, note: stock is now 0
    ({"tquantity":5,"pid":1,"sid":1,"uid":3,"wid":2}, 400),  # Not enough stock
    ({"tquantity":5,"pid":1,"sid":2,"uid":3,"wid":2}, 201),  #Succesful case testing another supplier
    ({"tquantity":1,"pid":3,"sid":2,"uid":1,"wid":1}, 400),  # supplier does not supply pid 3
    # test entity relationships
    ({"tquantity":1,"pid":3,"sid":2,"uid":3,"wid":2}, 400),  # warehouse doesnt have a rack for pid 3
    ({"tquantity":1,"pid":1,"sid":2,"uid":2,"wid":2}, 400),  # User does not work in warehouse
    ({"tquantity":1,"pid":1,"sid":2,"uid":3,"wid":1}, 400),  # Wrong Warehouse 
    ({"tquantity":1,"pid":1,"sid":99,"uid":3,"wid":2}, 400),  # Invalid supplier
    ({"pid":1,"sid":2,"uid":3,"wid":2}, 400),  # Missing tquantity
    ({"tquantity":1,"pid":1,"sid":2,"uid":3,"wid":"2"}, 400),  # Invalid wid
    ({"tquantity":1,"pid":1,"sid":"2","uid":3,"wid":2}, 400),  # Invalid sid
    ({"tquantity":"1","pid":1,"sid":2,"uid":3,"wid":2}, 400),  # Invalid tqauntity
    ({"tquantity":-1,"pid":1,"sid":2,"uid":3,"wid":2}, 400),  # Invalid tqauntity
    ({"tquantity":1,"pid":1,"sid":2,"uid":3,"wid":2}, 201),  # Successful case

])
def test_post_inncoming_transaction(client, data, status_code):
    from app.dao import parts, rack, warehouse, supplier
    pid = data.get('pid',None)
    wid =  data.get('wid',None)
    sid =  data.get('sid',None)
    
    rid =  rack.RackDAO().get_rid_from_wid_and_pid(wid,pid)
    pprice = parts.PartsDAO().get_part_price(pid)
    budget = warehouse.WarehouseDAO().get_warehouse_budget(wid)
    rack_quant = rack.RackDAO().get_rack_quantity(rid)
    stock = supplier.SupplierDAO().get_supplier_supplies_stock_by_sid_and_pid(sid,pid)

    endpoint = base_url + 'incoming'
    expected_structure = {"Incoming": ["incid", "tdate", "tquantity", "uid", "wid", "pid", "sid", "tid"]}
    if not helper_test_posts(client, endpoint, data, status_code, expected_structure): 
        return
    tquant = data['tquantity']
    assert warehouse.WarehouseDAO().get_warehouse_budget(wid) == budget - pprice*tquant
    assert rack.RackDAO().get_rack_quantity(rid) == rack_quant+tquant
    assert supplier.SupplierDAO().get_supplier_supplies_stock_by_sid_and_pid(sid,pid) == stock - tquant


@pytest.mark.parametrize("data, status_code", [
    # testing parts in rack
    ({"tquantity":17,"obuyer":"Test","pid":1,"uid":1,"wid":1,"tdate":"2023-2-1"}, 201),  # Successful case
    ({"tquantity":1,"obuyer":"Test","pid":1,"uid":1,"wid":1}, 400),  # not enough parts in rack
    # testing relationships
    ({"tquantity":1,"obuyer":"Test","pid":2,"uid":1,"wid":1}, 400),  # warehouse does not have a rack with pid 2
    ({"tquantity":1,"obuyer":"Test","pid":3,"uid":2,"wid":2}, 400),  # invalid user/warehouse
    ({"tquantity":1,"obuyer":"Test","pid":3,"uid":3,"wid":1}, 400),  # invalid warehouse/warehouse
    ({"tquantity":1,"obuyer":"Test","pid":3,"uid":1,"wid":1}, 201),  # Succesful case
    ({"tquantity":1,"obuyer":"Test","pid":"3","uid":1,"wid":1}, 400),  # Invalid pid 
    ({"tquantity":1,"obuyer":"Test","pid":3,"uid":"1","wid":1}, 400),  # Invalid uid 
    ({"tquantity":1,"obuyer":"Test","pid":3,"uid":99,"wid":1}, 400),  # uid doesnt exist 
    ({"tquantity":1,"obuyer":"Test","pid":3,"uid":1,"wid":99}, 400),  # wid doesnt exist 
    ({"tquantity":1,"obuyer":"Test","pid":99,"uid":1,"wid":1}, 400),  # pid doesnt exist 
    ({"tquantity":-1,"obuyer":"Test","pid":3,"uid":1,"wid":1}, 400),  # Invalid quantity 
    ({"tquantity":"1","obuyer":"Test","pid":1,"uid":3,"wid":2}, 400),  # invalid quantity
    ({"tquantity":1,"pid":1,"uid":3,"wid":2}, 400),  # Missing obuyer
    ({"tquantity":1,"obuyer":"Test","pid":1,"uid":3,"wid":2}, 201),  # Succesful case

])
def test_post_outgoing_transaction(client, data, status_code):
    from app.dao import parts, rack, warehouse, supplier
    pid = data.get('pid',None)
    wid = data.get('wid',None)
    rid = rack.RackDAO().get_rid_from_wid_and_pid(wid,pid)
    profit_yield = 1.10
    
    pprice = parts.PartsDAO().get_part_price(pid)
    budget = warehouse.WarehouseDAO().get_warehouse_budget(wid)
    rack_quant = rack.RackDAO().get_rack_quantity(rid)

    endpoint = base_url + 'outgoing'
    expected_structure = {"Outgoing": ["outid", "tdate", "tquantity", "uid", "wid", "pid", "tid", "obuyer"]}
    if not helper_test_posts(client, endpoint, data, status_code, expected_structure): 
        return
    tquant = data.get('tquantity')
    
    assert warehouse.WarehouseDAO().get_warehouse_budget(wid) == (budget + pprice*tquant*profit_yield)
    assert rack.RackDAO().get_rack_quantity(rid) == rack_quant-tquant
    assert rack.RackDAO().get_rack_quantity(rid) >=0



@pytest.mark.parametrize("data, status_code", [
    # testing parts in rack
    ({"tquantity":10,"pid":1, "sending_wid":2, "receiving_wid":1, "sending_uid":3,"receiving_uid":1, "tdate":"2023-2-1"}, 201),  # Successful case
    ({"tquantity":10,"pid":1, "sending_wid":2, "receiving_wid":1, "sending_uid":3,"receiving_uid":1}, 400),  # warehouse 2 does not have enough parts to send pid 1
    ({"tquantity":5,"pid":1, "sending_wid":1, "receiving_wid":2, "sending_uid":1,"receiving_uid":3}, 201),  #  Successful case
    ({"tquantity":5,"pid":1, "sending_wid":1, "receiving_wid":2, "sending_uid":1,"receiving_uid":2}, 400),  # user 2 does not work in warehouse 2
    ({"tquantity":5,"pid":1, "sending_wid":1, "receiving_wid":2, "sending_uid":3,"receiving_uid":3}, 400),  # user 3 does not work in warehouse 1 and uids' are the same
    ({"tquantity":1,"pid":1, "sending_wid":1, "receiving_wid":1, "sending_uid":1,"receiving_uid":2}, 400),  # transfering to the same warehouse is redundant
    ({"tquantity":1,"pid":2, "sending_wid":2, "receiving_wid":1, "sending_uid":3,"receiving_uid":1}, 400),  # warehouse 1 doesnt have a rack with pid 2
    ({"tquantity":1,"pid":3, "sending_wid":2, "receiving_wid":1, "sending_uid":3,"receiving_uid":1}, 400),  # neither warehouse has pid 3
    ({"tquantity":1,"pid":4, "sending_wid":1, "receiving_wid":2, "sending_uid":1,"receiving_uid":3}, 201),  # neither warehouse has pid 3
    ({"tquantity":6,"pid":4, "sending_wid":1, "receiving_wid":2, "sending_uid":1,"receiving_uid":3}, 400),  # warehouse 2 has too many of pid 4
    ({"tquantity":-1,"pid":1, "sending_wid":1, "receiving_wid":2, "sending_uid":1,"receiving_uid":3}, 400),  # Invalid tquantity
    ({"tquantity":"1","pid":1, "sending_wid":1, "receiving_wid":2, "sending_uid":1,"receiving_uid":3}, 400),  # Invalid tquantity
    ({"tquantity":0,"pid":1, "sending_wid":1, "receiving_wid":2, "sending_uid":1,"receiving_uid":3}, 400),  # Invalid tquantity
    ({"tquantity":1,"pid":1, "sending_wid":1, "receiving_wid":2, "sending_uid":1,"receiving_uid":99}, 400),  # receiving uid does not exist
    ({"tquantity":1,"pid":1, "sending_wid":1, "receiving_wid":99, "sending_uid":1,"receiving_uid":3}, 400),  # receiving wid does not exist
    ({"tquantity":1,"pid":1, "sending_wid":99, "receiving_wid":1, "sending_uid":1,"receiving_uid":3}, 400),  # sending wid does not exist
    ({"tquantity":1,"pid":1, "sending_wid":1, "receiving_wid":1, "sending_uid":99,"receiving_uid":3}, 400),  # sending uid does not exist
])
def test_post_exchange_transaction(client, data, status_code):
    from app.dao import parts, rack, warehouse, supplier
    pid = data.get('pid',None)
    sending_wid = data.get('sending_wid',None)
    receiving_wid = data.get('receiving_wid',None)

    sending_rid = rack.RackDAO().get_rid_from_wid_and_pid(sending_wid,pid)
    receiving_rid = rack.RackDAO().get_rid_from_wid_and_pid(receiving_wid,pid)
    receiving_rack_quant = rack.RackDAO().get_rack_quantity(receiving_rid)
    sending_rack_quant = rack.RackDAO().get_rack_quantity(sending_rid)

    endpoint = base_url + 'exchange'
    expected_structure = {"exchange": [ "tid", "tranid", 'taction', "tdate", "tquantity", "uid", "wid", "pid"]}
    
    response = client.post(endpoint, json = data)
    assert response.status_code == status_code, response.data

    if status_code!=201: return 
    response_data = response.json
    for key, fields in expected_structure.items():
        assert key in response_data
        for item in response_data[key]:
            for field in fields:
                assert field in item
                
                if field in data and field!='tdate':
                    assert item[field] == data[field]


    tquant = data.get('tquantity')
    assert rack.RackDAO().get_rack_quantity(sending_rid) == sending_rack_quant-tquant
    assert rack.RackDAO().get_rack_quantity(sending_rid) >=0

    assert rack.RackDAO().get_rack_quantity(receiving_rid) == receiving_rack_quant+tquant
    assert rack.RackDAO().get_rack_quantity(receiving_rid) <= rack.RackDAO().get_rack_capacity(receiving_rid)

# # @pytest.mark.parametrize("pid, data, status_code", [
# #     # testing parts in rack
# #     (1, {"pprice":111, "ptype":"semi-conductor", "pname":"amd cpu ryzen flop"}, 200),  # Successful case
# #     (1, {"pprice":0, "ptype":"semi-conductor", "pname":"amd cpu ryzen flop"}, 400),  # Invalid pprice
# #     (1, {"pprice":-50, "ptype":"semi-conductor", "pname":"amd cpu ryzen flop"}, 400),  # Invalid pprice
# #     (1, {"pprice":"50", "ptype":"semi-conductor", "pname":"amd cpu ryzen flop"}, 400),  # Invalid pprice
# #     (1, {"pprice":50, "ptype":"", "pname":"amd cpu ryzen flop"}, 400),  # invalid ptype
# # ])    
# # def test_update_part(client, pid, data, status_code):
# #     expected_structure = {"Part": ["pid", "pname", "pprice", "ptype"]}
# #     endpoint = base_url+f'part/{pid}'
# #     validate_updates(client, endpoint,data,status_code, expected_structure)


# # @pytest.mark.parametrize("sid, data, status_code", [
# #     # testing parts in rack
# #     (1,{"sname": "Sebastian-EDITED-AGAIN", "scity": "Moca-EDITED", "sphone": "787-0DB-TEST-EDITED", "semail":"db@gmail.com"}, 200),  # Successful case
# #     (1,{"sname": "Sebastian-EDITED-AGAIN", "scity": "Moca-EDITED", "sphone": "", "semail":"db@gmail.com"}, 400),  # sphone is empty
# #     (1,{ "scity": "Moca-EDITED", "sphone": "787-0DB-TEST-EDITED", "semail":"db@gmail.com"}, 400),  # Missing sname
# # ])    
# # def test_update_supplier(client, sid, data, status_code):
# #     expected_structure = {"Supplier": ["sid", "sname", "scity", "sphone", "semail"]}
# #     endpoint = base_url+f'supplier/{sid}'
# #     validate_updates(client, endpoint,data,status_code, expected_structure)

# # @pytest.mark.parametrize("sid, data, status_code", [
# #     # testing parts in rack
# #     (1, {"stock":10, "pid":1}, 200),  # Successful case
# #     (2, {"stock":1000, "pid":2}, 200),  # Successful case
# #     (2, {"stock":0, "pid":1}, 200),  # Successful case
# #     (2, {"stock":-1, "pid":1}, 400),  # Invalid stock
# #     (2, {"stock":"1", "pid":99}, 400),  # pid doesnt exist
# #     (2, {"stock":1, "pid":"99"}, 400),  # Invalid pid
# #     (2, {"pid":"99"}, 400),  # Missing stock
# #     (2, {"stock":1, "pid":99}, 400),  # pid doesnt exist
# #     (99, {"stock":1, "pid":99}, 404),  # sid doesnt exist
# #     (1, {"stock":1, "pid":3}, 400),  # supplier 1 doesnt supply pid 3
# # ])  
# # def test_update_supply(client, sid, data, status_code):
# #     expected_structure = {"Supplies": ["supid", "pid", "sid", "stock"]}
# #     endpoint = base_url+f'supplier/{sid}/parts'
# #     validate_updates(client, endpoint,data,status_code, expected_structure)

# # @pytest.mark.parametrize("uid, data, status_code", [
# #     # testing parts in rack
# #     (1,{"fname": "u Cristian", "lname": "u Seguinot", "uemail": "@test.com", "uphone":"787-updated", "wid": 2}, 200),  # Successful case
# #     (1,{"fname": "Cristian", "lname": "Seguinot", "uemail": "db@test", "uphone":"787-0DB-TEST", "wid": "1"}, 400),  # invalid wid
# #     (1,{"fname": "Cristian", "lname": "Seguinot", "uemail": "db@test", "uphone":"787-0DB-TEST", "wid": 99}, 400),  # warehouse doesnt exist
# #     (1,{"fname": "Cristian", "lname": "Seguinot", "uemail": "db@test", "uphone":"787-0DB-TEST"}, 400),  # missing wid
# #     (1,{"fname": "Cristian", "lname": "Seguinot", "uemail": "db@test", "wid": 2}, 400),  # missing uphones
# #     (1,{"fname": "Cristian", "lname": "", "uemail": "db@test", "uphone":"787-0DB-TEST", "wid": 2}, 400),  # invalid lname
# #     (9,{"fname": "Cristian", "lname": "bop", "uemail": "db@test", "uphone":"787-0DB-TEST", "wid": 2}, 404),  # user doesnt exist
# # ])  
# # def test_update_user(client, uid, data, status_code):
# #     endpoint = base_url+f'user/{uid}'
# #     expected_structure = {"User": ["uid", "fname", "lname", "uemail", "uphone", "wid"]}
# #     validate_updates(client, endpoint,data,status_code, expected_structure)

# # @pytest.mark.parametrize("wid, data, status_code", [
# #     # testing parts in rack
# #     (1,{"wname":"updated_Warehouse", "wcity":"updated Aguada", "wemail":"db@update-test", "wphone":"787-updated", "budget":0}, 200),  # Successful case
# #     (1,{"wname":"updated_Warehouse", "wcity":"updated Aguada", "wemail":"db@update-test", "wphone":"787-updated", "budget":-2}, 400),  # Invalid budget
# #     (1,{"wname":"updated_Warehouse", "wcity":"updated Aguada", "wemail":"db@update-test", "wphone":"787-updated", "budget":"2"}, 400),  # Invalid budget
# #     (1,{"wname":"updated_Warehouse", "wcity":"updated Aguada", "wemail":"db@update-test", "wphone":"787-updated"}, 400),  # missing budget
# #     (1,{"wname":"updated_Warehouse", "wcity":"updated Aguada", "wemail":"db@update-test", "budget":0}, 400),  # missing wphone
# #     (1,{"wname":"updated_Warehouse", "wcity":"updated Aguada", "wemail":"", "wphone":"787-updated", "budget":0}, 400),  # invalid wemail
# #     (99,{"wname":"updated_Warehouse", "wcity":"updated Aguada", "wemail":"db@update-test", "wphone":"787-updated", "budget":0}, 404),  # warehouse does not exist
# # ])  
# # def test_update_warehouse(client, wid, data, status_code):
# #     expected_structure = {"Warehouse": ["wid", "wname", "wcity", "wemail", "wphone", "budget"]}
# #     endpoint = base_url+f'warehouse/{wid}'
# #     validate_updates(client, endpoint,data,status_code, expected_structure)
    
# # @pytest.mark.parametrize("rid, data, status_code", [
# #     # testing parts in rack
# #     (1,{"capacity": 100, "wid": 1, "quantity": 100, "pid": 1}, 200),  # Successful case
# #     (1,{"capacity": 100, "wid": 1, "quantity": 0, "pid": 1}, 200),  # Successful case
# #     (1,{"capacity": 10, "wid": 1, "quantity": 0, "pid": 1}, 200),  # Successful case
# #     (1,{"capacity": 10, "wid": 1, "quantity": 11, "pid": 1}, 400),  # quantity exceeds capacity
# #     (1,{"capacity": 10, "wid": 1, "quantity": -1, "pid": 1}, 400),  # invalid quantity
# #     (1,{"capacity": 10, "wid": 1, "quantity": "10", "pid": 1}, 400),  # invalid quantity
# #     (1,{"capacity": 0, "wid": 1, "quantity": 0, "pid": 1}, 400),  # invalid capacity
# #     (1,{"capacity": -10, "wid": 1, "quantity": 0, "pid": 1}, 400),  # invalid capacity
# #     (1,{"capacity": "10", "wid": 1, "quantity": 10, "pid": 1}, 400),  # invalid capacity
# #     (1,{"capacity": 100, "wid": 1, "quantity": 0, "pid": 2}, 400),  # warehouse does not have a rack with pid 2
# #     (1,{"capacity": 100, "wid": 99, "quantity": 0, "pid": 1}, 400),  # warehouse does not exist
# #     (2,{"capacity": 100, "wid": 1, "quantity": 0, "pid": 1}, 400),  # rack does not belong to warehouse
# #     (99,{"capacity": 100, "wid": 1, "quantity": 0, "pid": 1}, 404),  # rack does not exist
# #     (1,{"capacity": 100, "wid": "1", "quantity": 0, "pid": 1}, 400),  # Invalid wid
# #     (1,{"capacity": 100, "wid": 1, "quantity": 0, "pid": "1"}, 400),  # Invalid pid
# # ])  
# # def test_update_rack(client,rid,data,status_code):
# #     endpoint = base_url+f'rack/{rid}'
# #     expected_structure = {"Rack": ["rid", "capacity", "quantity", "pid", "wid"]}
# #     validate_updates(client, endpoint,data,status_code, expected_structure)