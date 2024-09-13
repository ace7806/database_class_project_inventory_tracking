from app.config import dbconfig
import psycopg2

#Jeremy at work here :)

class TransactionDAO:
    def __init__(self):
        self.conn = psycopg2.connect(
            user=dbconfig.user,
            password=dbconfig.password,
            host=dbconfig.host,
            dbname=dbconfig.dbname,
            port=dbconfig.port,
        )
        print(self.conn)

    query_dict = {
        #queries for master table-----
        #Todo:
        "get_all_transactions":'''
                                select * from transaction;
                                ''',

        "insert_transaction": '''insert into transaction(tdate, tquantity, ttotal, pid, sid, rid, uid)
                                values(now(), %s, %s, %s, %s, %s, %s) returning tid;
                            ''',
                                
        "update_transaction":'''
                            update transaction set tdate = now(), tquantity = %s, ttotal = %s, pid = %s,
                            sid = %s, rid = %s, uid = %s
                            where tid = %s;
                            ''',
        "delete_transaction":'''
                            delete from transaction where tid = %s;
                            ''',
        #query needed for jsonify
        "get_transaction_date":'''
                            select tdate from transaction where tid = %s;
                            ''',
        
        #queries for incoming-----
        "get_all_incoming":'''
                            select * from incomingt natural inner join transaction where incid = %s;
                            ''',
        "get_incoming_by_id":'''
                            select * from incomingt natural inner join transaction where incid = %s;
                            ''',
        "get_tid_from_incoming":'''
                            select tid from incomingt where incid = %s;
                            ''',
        "insert_incoming":'''
                            insert into incomingt(wid, tid)
                            values (%s, %s) returning incid;
                            ''',
        "update_incoming":'''
                            update incomingt set <write new vals here> where incid = %s;
                            ''',
        "delete_incoming":'''
                            delete from incomingt where incid = %s;
                            ''',
        "get_least_cost":'''
                            select tdate, sum(ttotal)
                            from warehouse natural inner join incomingt
                                natural inner join transaction
                            where wid = %s
                            group by tdate
                            order by sum(ttotal)
                            limit %s
                            ''',
        #queries for outgoing-----
        "get_all_outgoing":'''
                            select * from outgoingt;
                            ''',
        "get_outgoing_by_id":'''
                            select * from outgoingt natural inner join where outid = %s;
                            ''',
        "insert_outgoing":'''
                            insert into outgoingt(obuyer, wid, tid)
                            values (%s, %s, %s) returning outid;
                            ''',
        "update_outgoing":'''
                            update outgoingt set obuyer = %s, wid = %s, tid = %s;
                            ''',
        "delete_outgoing":'''
                            delete from outgoingt where outid = %s;
                            ''',
        #queries for exchange-----
        "get_all_exchange":'''
                            select * from transfert;
                            ''',
        "get_exchange_by_id":'''
                            select * from transfert where tranid = %s;
                            ''',
        "insert_exchange":'''
                            insert into transfert(attributes here)
                            values (%s, %s, %s, %s) returning tranid;
                            ''',
        "update_exchange":'''
                            update transfert set <write new vals here> where tranid = %s;
                            ''',
        "delete_exchange":'''
                            delete from transfert where tranid = %s;
                            '''
        
    }


    #----------------------dao for master----------------------
    def get_all_transactions(self):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["get_all_transactions"])
        result = [row for row in cursor]
        cursor.close()
        return result
    
    def insert_transaction(self, tquantity, pid, wid, uid, tdate = 'now()'):
        cursor = self.conn.cursor()
        query = '''insert into transaction(tdate, tquantity, pid, wid, uid)
                                values(%s, %s, %s, %s, %s) returning tid;
                            '''
        cursor.execute(query, (tdate, tquantity, pid, wid, uid))
        tid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return tid

    def update_transaction(self, tquantity, wid, pid, rid, uid, tid):
        cursor = self.conn.cursor()
        query = '''
                update transaction set tdate = now(), tquantity = %s, wid = %s, pid = %s,
                uid = %s
                where tid = %s;
                ''',
        cursor.execute(query, (tquantity, wid, pid, uid, tid))
        self.conn.commit()
        cursor.close()
        return tid
    
    #needed for jsonify
    def get_transaction_date(self, tid):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["get_transaction_date"], (tid,))
        tdate = cursor.fetchone()
        cursor.close()
        return tdate
    def delete_transaction(self, tid):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["delete_transaction"], (tid,))
        self.conn.commit()
        cursor.close()
        return tid
    #----------------------dao for incoming----------------------
    def get_all_incoming(self):
        cursor = self.conn.cursor()
        query = "select * from incomingt natural inner join transaction;"
        cursor.execute(query)
        result = [row for row in cursor]
        cursor.close()
        return result
    
    def get_incoming_by_id(self, incid):
        cursor = self.conn.cursor()
        query = "select * from incomingt natural inner join transaction where incid = %s;"
        cursor.execute(query, (incid,))
        result = [row for row in cursor]
        cursor.close()
        return result
    def get_tid_from_incoming(self, incid):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["get_tid_from_incoming"], (incid,))
        tid = cursor.fetchone()[0]
        cursor.close()
        return tid

    def insert_incoming(self, sid, tid): #modify attributes
        cursor = self.conn.cursor()
        query = '''
                insert into incomingt(sid, tid)
                values (%s, %s) returning incid;
                '''
        cursor.execute(query, (sid, tid))
        incid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return incid
    
    def update_incoming(self, sid, incid):
        cursor = self.conn.cursor()
        query = "update incomingt set sid= %s where incid = %s;"
        cursor.execute(query, (sid, incid))
        self.conn.commit()
        cursor.close()
        return incid

    #isnt going to work since ttotal got deprecated   
    def get_warehouse_least_cost(self, wid, amount):
        cursor = self.conn.cursor()
        query = '''
                select tdate, sum(pprice*tquantity)
                from transaction natural inner join incomingt 
                    natural inner join parts natural inner join warehouse
                where wid = %s
                group by tdate
                order by sum(pprice*tquantity)
                limit %s
                '''
        cursor.execute(query, (wid, amount))
        result = [row for row in cursor]
        cursor.close()
        return result

    #for debugging, will be unused
    def delete_incoming(self, incid):
        cursor = self.conn.cursor()
        cursor.execute(self.query_dict["delete_incoming"], (incid,))
        self.conn.commit()
        cursor.close()
        return incid
    

    '''so basicamente el array te da uno de 3 resultados:
        true = el transaction es valido
        false = el transaction no es valido
        empty = no existe los connections entre uid, wid, rid, etc.
    '''
    def validate_incoming(self, tquant, uid, wid, rid, pid, sid):
        cursor = self.conn.cursor()
        query = '''
        select (budget-pprice*%s >= 0 and quantity + %s <= capacity and stock - %s >=0) as valid
        from warehouse natural inner join rack natural inner join parts natural inner join "user" natural inner join supplies natural inner join supplier
        where uid =%s and wid = %s and rid = %s and pid = %s and sid = %s;        
        '''
        cursor.execute(query, (tquant, tquant, tquant, uid, wid, rid, pid, sid))
        result = [row for row in cursor]
        cursor.close()
        return result
    #----------------------dao for outgoing----------------------
    def get_all_outgoing(self):
        cursor = self.conn.cursor()
        query = "select * from outgoingt natural inner join transaction;"
        cursor.execute(query)
        result = [row for row in cursor]
        cursor.close()
        return result
    
    def get_outgoing_by_id(self, outid):
        cursor = self.conn.cursor()
        query = "select * from outgoingt natural inner join transaction where outid = %s;"
        cursor.execute(query, (outid,))
        result = [row for row in cursor]
        cursor.close()
        return result
    
    def get_tid_from_outgoing(self, outid):
        cursor = self.conn.cursor()
        query = "select tid from outgoingt where outid = %s;"
        cursor.execute(query, (outid,))
        tid = cursor.fetchone()
        cursor.close()
        return tid[0] if tid else tid

    def insert_outgoing(self, obuyer, tid):
        cursor = self.conn.cursor()
        query = '''
                insert into outgoingt(obuyer, tid)
                values (%s, %s) returning outid;
                '''
        cursor.execute(query, (obuyer, tid))
        outid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return outid
    
    #TODO(xavier)
    def update_outgoing(self, outid, obuyer):
        cursor = self.conn.cursor()
        query = "update outgoingt set obuyer = %s, where outid = %s;"
        cursor.execute(query, (obuyer, outid))
        self.conn.commit()
        cursor.close()
        return outid

    #for debugging, will be unused
    def delete_outgoing(self, tid):
        return

    #----------------------dao for exchange----------------------
    def get_all_exchange(self):
        cursor = self.conn.cursor()
        query = "select * from transfert natural inner join transaction;"
        cursor.execute(query)
        result = [row for row in cursor]
        cursor.close()
        return result
    
    def get_exchange_by_id(self, tranid):
        cursor = self.conn.cursor()
        query = "select * from transfert natural inner join transaction where tranid = %s;"
        cursor.execute(query, (tranid,))
        result = [row for row in cursor]
        cursor.close()
        return result

    def get_tid_from_exchange(self, tranid):
        cursor = self.conn.cursor()
        query = "select tid from transfert where tranid = %s;"
        cursor.execute(query, (tranid,))
        tid = cursor.fetchone()
        cursor.close()
        return tid[0] if tid else tid

    def insert_exchange(self, taction, tid):
        cursor = self.conn.cursor()
        query = ''' insert into transfert(taction, tid)
                            values (%s, %s) returning tranid;
'''
        cursor.execute(query, (taction, tid))
        tranid = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return tranid
    
    def update_exchange(self, tranid):
        return
    #for debugging, will be unused
    def delete_exchange(self, tid):
        return
    
    #-----For Master Table-----

    # def insert_to_master_table(self, tid):
    #     return



    def is_exchange_receiving_valid(self,tquant, uid, wid, pid):
        cursor = self.conn.cursor()
        query = '''
        select (quantity + %s <= capacity) as valid
        from warehouse natural inner join rack natural inner join parts natural inner join "user"
        where uid =%s and wid = %s and pid = %s;       
        '''
        cursor.execute(query, (tquant, uid, wid, pid))
        result = [row for row in cursor]
        cursor.close()
        return result
    
    
    def is_exchange_sending_valid(self,tquant, uid, wid, pid):
        cursor = self.conn.cursor()
        query = '''
        select (rack.quantity - %s >=0) as valid
        from warehouse natural inner join rack natural inner join parts natural inner join "user"
        where uid =%s and wid = %s and pid = %s;      
        '''
        cursor.execute(query, (tquant, uid, wid, pid))
        result = [row for row in cursor]
        cursor.close()
        return result
    
    
