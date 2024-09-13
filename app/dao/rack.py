from app.config import dbconfig
import psycopg2
from psycopg2 import errors

# TODO(xavier)
class RackDAO:
    def __init__(self):
        self.conn = psycopg2.connect(
            user=dbconfig.user,
            password=dbconfig.password,
            host=dbconfig.host,
            dbname=dbconfig.dbname,
            port=dbconfig.port)
        print(self.conn)

    def get_all_racks(self):
        cursor = self.conn.cursor()
        query = "select * from rack;"
        cursor.execute(query)
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_rack_by_id(self, rid):
        cursor = self.conn.cursor()
        query = 'select * from rack as r where r.rid = %s;'
        cursor.execute(query, (rid,))
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_warehouse_racks_lowstock(self, wid, amount):
        cursor = self.conn.cursor()
        query = '''
        select rid, capacity, wid, quantity, pid
        from (
           select * from
           warehouse w natural inner join rack r
           where w.wid = %s
        ) as racks
        where racks.quantity < ( racks.capacity * 0.25 )
        order by racks.quantity
        limit %s;
        '''
        cursor.execute(query, (wid, amount))
        self.conn.commit()
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_most_expensive_racks(self, wid):
        cursor = self.conn.cursor()
        query = '''
        select rid, pprice*rack.quantity as total_price from rack natural inner join parts
        where wid = %s
        order by total_price desc
        limit 3;
        '''
        cursor.execute(query, (wid,))
        self.conn.commit()
        result = [row for row in cursor]
        cursor.close()
        return result

    #TODO prob belongs in parts
    #weird return bc of its being built as regular parts
    def get_warehouse_rack_bottom_material(self, wid, amount):
        cursor = self.conn.cursor()
        query = '''
        select ptype,count(p.ptype)
        from (
            select * from
            warehouse w natural inner join rack r
            where w.wid = %s
        ) as racks natural inner join parts p
       group by p.ptype
       order by count(p.ptype)
       limit %s
        '''
        cursor.execute(query,(wid, amount))
        self.conn.commit()
        result = [row for row in cursor]
        cursor.close()
        return result

    def insert(self, capacity, quantity, pid, wid):
        cursor = self.conn.cursor()
        query = '''
           insert into rack(capacity, wid, quantity, pid)
           values (%s, %s, %s, %s) returning rid;
        '''
        cursor.execute(query, (capacity, wid, quantity, pid))
        rid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return rid

    def update(self, rid, capacity, quantity, pid, wid):
        cursor = self.conn.cursor()
        query = '''
            update rack set capacity = %s, wid = %s, quantity = %s, pid = %s
            where rid = %s;
        '''
        cursor.execute(query, (capacity, wid, quantity, pid, rid))
        self.conn.commit()
        cursor.close()
        return rid

    def delete(self, rid):
        try:
            cursor = self.conn.cursor()
            query = '''
                delete from rack where rid = %s;
            '''
            cursor.execute(query, (rid,))
            self.conn.commit()
            cursor.close()
            return rid
        except errors.ForeignKeyViolation as error:
            self.conn.rollback()
            return -1

    def get_parts_in_rack(self, rid):
        cursor = self.conn.cursor()
        query = '''
            select * from parts natural inner join rack as r where r.rid = %s;
        '''
        cursor.execute(query, (rid,))
        result = [row for row in cursor]
        cursor.close()
        return result


    def get_rid_from_wid_and_pid(self, wid, pid):
        cursor = self.conn.cursor()
        query = '''
            select rid from rack where wid=%s and pid=%s;
        '''
        cursor.execute(query, (wid, pid))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else result

    #queries needed for validation
    def get_rack_warehouse(self, rid):
        cursor = self.conn.cursor()
        query = '''
            select wid from rack as r where r.rid = %s;
        '''
        cursor.execute(query, (rid,))
        wid = cursor.fetchone()
        cursor.close()
        return wid

    def get_rack_part(self, rid):
        cursor = self.conn.cursor()
        query = '''
            select pid from rack as r where r.rid = %s;
        '''
        cursor.execute(query, (rid,))
        pid = cursor.fetchone()
        cursor.close()
        return pid
    
    def get_rack_capacity(self, rid):
        cursor = self.conn.cursor()
        query = '''
            select capacity from rack as r where r.rid = %s;
        '''
        cursor.execute(query, (rid,))
        capacity = cursor.fetchone()[0]
        cursor.close()
        return capacity

    def get_rack_quantity(self, rid):
        cursor = self.conn.cursor()
        query = '''
            select quantity from rack as r where r.rid = %s;
        '''
        cursor.execute(query, (rid,))
        quantity = cursor.fetchone()
        cursor.close()
        return quantity[0] if quantity else quantity

    def set_rack_quantity(self, rid, new_quantity):
        cursor = self.conn.cursor()
        query = '''
            update rack set quantity = %s where rid = %s;
         '''
        cursor.execute(query, (new_quantity, rid))
        self.conn.commit()
        cursor.close()
        return rid

    def get_parts_in_warehouse(self, wid):
        cursor = self.conn.cursor()
        query = '''
                select ptype, pname, pid
                from parts natural inner join rack natural inner join warehouse
                where wid = %s;
                '''
        cursor.execute(query, (wid,))
        self.conn.commit()
        result = [row for row in cursor]
        cursor.close()
        return result

    def rack_in_warehouse_validation(self, wid, pid):
        cursor = self.conn.cursor()
        query = '''with test as (select rid
                from rack natural inner join warehouse
                where wid = %s and pid = %s)
                select rid
                from rack
                where rid IN (select * from test);
                '''
        cursor.execute(query, (wid, pid))
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False
    def update_rack_in_warehouse_validation(self, pid, wid, rid):
        cursor = self.conn.cursor()
        query = '''
            select exists (
                select 1
                from rack
                where pid = %s
                    and wid = %s
                    and rid <> %s
            ) as rack_exists;
        '''
        cursor.execute(query, (pid, wid, rid))
        result = cursor.fetchone()
        return result[0]
