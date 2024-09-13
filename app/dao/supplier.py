from app.config import dbconfig
import psycopg2
from psycopg2 import errors

#Jeremy at work here :)

class SupplierDAO:
    def __init__(self):
        self.conn = psycopg2.connect(
            user=dbconfig.user,
            password=dbconfig.password,
            host=dbconfig.host,
            dbname=dbconfig.dbname,
            port=dbconfig.port,
        )
        print(self.conn)

    #-----CRUD operations start here-----

    #Create
    def insert(self, sname, scity, sphone=None, semail=None):
        cursor = self.conn.cursor()
        query = '''
                insert into supplier(sname, scity, sphone, semail)
                values (%s, %s, %s, %s) returning sid;
                '''
        cursor.execute(query, (sname, scity, sphone, semail))
        sid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return sid
    
    #Read---------------------
    def get_all_suppliers(self):
        cursor = self.conn.cursor()
        query = "select * from supplier;"
        cursor.execute(query)
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_supplier_by_ID(self, sid):
        cursor = self.conn.cursor()
        query = "select * from supplier as s where s.sid = %s;"
        cursor.execute(query, (sid,))
        result = [row for row in cursor]
        cursor.close()
        return result

    #unused
    # def get_supplier_by_name(self, sname):
    #     cursor = self.conn.cursor()
    #     query = "select * from supplier as s where s.sname = %s;"
    #     cursor.execute(query, (sname,))
    #     result = [row for row in cursor]
    #     return result
    
    # def get_supplier_by_city(self, scity):
    #     cursor = self.conn.cursor()
    #     query = "select * from supplier as s where s.scity = %s;"
    #     cursor.execute(query, (scity,))
    #     result = [row for row in cursor]
    #     return result
    #-------------------------

    #Update
    def update(self, sid, scity, sname, sphone, semail):
        cursor = self.conn.cursor()
        query = '''
                    update supplier set scity = %s, sname = %s, sphone = %s, semail = %s
                    where sid = %s;
                '''
        cursor.execute(query, (scity, sname, sphone, semail, sid))
        self.conn.commit()
        cursor.close()
        return sid
    
    #Delete
    def delete(self, sid):
        try:
            cursor = self.conn.cursor()
            query = "delete from supplier where sid = %s;"
            cursor.execute(query, (sid,))
            self.conn.commit()
            cursor.close()
            return sid
        except errors.ForeignKeyViolation as error:
            self.conn.rollback()
            return -1

    #-----CRUD operations end here-----

    #-----Additional Query Operations after here-----



    #--------Supplies-----------------------------
    def supplyPart(self, stock, sid, pid):
        if stock <= 0:
            return "Error. Supplies must be greater than 0.", 400
        cursor = self.conn.cursor()
        query =  'insert into supplies(stock, sid, pid) values (%s, %s, %s) returning supid'
        cursor.execute(query, (stock, sid, pid))
        supid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return supid
    
    def update_supply_stock_by_supid(self, supid, stock):
        cursor = self.conn.cursor()
        if stock < 0:
            return "Error. Stock must be greater or equal to 0.", 400
        query = '''
                    update supplies set stock = %s
                    where supid = %s;
                '''
        cursor.execute(query, (stock, supid))
        self.conn.commit()
        cursor.close()
        return supid
    
    def deleteAllSuppliesBySupplierId(self, sid):
        cursor = self.conn.cursor()
        query = """
        DELETE FROM Supplies
        WHERE sid = %s;
        """
        cursor.execute(query, (sid,))
        self.conn.commit()
        cursor.close()
        return sid
    
    def get_supplied_parts_by_sid(self, sid):
        cursor = self.conn.cursor()
        query = """
        select pid, pprice, ptype, pname from supplies natural inner join parts where sid = %s;
        """
        cursor.execute(query, (sid,))
        result = []
        for row in cursor:
            result.append(row)
        cursor.close()
        return result
    
    def get_supply_by_sid_and_pid(self, sid, pid):
        cursor = self.conn.cursor()
        query = """
        select supid from supplies where sid = %s and pid = %s;
        """
        cursor.execute(query, (sid, pid))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else result

    def get_supply_by_supid(self,supid):
        cursor = self.conn.cursor()
        query = """
        select * from supplies where sid = %s;
        """
        cursor.execute(query, (supid,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else result

    def get_supplier_supplies_stock_by_supid(self, supid):
        cursor = self.conn.cursor()
        query = """
        select stock from supplies where supid = %s;
        """
        cursor.execute(query, (supid,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else result

    def get_supplier_supplies_stock_by_sid_and_pid(self, sid, pid):
        cursor = self.conn.cursor()
        query = """
        select stock from supplies where sid = %s and pid = %s;
        """
        cursor.execute(query, (sid,pid))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else result

    def edit_supplies_stock_by_sid_and_pid(self, sid, pid, new_stock):
        cursor = self.conn.cursor()
        query = """
        update supplies set stock = %s where sid = %s and pid = %s;
        """
        cursor.execute(query, (new_stock, sid, pid))
        self.conn.commit()
        cursor.close()
        return sid, pid

    def get_top_suppliers_for_warehouse(self, wid, amount):
        cursor = self.conn.cursor()
        query = """
        select sid, count(incid)
        from incomingt natural inner join transaction
        where wid = %s
        group by sid
        order by count(incid)
        limit %s
        """
        cursor.execute(query, (wid, amount))
        result = [row for row in cursor]
        cursor.close()
        return result

# -------- end of supplies -------------
