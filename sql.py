import pymysql
import config as cfg
import config_msg 
import ai 

sql = None

def con()->pymysql.connect:
    try:
        sql = pymysql.connect(
                host=cfg.sql_host,
                port=3306,
                user=cfg.sql_user,
                password=cfg.sql_pass,
                database=cfg.sql_database,
                cursorclass=pymysql.cursors.DictCursor
            )
        return(sql) 
    except Exception as ex:
        print(ex)

sql = con()

class Promo_code:
    def __init__(self, text):
        self.text = text
        self.activ = None
        self.max_activ = None

    def in_database(self):
        with sql.cursor() as cursor:
            query = 'SELECT * FROM `promo` WHERE code =\''+self.text+'\';'
            cursor.execute(query)
            out= cursor.fetchall()
            if out == ():
                return False
            self.activ = out[0]['activ']
            self.max_activ = out[0]['max_activ']
            return True
    
    def activation(self, userid):
        if not self.in_database():
            return ('Промокода не существует(')
        if self.activ >= self.max_activ:
            return ('Превышено количество активаций')
        with sql.cursor() as cursor:
            query = 'UPDATE `promo` SET activ=activ+1 WHERE code=\''+self.text+'\';'
            cursor.execute(query)
            sql.commit()
        with sql.cursor() as cursor:
            query = 'UPDATE `user` SET premium=TRUE WHERE id='+userid+';'
            cursor.execute(query)
            sql.commit()
        return('Премиум активирован❤')
        
class Promt:
    def __init__(self, id):
        self.id = str(id)
        self.name = None
        self.user_id = None
        self.system = None

    def connect(self):
        with sql.cursor() as cursor:
            query = 'SELECT * FROM `promt` WHERE id ='+self.id+';'
            cursor.execute(query)
            out= cursor.fetchall()
            if out == ():
                return False
            self.name = out[0]['name']
            self.user_id = out[0]['user_id']
            self.system = out[0]['system_promt']
            return True
        
    def set_name(self, message):
        with sql.cursor() as cursor:
            query = 'UPDATE `promt` SET name=\''+message.text+'\' WHERE id='+self.id+';'
            cursor.execute(query)
            sql.commit()

class User:
    def  __init__(self, message) -> None:
        self.id = str(message.from_user.id)
        self.last_date = message.date
        self.last_date_sql = None
        self.premium = False
        self.promt = 0

    def in_database(self):
        with sql.cursor() as cursor:
            query = 'SELECT * FROM `user` WHERE id ='+self.id+';'
            cursor.execute(query)
            out= cursor.fetchall()
            if out == ():
                return False
            self.last_date_sql = out[0]['last_date']
            self.premium = out[0]['premium']
            self.promt = out[0]['activ_promt']
            return True
    
    def create_user(self):
        self.in_database()
        if not self.in_database():
            with sql.cursor() as cursor:
                query = 'INSERT INTO `user` (id, last_date) VALUES ('+self.id+', '+str(self.last_date)+');'
                cursor.execute(query)
                sql.commit()
    
    def set_last_time(self):
        with sql.cursor() as cursor:
            query = 'UPDATE `user` SET last_date='+str(self.last_date)+' WHERE id='+self.id+';'
            cursor.execute(query)
            sql.commit()

    def promo(self, promo):
        self.create_user()
        if self.premium:
            return 'У вас уже есть 💎премиум'
        promo_code = Promo_code(promo)
        return promo_code.activation(self.id)
    
    def promt_list(self):
        self.create_user()
        with sql.cursor() as cursor:
            query = 'SELECT id, name FROM `promt` WHERE user_id = '+self.id+' OR id = 0;'
            cursor.execute(query)
            out= cursor.fetchall()
            return out

    def set_promt(self, name):
        self.create_user()
        set_id = None
        with sql.cursor() as cursor:
            query = 'SELECT id FROM `promt` WHERE (user_id = '+self.id+' OR id = 0) AND name = \''+name+'\';'
            cursor.execute(query)
            out= cursor.fetchall()
            set_id = out[0]['id']
        with sql.cursor() as cursor:
            query = 'UPDATE `user` SET activ_promt='+str(set_id)+' WHERE id='+self.id+';'
            cursor.execute(query)
            sql.commit()

    def del_promt(self, name):
        with sql.cursor() as cursor:
            query = 'SELECT id FROM `promt` WHERE user_id = '+self.id+' AND name = \''+name+'\';'
            cursor.execute(query)
            out= cursor.fetchall()
            set_id = out[0]['id']
        with sql.cursor() as cursor:
            query = 'DELETE FROM `promt` WHERE id='+str(set_id)+';'
            cursor.execute(query)
            sql.commit()

    def create_promt(self, text):
        self.create_user()
        with sql.cursor() as cursor:
            query = 'INSERT INTO `promt` (name, user_id, system_promt) VALUES (\'New promt\','+self.id+', \''+text+'\');'
            cursor.execute(query)
            sql.commit()
        with sql.cursor() as cursor:
            query = 'SELECT id FROM `promt` WHERE name =\'New promt\' AND user_id = '+self.id+' AND system_promt = \''+text+'\';'
            cursor.execute(query)
            out= cursor.fetchall()
            return Promt(out[0]['id'])

    def gpt_query(self, text, memory=None):
        self.create_user()
        out_time = config_msg.msg_time
        if self.premium:
            out_time = config_msg.msg_time_premium
        if self.last_date_sql != None and (self.last_date-self.last_date_sql) <= out_time:
            if self.premium:
                return(config_msg.out_time_msg_prime)
            return(config_msg.out_time_msg)
        if self.last_date_sql == None:
            self.create_user()
        self.set_last_time()

        out = None
        if memory ==None:
            if self.promt == 0:
                out = ai.query(text)
            else: 
                promt = Promt(self.promt)
                promt.connect()
                out = ai.query(text, instruct=promt.system)
        else:
            out = ai.query(text, memory_save=memory)
        
        return out