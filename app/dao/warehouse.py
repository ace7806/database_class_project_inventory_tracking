from app.config import dbconfig
import psycopg2
from psycopg2 import errors

#TODO(xavier)
class WarehouseDAO:
    def __init__(self):
        self.conn = psycopg2.connect(
            user=dbconfig.user,
            password=dbconfig.password,
            host=dbconfig.host,
            dbname=dbconfig.dbname,
            port=dbconfig.port)
        print(self.conn)

    def get_all_warehouses(self):
        cursor = self.conn.cursor()
        query = "select * from warehouse;"
        cursor.execute(query)
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_warehouse_by_id(self, wid):
        cursor = self.conn.cursor()
        query = 'select * from warehouse as w where w.wid = %s;'
        cursor.execute(query, (wid,))
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_warehouse_by_name(self, wname):
        cursor = self.conn.cursor()
        query = 'select * from warehouse as w where w.wname = %s;'
        cursor.execute(query, (wname,))
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_warehouse_most_incoming(self,amount):
        cursor = self.conn.cursor()
        query = '''
        select wid, count(incid)
        from warehouse natural inner join incomingt natural inner join transaction
        group by wid
        order by count(incid) desc
        limit %s;
        '''
        cursor.execute(query, (amount,))
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_warehouse_most_racks(self,amount:int):
        cursor = self.conn.cursor()
        query = '''
        select wid, count(rid)
        from rack natural inner join warehouse
        group by wid
        order by count(rid) desc
        limit %s;
        '''
        cursor.execute(query, (amount,))
        result = [row for row in cursor]
        cursor.close()
        return result

    def insert(self, wname, wcity, wemail=None, wphone=None, budget=0):
        cursor= self.conn.cursor()
        query = '''
           insert into warehouse(wname, wcity, wemail, wphone, budget)
           values (%s, %s, %s, %s, %s) returning wid;
        '''
        cursor.execute(query, (wname, wcity, wemail, wphone, budget))
        wid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return wid

    def update(self, wid, wname, wcity, wemail, wphone, budget):
        cursor = self.conn.cursor()
        query = '''
            update warehouse set wname = %s, wcity = %s, wemail = %s,
                wphone = %s, budget = %s
            where wid = %s;
        '''
        cursor.execute(query, (wname, wcity, wemail, wphone, budget, wid))
        self.conn.commit()
        cursor.close()
        return wid

    def delete(self, wid):
        try:

            cursor = self.conn.cursor()
            query = '''
            delete from warehouse where wid = %s;
            '''
            cursor.execute(query, (wid,))
            self.conn.commit()
            cursor.close()
            return wid
        except errors.ForeignKeyViolation as error:
            self.conn.rollback()
            return -1

    def get_warehouse_least_outgoing(self, amount):
        cursor = self.conn.cursor()
        query = '''
        select wid, count(outid)
        from warehouse natural inner join transaction natural inner join outgoingt
        group by wid
        order by count(outid)
        limit %s;
        '''
        cursor.execute(query, (amount,))
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_most_city_transactions(self, amount):
        cursor = self.conn.cursor()
        query = '''
        select wcity, count(tid)
        from warehouse natural inner join rack
        natural inner join transaction
        group by wcity
        order by count(tid) desc
        limit %s;
        '''
        cursor.execute(query, (amount,))
        result = [row for row in cursor]
        cursor.close()
        return result

    #queries needed for validation
    def get_warehouse_budget(self, wid):
        cursor = self.conn.cursor()
        query = '''
            select budget from warehouse as w where w.wid = %s;
        '''
        cursor.execute(query, (wid,))
        budget = cursor.fetchone()
        cursor.close()
        return budget[0] if budget else budget

    def get_warehouse_profit(self, wid):
        cursor = self.conn.cursor()
        query = '''
        select coalesce(expenses.year, earnings.year) as year, coalesce(income - cost, income, -cost) as profit from

        (select extract(year from tdate) as year, sum(pprice*transaction.tquantity) as cost
        from incomingt natural inner join transaction natural inner join parts where wid =%s
        group by year) as expenses

        full outer join

        (select extract(year from tdate) as year, sum(pprice*transaction.tquantity*1.10) as income
        from outgoingt natural inner join transaction  natural inner join parts where wid=%s group by year) as earnings
        on expenses.year = earnings.year
        order by year;
        '''
        cursor.execute(query, (wid, wid))
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_warehouse_most_deliver(self, amount):
        cursor = self.conn.cursor()
        query = '''
        select wid, count(taction) as count
        from transfert natural inner join transaction
        where taction = 'sending'
        group by wid
        order by count desc
        limit %s;
        '''
        cursor.execute(query, (amount, ))
        result = [row for row in cursor]
        cursor.close()
        return result
    
    def set_warehouse_budget(self, wid, new_budget):
        cursor = self.conn.cursor()
        query = '''
            update warehouse set budget = %s where wid = %s;
        '''
        cursor.execute(query, (new_budget, wid))
        self.conn.commit()
        cursor.close()
        return wid
