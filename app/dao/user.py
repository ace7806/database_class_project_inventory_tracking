from app.config import dbconfig
import psycopg2


# Leamsi working here

class UserDAO:

    def __init__(self):
        self.conn = psycopg2.connect(
            user=dbconfig.user,
            password=dbconfig.password,
            host=dbconfig.host,
            dbname=dbconfig.dbname,
            port=dbconfig.port)
        print(self.conn)

    def getAllUsers(self):
        cursor = self.conn.cursor()
        query = "select * from public.user as u;"
        cursor.execute(query)
        result = []
        for row in cursor:
            result.append(row)
        cursor.close()
        return result

    def getUserById(self, uid):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where uid = %s;"
        cursor.execute(query, (uid,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def getUserByFirstName(self, fname):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where fname = %s;"
        cursor.execute(query, (fname,))
        result = []
        for row in cursor:
            result.append(row)
        cursor.close()
        return result

    def getUserByLastName(self, lname):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where lname = %s;"
        cursor.execute(query, (lname,))
        result = []
        for row in cursor:
            result.append(row)
        cursor.close()
        return result

    def getUserByLastName(self, lname):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where lname = %s;"
        cursor.execute(query, (lname,))
        result = []
        for row in cursor:
            result.append(row)
        cursor.close()
        return result

    def getUserByFullName(self, fname, lname):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where fname = %s and lname = %s;"
        cursor.execute(query, (fname, lname))
        result = []
        for row in cursor:
            result.append(row)
        cursor.close()
        return result

    def getUserByEmail(self, uemail):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where uemail = %s;"
        cursor.execute(query, (uemail,))
        result = []
        for row in cursor:
            result.append(row)
        cursor.close()
        return result

    def getUserByPhone(self, uphone):
        cursor = self.conn.cursor()
        query = "select * from public.user as u where uphone = %s;"
        cursor.execute(query, (uphone,))
        result = []
        for row in cursor:
            result.append(row)
        cursor.close()
        return result

    def getUserWarehouse(self, uid):
        cursor = self.conn.cursor()
        query = 'select wid from public.user u where u.uid = %s;'
        cursor.execute(query, (uid,))
        #don't index, might be None
        wid = cursor.fetchone()
        cursor.close()
        return wid

    def getUserReceivesMost(self, wid, amount):
        cursor = self.conn.cursor()
        # query = '''
        # select uid, count(tid)
        # from public.user u natural inner join transaction
        # where u.wid = %s
        # group by uid
        # order by count(tid) desc
        # limit %s
        # '''
        query = '''
        select uid, count(tid)
        from transfert natural inner join transaction
        where wid = %s
        group by uid
        order by count(tid) desc
        limit %s
        '''
        cursor.execute(query, (wid, amount))
        result = [row for row in cursor]
        cursor.close()
        return result

    def getUsersWithMostTransactions(self, amount):
        cursor = self.conn.cursor()
        query = '''
        select uid, count(transaction) from "user" natural inner join transaction
        group by uid
        order by count(transaction) desc
        limit %s;
        '''
        cursor.execute(query, (amount,))
        result = [row for row in cursor]
        cursor.close()
        return result
    
    def insert(self, fname, lname, wid, uemail=None, uphone=None):
        cursor = self.conn.cursor()
        query = '''
                insert into
                public.user(fname, lname, uemail, uphone, wid)
                values (%s, %s, %s, %s, %s) returning uid;
                '''
        cursor.execute(query, (fname, lname, uemail, uphone, wid))
        uid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return uid

    def update(self, uid, fname, lname, wid, uemail, uphone):
        cursor = self.conn.cursor()
        query = '''
        update public.user as u
        set fname = %s, lname = %s, uemail = %s, uphone = %s, wid = %s
        where uid = %s;
        '''
        cursor.execute(query, (fname, lname, uemail, uphone, wid, uid))
        self.conn.commit()
        cursor.close()
        return uid

    def delete(self, uid):
        cursor = self.conn.cursor()
        query = "delete from public.user as u where uid = %s;"
        cursor.execute(query, (uid,))
        self.conn.commit()
        cursor.close()
        return uid
