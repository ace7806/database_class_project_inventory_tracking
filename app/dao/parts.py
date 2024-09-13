from app.config import dbconfig
import psycopg2
from psycopg2 import errors

class PartsDAO:
    def __init__(self):
        self.conn = psycopg2.connect(
            user=dbconfig.user,
            password=dbconfig.password,
            host=dbconfig.host,
            dbname=dbconfig.dbname,
            port=dbconfig.port,
        )
        print(self.conn)

    def getAllParts(self):
        cursor = self.conn.cursor()
        query = "select * from parts;"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        return result
    
    def getPartById(self, pid):
        cursor = self.conn.cursor()
        query = "select * from parts where pid = %s;"
        cursor.execute(query, (pid,))
        result = cursor.fetchone()
        return result
    
    def getPartsByPrice(self, pprice):
        cursor = self.conn.cursor()
        query = "select * from parts where pprice = %s;"
        cursor.execute(query, (pprice,))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getPartsByType(self, ptype):
        cursor = self.conn.cursor()
        query = "select * from parts where ptype = %s;"
        cursor.execute(query, (ptype,))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getPartsByPriceAndType(self, pprice, ptype):
        cursor = self.conn.cursor()
        query = "select * from parts where pprice = %s and ptype = %s;"
        cursor.execute(query, (pprice, ptype))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def getPartsByName(self, pname):
        cursor = self.conn.cursor()
        query = "select * from parts where pname = %s;"
        cursor.execute(query, (pname,))
        result = []
        for row in cursor:
            result.append(row)
        return result

    def insert(self, pprice, ptype, pname):
        cursor = self.conn.cursor()
        query = "insert into parts(pprice, ptype, pname) values (%s, %s, %s) returning pid;"
        cursor.execute(query, (pprice, ptype, pname))
        pid = cursor.fetchone()[0]
        self.conn.commit()
        return pid

    def delete(self, pid):
        try:
            cursor = self.conn.cursor()
            query = "delete from parts where pid = %s;"
            cursor.execute(query, (pid,))
            self.conn.commit()
            return pid
        except errors.ForeignKeyViolation as error:
            self.conn.rollback()
            return -1

    def update(self, pid, pprice, ptype, pname):
        cursor = self.conn.cursor()
        query = "update parts set pprice = %s, ptype = %s, pname = %s where pid = %s;"
        cursor.execute(query, (pprice, ptype, pname, pid))
        self.conn.commit()
        return pid

    #queries needed for validation
    def get_part_price(self, pid):
        cursor = self.conn.cursor()
        query = '''
            select pprice from parts as p where p.pid = %s;
        '''
        cursor.execute(query, (pid,))
        pprice = cursor.fetchone()
        return pprice[0] if pprice else pprice
