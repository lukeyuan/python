#-*-coding:utf-8-*-

import os

BASE_PATH = os.environ['OPENSHIFT_REPO_DIR'] + 'wsgi/dbinfo'

class db():

    dbMsg = {}

    __init__(self):
        if os.path.exist(BASE_PATH):
            with open(BASE_PATH, "rb") as info:
                data = info.readlines()
                for f in data:
                    f = f.split()
                    self.dbMsg[f[0]] = f[1]

    def showDBInfo(self):
        if self.dbMsg:
            return self.dbMsg
        else:
            return 0
