#-*-coding:utf-8-*-

import os
import json

import MySQLdb
import pymongo

from util import mongoChange, mysqlChange

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
                self.dbInstance = mysql_db(self.dbMsg)
            elif self.dbMsg['DB'] == 'mongo':
                self.dbInstance = mongo_db(self.dbMsg)

    def select(self, table, criteria='', fields=[]):
        return self.dbInstance.select(table, criteria, fields)

    def insert(self, table, keys_values):
        return self.dbInstance.insert(table, keys_values)

    def insert_all(self, json_content):
        return self.dbInstance.insert_all(json_content)

    def delete(self, table, criteria=''):
        return self.dbInstance.delete(table, criteria)

    def update(self, table, modify, criteria=''):
        return self.dbInstance.update(table, modify, criteria)

    def create(self, table, items_types, notnull=[], default={}, auto_increment=[], primarykey = None):
        if self.dbInstance:
            return self.dbInstance.create(table, items_types, notnull, default, auto_increment, primarykey)
        else:
            return False

    def drop(self, table):
        return self.dbInstance.drop(table)

    def rawsql(self, sqlstr):
        if self.dbMsg['DB'] == 'mysql':
            return self.dbInstance.rawsql(sqlstr)
        else:
            return False

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
                port=3306,
                charset="utf8")
        self.cur = self.conn.cursor()
        self.conn.select_db(os.environ['OPENSHIFT_APP_NAME'])

    def rawsql(self, sqlstr):
        try:
            self.cur.execute(sqlstr)
            self.conn.commit()
            return True
        except Exception,ex:
            return False

    def create(self, table, items_types, notnull=[], default={}, auto_increment=[], primarykey = None):
        '''
        mysql建立表
        table 表名字
        items_types 字典类型，key=变量， value=变量类型
        notnull 列表类型，为非空的值
        default 字典类型，某变量的默认值
        auto_increment 列表类型，自增的变量
        primarykey 主键
        '''
        createTpl = "CREATE TABLE IF NOT EXISTS %s (%s)"
        para = []
        for k,v in items_types.items():#遍历创建的量
            templi = [k, v]
            if k in notnull:
                templi.append("NOT NULL")
            if k in default.keys():
                if default[k] == 'NULL':
                    templi.append("DEFAULT NULL")
                else:
                    templi.append("DEFAULT %r" % default[k])#字符串自带''
            if k in auto_increment:
                templi.append("AUTO_INCREMENT")
            if primarykey and k == primarykey:
                templi.append("PRIMARY KEY")
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
        if isinstance(keys_values, dict) and keys_values:#空值判断
            tempList = []
            for i in keys_values.values():
                if isinstance(i, unicode):
                    i = str(i)
                if isinstancei(i, str):
                    tempList.append("'%s'" % i )
                else:
                    tempList.append("%r" % i)
            insertTpl = "INSERT INTO %s ( %s ) VALUES ( %s )" % \
                    (table, ','.join(keys_values.keys()),
                            ','.join(tempList))
            try:
                self.cur.execute(insertTpl)
                self.conn.commit()
                return True
            except MySQLdb.Error, e:
                return False
        else:
            return False

    def insert_all(self, json_content):
        try:
            json_content = json.loads(json_content)
        except Exception, e:
            return False
        try:
            table = json_content['table']
            data = json_content['data']
            keys = data.pop(0)
            n = len(keys)
            valueList = ["%s"] * n
            insertTpl = "INSERT INTO %s ( %s ) values " % (table, ','.join(keys)) + ''.join(['( ', ','.join(valueList), ' )'])
            self.cur.executemany(insertTpl, data)
            self.conn.commit()
            return True
        except Exception, ex:
            return False

    def select(self, table, criteria='', fields=[]):
        query = ''
        try:
            if not criteria and not fields:
                query = "SELECT * FROM %s" % table
            elif not criteria and fields:
                query = "SELECT %s FROM %s" % (','.join(fields), table)
            elif criteria and not fields:
                query = "SELECT * FROM %s WHERE %s" % (table, mysqlChange(criteria))
            else:
                query = "SELECT %s FROM %s WHERE %s" % (','.join(fields), table, mysqlChange(criteria))
            tempList = []
            if not fields:
                subquery = "SHOW COLUMNS FROM %s " % table
                self.cur.execute(subquery)
                r = self.cur.fetchone()
                for i in r:
                    tempList.append(i[0])
            else:
                tempList = fields
            try:
                self.cur.execute(query)
                self.conn.commit()
                rr = self.cur.fetchall()
                result = []
                for r in rr:
                    tempDic = {}
                    for i, t in enumerate(tempList):
                        tempDic[t] = r[i]
                    result.append(tempDic)
                return tuple(result)
            except MySQLdb.Error, e:
                return False
        except Exception, ex:
            return False

    def drop(self, table):
        dropTpl = "DROP TABLE %s" % table
        try:
            self.cur.execute(dropTpl)
            self.conn.commit()
            return True
        except MySQLdb.Error, e:
            return False

    def delete(self, table, criteria):
        delTpl = ""
        try:
            if criteria:
                delTpl = "DELETE FROM %s WHERE %s " % (table, mysqlChange(criteria))
            else:
                delTpl = "DELETE FROM %s " % table
            try:
                self.cur.execute(delTpl)
                self.conn.commit()
                return True
            except MySQLdb.Error, e:
                return False
        except Exception,ex:
            return False

    def update(self, table, modify, criteria):
        updateTpl = ""
        tmpList = []
        for k,v in modify.items():
            if isinstance(v, unicode):
                v = str(v)
            if isinstance(v, str):
                tmpList.append("%s='%s'" %(k,v))
            else:
                tmpList.append("%s=%r" %(k,v))
        try:
            if criteria:
                updateTpl = "UPDATE %s SET %s WHERE %s" % (table, ','.join(tmpList), mysqlChange(criteria))
            else:
                updateTpl = "UPDATE %s SET %s" % (table, ','.join(tmpList))
            try:
                self.cur.execute(updateTpl)
                self.conn.commit()
                return True
            except MySQLdb.Error, e:
                return False
        except Exception,ex :
            return False

    def __del__(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

class mongo_db:
    conn = ''
    db = ''
    def __init__(self, dbMsg):
        self.conn = pymongo.Connection(dbMsg['OPENSHIFT_MONGODB_DB_HOST'], 27017)
        self.db = self.conn[os.environ['OPENSHIFT_APP_NAME']]
        self.db.authenticate(dbMsg['OPENSHIFT_MONGODB_DB_USERNAME'], dbMsg['OPENSHIFT_MONGODB_DB_PASSWORD'])
    
    def create(self, table, items_types, notnull=[], default={}, auto_increment=[], privatekey = None):
        #mongo不需要创建表
        return True

    def insert(self, table, keys_values):
        try:
            self.db[table].insert(keys_values)
            return True
        except Exception,ex:
            return False

    def insert_all(self, json_content):
        try:
            json_content = json.loads(json_content)
        except Exception,ex:
            return False
        table = json_content['table']
        data = json_content['data']
        keys = data.pop(0)
        insertList = []
        for l in data:
            tempDict = {}
            for k,v in zip(keys,l):
                tempDict[k] = v
            insertList.append(tempDict)
        try:
            self.db[table].insert(insertList)
            return True
        except Exception,ex:
            return False

    def select(self, table, criteria="", fields=[]):
        if not criteria:
            cur = self.db[table].find()
            tempList = []
            for r in cur:
                tempList.append(r)
            return tuple(tempList)
        else:
            condition = mongoChange(criteria)
            if condition:
                try:
                    cur =  self.db[table].find(json.loads(condition))
                    tempList = []
                    for r in cur:
                        tempList.append(r)
                    return tuple(tempList)
                except Exception,ex:
                    return False
            else:
                return False

    def drop(self, table):
        try:
            self.db[table].drop()
            return True
        except Exception,ex:
            return False

    def delete(self, table, criteria=""):
        if not criteria:
            self.db[table].remove()
            return True
        else:
            condition = mongoChange(criteria)
            if condition:
                try:
                    self.db[table].remove(json.loads(condition))
                    return True
                except Exception,ex:
                    return False
            else:
                return False

    def update(self, table, modify, criteria=""):
        tempDict = {}
        for k,v in modify:
            tempDict[k] = v
        if criteria:
            condition = mongoChange(criteria)
            if condition:
                try:
                    self.db[table].update(json.loads(condition), {"set": tempDict}, multi = True)
                    return True
                except Exception,ex:
                    return False
            else:
                return False
        else:
            try:
                self.db[table].update({}, {"$set": tempDict}, multi = True)
                return True
            except Exception,ex:
                return False

    def __del__(self):
        self.db.logout()
