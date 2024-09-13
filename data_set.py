from app.handlers import user, rack, warehouse, parts, transaction, supplier
from app.config import dbconfig
import psycopg2
from app import app

#Seba Local DB Credentials
dbconfig.host = "localhost"
dbconfig.dbname = "testdb"
dbconfig.user = "postgres"
dbconfig.password = "postgres"
dbconfig.port = "5432"

#Jeremy Local DB Credentials
# dbconfig.user = 'postgres'
# dbconfig.password = 'DBLosCangri587'
# dbconfig.dbname = 'postgres'
# dbconfig.host = 'localhost'
# dbconfig.port = 5432

a = app.test_client()

def reset_db():
    # List of tables to truncate
    tables_to_truncate = [
        'supplies', 'incomingt', 'outgoingt',
        'transaction', '"user"', 'supplier', 'rack', 'parts',
        'transfert', 'warehouse'
    ]
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
    
reset_db()
p = '/los-cangri/part'
w = '/los-cangri/warehouse'
u = '/los-cangri/user'
r = '/los-cangri/rack'
s = '/los-cangri/supplier'
inc = '/los-cangri/incoming'
o = '/los-cangri/outgoing'
e = '/los-cangri/exchange'



#Part Creation--------------------------------------------------------
# pypes{ Plastic: 3, Wood: 4, Steel: 1, PVC: 1}
a.post(p, json = {"pprice":13, "ptype":"Plastic", "pname":"Table"}) #1
a.post(p, json = {"pprice":75, "ptype":"Steel", "pname":"Pipe"}) #2
a.post(p, json = {"pprice":10, "ptype":"Wood", "pname":"Plank"}) #3
a.post(p, json = {"pprice":20, "ptype":"Plastic", "pname":"Cupboard"}) #4
a.post(p, json = {"pprice":50, "ptype":"Wood", "pname":"Door"}) #5
a.post(p, json = {"pprice":75, "ptype":"Wood", "pname":"Sculpture"}) #6
a.post(p, json = {"pprice":35, "ptype":"Plastic", "pname":"Bottle"}) #7
a.post(p, json = {"pprice":35, "ptype":"PVC", "pname":"Kiddie Pool"}) #8
a.post(p, json = {"pprice":45, "ptype":"Wood", "pname":"Table"}) #9
#Supplier Creation------------------------------------------------------
#Supp 1
a.post(s, json = {"sname":"Berrios Imports", "scity":"Moca", "sphone":"787-0DB-TEST", "semail":"test@gmail.com"}) 
#Supp 2
a.post(s, json = {"sname":"Sams Club", "scity":"Trujillo", "sphone":"787-1DB-TEST", "semail":"test@hotmail.com"})
#Supp 3
a.post(s, json = {"sname":"Sears", "scity":"Aguada", "sphone":"787-2DB-TEST", "semail":"test@icloud.com"})
#Supp 4
a.post(s, json = {"sname":"Walgreens", "scity":"San Juan", "sphone":"787-3DB-TEST", "semail":"test@business.com"})

#Supplies Creation (Each Supplier will supply 3 parts)--------------------
#Supplier 1
a.post(s+f"/{1}/parts", json = {"pid":1, "stock":1000})
a.post(s+f"/{1}/parts", json ={"pid":2, "stock":100})
a.post(s+f"/{1}/parts", json ={"pid":3, "stock":100})

#Supplier 2
a.post(s+f"/{2}/parts", json ={"pid":3, "stock":500})
a.post(s+f"/{2}/parts", json ={"pid":5, "stock":500})
a.post(s+f"/{2}/parts", json ={"pid":6, "stock":500})

#Supplier 3
a.post(s+f"/{3}/parts", json ={"pid":7, "stock":400})
a.post(s+f"/{3}/parts", json ={"pid":4, "stock":400})
a.post(s+f"/{3}/parts", json ={"pid":8, "stock":400})

#Supplier 4
a.post(s+f"/{4}/parts", json ={"pid":4, "stock":300})
a.post(s+f"/{4}/parts", json ={"pid":3, "stock":300})
a.post(s+f"/{4}/parts", json ={"pid":9, "stock":300})

#Warehouse Creation-------------------------------------------------------
#cities: Aguada: 4, San Juan: 1, Mayaguez: 3, Caguas: 1, Moca: 1, Fajardo: 1
a.post(w, json ={"wname":"Transaction_Warehouse", "wcity":"Aguada", "wemail":"db@lol", "wphone":"787-1DB-TEST", "budget":5000}) #1
a.post(w, json ={"wname":"big balling warehouse", "wcity":"Aguada", "wemail":"db@test", "wphone":"787-2DB-TEST", "budget":10000}) #2
a.post(w, json ={"wname":"small balling warehouse", "wcity":"San Juan", "wemail":"db@yolo", "wphone":"787-3DB-TEST", "budget":5000}) #3
a.post(w, json ={"wname":"bobs warehouse", "wcity":"Mayaguez", "wemail":"db@gmail", "wphone":"787-4DB-TEST", "budget":1000}) #4
a.post(w, json ={"wname":"Database Warehouse", "wcity":"Caguas", "wemail":"db@hotmail", "wphone":"787-5DB-TEST", "budget":5000}) #5
a.post(w, json ={"wname":"Jeremy Warehouse", "wcity":"Aguada", "wemail":"db@Jeremy", "wphone":"787-6DB-TEST", "budget":10000}) #6
a.post(w, json ={"wname":"Sebastian warehouse", "wcity":"Moca", "wemail":"db@Sebastian", "wphone":"787-7DB-TEST", "budget":5000}) #7
a.post(w, json ={"wname":"Xavier warehouse", "wcity":"Mayaguez", "wemail":"db@Xavier", "wphone":"787-8DB-TEST", "budget":1000}) #8
a.post(w, json ={"wname":"Leamsi Warehouse", "wcity":"Fajardo", "wemail":"db@Leamsi", "wphone":"787-9DB-TEST", "budget":5000}) #9
a.post(w, json ={"wname":"Los Cangri Warehouse", "wcity":"Mayaguez", "wemail":"db@Cangri", "wphone":"787-0DB-TEST", "budget":3000}) #10
a.post(w, json ={"wname":"poor mans Warehouse", "wcity":"Aguada", "wemail":"db@Phase3", "wphone":"787-0DB-TEST", "budget":100000}) #11

#User Creation---------------------------------------------------------------------------------
first_names = ["Ethan", "Ava", "Lucas", "Mia", "Oliver", "Sophia", "Noah", "Isabella", "Liam", "Olivia", "Jackson", "Emma", "Aiden", "Harper", "Caleb", "Abigail", "Mason", "Emily", "Logan", "Ella", "Benjamin", "Scarlett"]

last_names = ["Johnson", "Smith", "Williams", "Brown", "Jones", "Garcia", "Davis", "Rodriguez", "Martinez", "Hernandez", "Jackson", "Taylor", "Anderson", "Thomas", "White", "Harris", "Martin", "Thompson", "Robinson", "Clark", "Lewis", "Walker"]
wid = 1
for i in range(22):
    a.post(u, json = {"fname": first_names[i],"lname": last_names[i],"uemail": "db@test","uphone":"787-0DB-TEST","wid": wid})
    if (i+1) % 2 == 0:
        wid += 1
    
    
#Rack Creation---------------------------------------------------------------------------------
a.post(r, json = {"capacity":100, "wid":1, "quantity":50, "pid":1})
a.post(r, json = {"capacity":100, "wid":1, "quantity":24, "pid":2})
a.post(r, json = {"capacity":100, "wid":1, "quantity":4, "pid":3})
a.post(r, json = {"capacity":100, "wid":1, "quantity":12, "pid":4})
a.post(r, json = {"capacity":100, "wid":1, "quantity":7, "pid":5})
a.post(r, json = {"capacity":100, "wid":1, "quantity":23, "pid":6})

a.post(r, json = {"capacity":100, "wid":2, "quantity":9, "pid":1})
a.post(r, json = {"capacity":100, "wid":2, "quantity":25, "pid":2})
a.post(r, json = {"capacity":100, "wid":2, "quantity":21, "pid":7})
a.post(r, json = {"capacity":100, "wid":2, "quantity":8, "pid":8})
a.post(r, json = {"capacity":100, "wid":2, "quantity":17, "pid":9})
a.post(r, json = {"capacity":100, "wid":2, "quantity":80, "pid":3})
a.post(r, json = {"capacity":100, "wid":2, "quantity":80, "pid":5})
a.post(r, json = {"capacity":100, "wid":2, "quantity":80, "pid":6})

a.post(r, json = {"capacity":100, "wid":3, "quantity":5, "pid":1})
a.post(r, json = {"capacity":100, "wid":3, "quantity":13, "pid":2})
a.post(r, json = {"capacity":100, "wid":3, "quantity":11, "pid":5})
a.post(r, json = {"capacity":100, "wid":3, "quantity":24, "pid":6})
a.post(r, json = {"capacity":100, "wid":3, "quantity":4, "pid":7})
a.post(r, json = {"capacity":100, "wid":3, "quantity":67, "pid":8})
a.post(r, json = {"capacity":100, "wid":3, "quantity":67, "pid":9})

a.post(r, json = {"capacity":100, "wid":4, "quantity":60, "pid":1})
a.post(r, json = {"capacity":100, "wid":4, "quantity":23, "pid":2})
a.post(r, json = {"capacity":100, "wid":4, "quantity":57, "pid":9})
a.post(r, json = {"capacity":100, "wid":4, "quantity":87, "pid":8})
a.post(r, json = {"capacity":100, "wid":4, "quantity":18, "pid":7})
a.post(r, json = {"capacity":100, "wid":4, "quantity":14, "pid":6})
a.post(r, json = {"capacity":100, "wid":4, "quantity":14, "pid":5})

a.post(r, json = {"capacity":100, "wid":5, "quantity":12, "pid":1})
a.post(r, json = {"capacity":100, "wid":5, "quantity":21, "pid":2})
a.post(r, json = {"capacity":100, "wid":5, "quantity":5, "pid":3})
a.post(r, json = {"capacity":100, "wid":5, "quantity":32, "pid":5})
a.post(r, json = {"capacity":100, "wid":5, "quantity":5, "pid":6})
a.post(r, json = {"capacity":100, "wid":5, "quantity":8, "pid":9})
a.post(r, json = {"capacity":100, "wid":5, "quantity":8, "pid":4})
a.post(r, json = {"capacity":100, "wid":5, "quantity":8, "pid":8})

a.post(r, json = {"capacity":100, "wid":6, "quantity":18, "pid":1})
a.post(r, json = {"capacity":100, "wid":6, "quantity":53, "pid":2})
a.post(r, json = {"capacity":100, "wid":6, "quantity":90, "pid":9})
a.post(r, json = {"capacity":100, "wid":6, "quantity":9, "pid":7})
a.post(r, json = {"capacity":100, "wid":6, "quantity":8, "pid":5})
a.post(r, json = {"capacity":100, "wid":6, "quantity":53, "pid":3})

a.post(r, json = {"capacity":100, "wid":7, "quantity":8, "pid":1})
a.post(r, json = {"capacity":100, "wid":7, "quantity":22, "pid":2})
a.post(r, json = {"capacity":100, "wid":7, "quantity":3, "pid":6})
a.post(r, json = {"capacity":100, "wid":7, "quantity":21, "pid":6})
a.post(r, json = {"capacity":100, "wid":7, "quantity":24, "pid":8})
a.post(r, json = {"capacity":100, "wid":7, "quantity":13, "pid":9})

a.post(r, json = {"capacity":100, "wid":8, "quantity":12, "pid":1})
a.post(r, json = {"capacity":100, "wid":8, "quantity":2, "pid":2})
a.post(r, json = {"capacity":100, "wid":8, "quantity":5, "pid":7})
a.post(r, json = {"capacity":100, "wid":8, "quantity":4, "pid":4})
a.post(r, json = {"capacity":100, "wid":8, "quantity":2, "pid":6})
a.post(r, json = {"capacity":100, "wid":8, "quantity":1, "pid":8})

a.post(r, json = {"capacity":100, "wid":9, "quantity":13, "pid":1})
a.post(r, json = {"capacity":100, "wid":9, "quantity":3, "pid":2})
a.post(r, json = {"capacity":100, "wid":9, "quantity":5, "pid":8})
a.post(r, json = {"capacity":100, "wid":9, "quantity":2, "pid":5})
a.post(r, json = {"capacity":100, "wid":9, "quantity":6, "pid":3})
a.post(r, json = {"capacity":100, "wid":9, "quantity":20, "pid":4})

a.post(r, json = {"capacity":100, "wid":10, "quantity":1, "pid":1})
a.post(r, json = {"capacity":100, "wid":10, "quantity":11, "pid":2})
a.post(r, json = {"capacity":100, "wid":10, "quantity":14, "pid":1})
a.post(r, json = {"capacity":100, "wid":10, "quantity":42, "pid":9})
a.post(r, json = {"capacity":100, "wid":10, "quantity":21, "pid":3})
a.post(r, json = {"capacity":100, "wid":10, "quantity":15, "pid":5})

a.post(r, json = {"capacity":100, "wid":11, "quantity":5, "pid":1})
a.post(r, json = {"capacity":100, "wid":11, "quantity":2, "pid":2})
a.post(r, json = {"capacity":100, "wid":11, "quantity":32, "pid":4})
a.post(r, json = {"capacity":100, "wid":11, "quantity":2, "pid":7})
a.post(r, json = {"capacity":100, "wid":11, "quantity":1, "pid":3})
a.post(r, json = {"capacity":100, "wid":11, "quantity":0, "pid":9})


#Transaction Creation---------------------------------------------------------------------------------

#incoming
#wid 1
a.post(inc, json = {"tquantity":2,"pid":1,"sid":1,"uid":1,"wid":1})
a.post(inc, json = {"tquantity":1,"pid":2,"sid":1,"uid":2,"wid":1})
a.post(inc, json = {"tquantity":3,"pid":3,"sid":1,"uid":1,"wid":1})

#wid 2
a.post(inc, json = {"tquantity":2,"pid":1,"sid":1,"uid":3,"wid":2})
a.post(inc, json = {"tquantity":1,"pid":5,"sid":2,"uid":4,"wid":2})
a.post(inc, json = {"tquantity":3,"pid":6,"sid":2,"uid":4,"wid":2})
a.post(inc, json = {"tquantity":3,"pid":3,"sid":1,"uid":3,"wid":2})

# #wid 3

a.post(inc, json = {"tquantity":7,"pid":9,"sid":4,"uid":5,"wid":3})


# #wid 4
a.post(inc, json = {"tquantity":2,"pid":1,"sid":1,"uid":7,"wid":4})
a.post(inc, json = {"tquantity":1,"pid":6,"sid":2,"uid":8,"wid":4})
a.post(inc, json = {"tquantity":3,"pid":5,"sid":2,"uid":7,"wid":4})

#wid 5
a.post(inc, json = {"tquantity":4,"pid":3,"sid":4,"uid":9,"wid":5})
a.post(inc, json = {"tquantity":5,"pid":9,"sid":4,"uid":9,"wid":5})
a.post(inc, json = {"tquantity":1,"pid":4,"sid":4,"uid":9,"wid":5})
a.post(inc, json = {"tquantity":1,"pid":8,"sid":3,"uid":9,"wid":5})
a.post(inc, json = {"tquantity":1,"pid":6,"sid":2,"uid":9,"wid":5})
a.post(inc, json = {"tquantity":1,"pid":1,"sid":1,"uid":9,"wid":5})

#outgoing
a.post(o, json = {"tquantity":4,"obuyer":"Test","pid":1,"uid":1,"wid":1})
a.post(o, json = {"tquantity":1,"obuyer":"Test","pid":2,"uid":2,"wid":1})
a.post(o, json = {"tquantity":7,"obuyer":"Test","pid":5,"uid":1,"wid":1})

a.post(o, json = {"tquantity":2,"obuyer":"omegle","pid":8,"uid":3,"wid":2})
a.post(o, json = {"tquantity":3,"obuyer":"papa johns","pid":9,"uid":4,"wid":2})
a.post(o, json = {"tquantity":1,"obuyer":"big bear bobby","pid":3,"uid":3,"wid":2})

a.post(o, json = {"tquantity":2,"obuyer":"Test","pid":5,"uid":5,"wid":3})
a.post(o, json = {"tquantity":6,"obuyer":"Test","pid":6,"uid":6,"wid":3})
a.post(o, json = {"tquantity":4,"obuyer":"Test","pid":7,"uid":5,"wid":3})



#exchange
#Deliveries: by wid = 1: 3, wid = 10: 3, wid = 8: 2, wid = 2: 1, wid = 7: ,
a.post(e, json = {"tquantity":1, "pid":1, "sending_wid": 1, "receiving_wid": 2, "sending_uid": 1, "receiving_uid": 3})
a.post(e, json = {"tquantity":1, "pid":2, "sending_wid": 1, "receiving_wid": 2, "sending_uid": 1, "receiving_uid": 3})
a.post(e, json = {"tquantity":1, "pid":1, "sending_wid": 1, "receiving_wid": 2, "sending_uid": 1, "receiving_uid": 3})

a.post(e, json = {"tquantity":1, "pid":9, "sending_wid": 10, "receiving_wid": 11, "sending_uid": 20, "receiving_uid": 22})
a.post(e, json = {"tquantity":1, "pid":5, "sending_wid": 10, "receiving_wid": 9, "sending_uid": 19, "receiving_uid": 18})
a.post(e, json = {"tquantity":1, "pid":1, "sending_wid": 10, "receiving_wid": 1, "sending_uid": 20, "receiving_uid": 2})

a.post(e, json = {"tquantity":1, "pid":6, "sending_wid": 8, "receiving_wid": 7, "sending_uid": 15, "receiving_uid": 14})
a.post(e, json = {"tquantity":1, "pid":4, "sending_wid": 8, "receiving_wid": 9, "sending_uid": 15, "receiving_uid": 17})
a.post(e, json = {"tquantity":1, "pid":9, "sending_wid": 2, "receiving_wid": 4, "sending_uid": 3, "receiving_uid": 7})
a.post(e, json = {"tquantity":1, "pid":6, "sending_wid": 7, "receiving_wid": 5, "sending_uid": 13, "receiving_uid": 10})
a.post(e, json = {"tquantity":1, "pid":2, "sending_wid": 2, "receiving_wid": 4, "sending_uid": 4, "receiving_uid": 8})

