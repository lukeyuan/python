#-*-coding:utf-8-*-

import os
import json

import MySQLdb
import pymongo

BASE_PATH = os.environ['OPENSHIFT_REPO_DIR'] + 'wsgi/dbinfo'

class db():

    dbMsg = {}
    dbInstance = ""

    def __init__(self):
        if os.path.exists(BASE_PATH):
            with open(BASE_PATH, "rb") as info:
                data = info.readlines()
                for f in data:
                    f = f.split()
                    self.dbMsg[f[0]] = f[1]
            if self.dbMsg['DB'] == 'mysql':
                self.dbInstance = mysql_db()
            elif self.dbMsg['DB'] == 'mongodb':
                self.dbInstance = mongo_db()

    def select(self, table, criteria={}, fields={}):
        pass

    def insert(self, table, keys_values):
        pass

    def insert_all(self, json_content):
        pass

    def delete(self, table, criteria):
        pass

    def update(self, table, modify, criteria):
        pass

    def create(self, table, items_types, notnull=[], default={}, auto_increment=[], privatekey = None):
        if dbInstance:
            return dbInstance.create(table, items_types, notnull, default, auto_increment, privatekey)
        else:
            return False

    def drop(self, table):
        pass


    def showDBInfo(self):
        if self.dbMsg:
            return self.dbMsg
        else:
            return 0

class mysql_db:
    conn = ''
    cur = ''
    def __init__(self,dbMsg):
        self.conn = MySQLdb.connect(host=dbMsg['OPENSHIFT_MYSQL_DB_HOST'],
                user=dbMsg['OPENSHIFT_MYSQL_DB_USERNAME'],
                passwd=dbMsg['OPENSHIFT_MYSQL_DB_PASSWORD'],
                port=3306)
        self.cur = self.conn.cursor()
        self.conn.select_db(os.environ['OPENSHIFT_APP_NAME'])

    def create(self, table, items_types, notnull=[], default={}, auto_increment=[], privatekey = None):
        '''
        mysql建立表
        table 表名字
        items_types 字典类型，key=变量， value=变量类型
        notnull 列表类型，为非空的值
        default 字典类型，某变量的默认值
        auto_increment 列表类型，自增的变量
        privatekey 主键
        '''
        createTpl = "CREATE TABLE %s (%s)"
        para = []
        for k,v in items_types:#遍历创建的量
            templi = [k, v]
            if k in notnull:
                templi.append("NOT NULL")
            if k in default.keys():
                templi.append("DEFAULT %r" % default[k])#字符串自带''
            if k in auto_increment:
                templi.append("AUTO_INCREMENT")
            if privatekey and k == privatekey:
                templi.append("PRIVATE KEY")
            para.append(' '.join(templi))#以一个空格分隔上述变量，存入para
        string = ','.join(para) #组装为创建条件
        string = createTpl % (table, string)#完整的sql语句
        try:
            self.cur.execute(string)
            self.conn.commit()
            return True
        except MySQLdb.Error, e:
            return False #"Mysql Error %d: %s" % (e.args[0], e.args[1])
    
    def insert(self, table, keys_values):
        '''
        mysql插入数据
        keys_values 字典类型，变量：值 对
        '''
        if isinstance(keys_values, {}) and keys_values:#空值判断
            insertTpl = "INSERT INTO %s ( %s ) VALUES ( %s )" % \
                    (','.join(keys_values.keys()),
                            ','.join(keys_values.values()))
            try:
                self.cur.execute(insertTpl)
                self.conn.commit()
                return True
            except MySQLdb.Error, e:
                return False
        else:
            return False

    def insert_all(json_content):
        try:
            json_content = json.loads(json_content)
        except Exception, e:
            return False
        try:
            table = json_content['table']
            data = json_content['data']
            keys = data.pop(0)
            insertTpl = "INSERT INTO %s ( %s ) values " % (table, ','.join(keys)) + " ( %s ) "
            self.cur.executemany(insertTpl, data)
            self.conn.commit()
            return True
        except KeyError, IndexError, TypeError:
            return False
        pass

    def select(self, table, criteria={}, fields={}):
        query = ''
        if criteria:
            query = "SELECT * FROM %s" % table
        else:
            pass
        pass

    def drop(self, table):
        dropTpl = "DROP TABLE %s" % table
        try:
            self.cur.execute(dropTpl)
            self.conn.commit()
            return True
        except MySQLdb, e:
            return False

    def delete(self, criteria):
        pass

    def update(self, table, modify, criteria):
        pass

    def __del__(self):
        if cur:
            cur.close()
        if conn:
            conn.close()

class mongo_db:
    def __init__():
        pass
    pass
