#-*-coding:utf-8-*-

import os
import json
import re
import sql
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class stateMachine:
    
    def __init__(self):
        '''
        ecnt 图的边数
        head 每个结点邻接表的链头
        nxt 下一条邻接边的边号
        weight 边的权值
        db 数据库实例
        '''
        self.MAX_STATE = 1000
        self.ecnt = 0
        self.edgeTo = {}
        self.head = {}
        self.nxt = {}
        self.weight = {}
        self.db = sql.db()
        self.table = 'user_state'
        items = {'id': 'int(11)', 'username': 'varchar(1000)', 
                'state': 'varchar(1000)'}
        notnull = ['id', 'username']
        default = {'state': 'NULL'}
        autoIncrement = ['id']
        primarykey = 'id'
        self.db.create(self.table, items, notnull, default
                , autoIncrement, primarykey)
        
    def add_edge(self, e_from, e_to, pattern_string):
        '''
        邻接表加边
        e_from 边的起点
        e_to 边的终点
        pattern_string 正则表达式
        '''
        if e_from not in self.head:
            self.head[e_from] = 'null'
        self.edgeTo[self.ecnt] = e_to
        self.weight[self.ecnt] = pattern_string
        self.nxt[self.ecnt] = self.head[e_from]
        self.head[e_from] = self.ecnt
        self.ecnt += 1

    def can_go(self, user, target_state, select):
        '''
        判断指定用户是否能通过select,到达target_state
        '''
        user = str(user)
        curState = self.get_state(user)
        if curState not in self.head:
            self.head[curState] = 'null'
        e = self.head[curState]
        while e != 'null':
            if self.edgeTo[e] == target_state:
                rightSelect = self.weight[e]
                selectPattern = re.compile(rightSelect)
                if selectPattern.match(select):
                    return True
            e = self.nxt[e]
        return False

    def go_with(self, user, select):
        '''
        用户能否根据选择到达下一状态
        '''
        user = str(user)
        curState = self.get_state(user)
        if curState not in self.head:
            self.head[curState] = 'null'
        e = self.head[curState]
        while e != 'null':
            rightSelect = self.weight[e]
            # use unicode to match
            if not isinstance(rightSelect, unicode):
                selectPattern = re.compile(rightSelect.decode('utf-8'))
            else:
                selectPattern = re.compile(rightSelect)
            matchOK = False
            if not isinstance(select, unicode):
                matchOK = selectPattern.match(select.decode('utf-8'))
            else:
                matchOK = selectPattern.match(select)
            if matchOK:
                return self.edgeTo[e]
            e = self.nxt[e]
        return '00'

    def get_state(self, user):
        '''
        获取用户状态
        '''
        user = str(user)
        result = self.db.select(self.table, "username == '%s'" % user, ['state'])
        if not result:#用户不存在
            self.create_userstate(user)
            return 'null'
        else:
            r = result[0]
            userJson = r['state']
            userJsonContent = json.loads(userJson)
            return userJsonContent['state']

    def get_select(self, user):
        '''
        获取用户的选择（当前）
        '''
        user = str(user)
        result = self.db.select(self.table, "username == '%s'" % user, ['state'])
        if not result:#用户不存在
            self.create_userstate(user)
            return 'null'
        else:
            r = result[0]
            userJson = r['state']
            userJsonContent = json.loads(userJson)
            return userJsonContent['select']
    
    def reset_userstate(self, user):
        userJson = json.dumps({"state": "null", "select": "null", "fa": {}})
        result = self.db.update(self.table, {"state": userJson}, "username = '%s' " % user)
        return result

    def save_state(self, user, state, select):
        '''
        保存用户状态
        '''
        user = str(user)
        result = self.db.select(self.table, "username == '%s'" % user, ['state'])
        if not result:
            return self.create_userstate(user)
        else:
            r = result[0]
            userJson = r['state']
            userJsonContent = json.loads(userJson)
            if len(userJson) > 990:
                userJsonContent['fa']['fa'] = {} #清空后
            userJson = json.dumps({"state": state, "select": select, "fa": userJsonContent})
            result = self.db.update(self.table, {"state": userJson}, "username == '%s'" % user)
            return result

    def rollback(self, user):
        '''
        回滚用户到上一状态
        '''
        user = str(user)
        result = self.db.select(self.table, "username = '%s'" % user, ['state'])
        if not result:
            return self.create_userstate(user)
        else:
            r = result[0]
            userJson = r['state']
            userJsonContent = json.loads(userJson)
            if userJsonContent['fa'] == {} :
                return False
            userJson = json.dumps({"state": userJsonContent['fa']['state'],
                "select": userJsonContent['fa']['select'],
                "fa": userJsonContent['fa']['fa'] })
            result = self.db.update(self.table, {"state": userJson}, "username == '%s'" % user)
            return result

    def create_userstate(self, user):
        user = str(user)
        userJson = json.dumps({"state": "null", "select": "null", "fa": {}})
        dic = {"username": user, "state": userJson}
        r = self.db.insert(self.table, dic)
        if r:
            return True
        else:
            return False

    def debug(self, s):
        with open(os.environ['OPENSHIFT_REPO_DIR']+'wsgi/testSM', 'ab') as f:
            f.write(str(s))
