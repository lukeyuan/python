#-*-coding:utf-8-*-

import sys
import urllib
import cgi
import json
import xml.dom.minidom
import hashlib
import time

import sql

try:
    import logic
except ImportError:
    pass

reload(sys)
sys.setdefaultencoding("utf-8")

def openshiftHttpRequest(environ):
    para = {}
    para = _getGETPara(environ, para)
    try:
        try:
            bodySize = int(environ['CONTENT_LENGTH'])
        except Exception, ex:
            bodySize = 0
        if bodySize:
            fields = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=1)
            for index in fields:
                if fields[index].filename == None: #POST数据变量
                    para[fields[index].name] = fields[index].value
                elif fields[index].filename: #POST数据文件
                    para[fields[index].name] = {'name': fields[index].filename, 'value': fields[index].value}
         
    except Exception,ex:
        return Exception,":",ex
    if 'logic' in globals():
        if "method" in para:
            method = para['method']
            if callable(getattr(logic.logic(), method)):
                function = getattr(logic.logic(), method)
                result = function(para)
                try:
                    ret = json.dumps(result['AppText'])
                    return ret
                except Exception,ex:
                    ret = str(result['AppText'])
                    return ret
                    #return "JSON format error"
    #if para:
    #    return str(para)
    #else:
    #    return "no logic , no para"

def openshiftWeChatHttpRequest(environ):
    TOKEN = "weixin"
    para = {}
    if environ['REQUEST_METHOD'] == "GET":#微信认证
        para = _getGETPara(environ, para)
        try:
            if para:
                signature = para['signature']
                timestamp = para['timestamp']
                nonce = para['nonce']
                token = TOKEN
                tmpArr = [token, timestamp, nonce]
                tmpArr.sort()
                tmpStr = ''.join(tmpArr)
                m = hashlib.sha1()
                m.update(tmpStr)
                if m.hexdigest() == signature:
                    return para['echostr']
                else:
                    return False
            else:
                return False
        except Exception, ex:
            return False
    else:
        try:
            field = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=1)
            if field.value:
                doc = xml.dom.minidom.parseString(field.value)
                root = doc.documentElement
                for node in root.childNodes:#解释xml树
                    if node.nodeType == node.ELEMENT_NODE:
                        for n in node.childNodes:
                            if n.nodeType in (n.TEXT_NODE, n.CDATA_SECTION_NODE):
                                para[node.nodeName] = n.data
            if 'logic' in globals():
                if callable(getattr(logic.logic(), "all")):
                    function = getattr(logic.logic(), "all")
                    result = function(para)
                    if result['MsgType'] == 'text':
                        textTpl = '''<?xml version='1.0' encoding='utf-8' ?>
                        <xml>
                            <ToUserName>%s</ToUserName>
                            <FromUserName>%s</FromUserName>
                            <CreateTime>%s</CreateTime>
                            <MsgType>%s</MsgType>
                            <Content>%s</Content>
                        </xml>
                        '''
                        resultStr = textTpl % (para["FromUserName"], para['ToUserName'], time.time(), result["MsgType"], result["Content"])
                        return resultStr
                    elif result['MsgType'] == 'news':
                        newsTpl = '''<?xml version='1.0' encoding='utf-8' ?>
                        <xml>
                            <ToUserName>%s</ToUserName>
                            <FromUserName>%s</FromUserName>
                            <CreateTime>%s</CreateTime>
                            <MsgType>%s</MsgType>
                            <ArticleCount>%s<ArticleCount>
                            <Articles>
                                %s
                            </Articles>
                        </xml>
                        '''
                        articleCount = int(result['ArticleCount'])
                        tpl = '''<item>
                            <Title>%s</Title>
                            <Description>%s</Description>
                            <PicUrl>%s</PicUrl>
                        </item>
                        '''
                        tplList = []
                        for i in range(1, articleCount+1):
                            pass
            else:
                return "no logic in wx"

        except Exception, ex:
            return ' '.join(["错误：",str(Exception),":",str(ex)])
    return "WeChatOK"

def insertData(environ):
    fields = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=1)
    if fields.value:
        value = fields.value
        db = sql.db()
        result = db.insert_all(value)
        if result:
            return True#"插入成功"
        else:
            return "插入失败"
    else:
        return "没有数据"

def createTable(environ):
    fields = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=1)
    try:
        createSQL = fields['createSQL'].value
        db = sql.db()
        r = db.rawsql(createSQL)
        if r:
            return True
        else:
            return False
    except Exception,ex:
        return False

def _getGETPara(environ, para):
    try:
        if "QUERY_STRING" in environ and environ['QUERY_STRING']:
            string = environ['QUERY_STRING']
            string = string.split("&") #分解Get
            for k in string:
                k = k.split("=")
                para[k[0]] = k[1]
            return para
        else:
            return {}
    except Exception, ex:
        return {}

