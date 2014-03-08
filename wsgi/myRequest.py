#-*-coding:utf-8-*-

import sys
import urllib
import cgi

import sql

reload(sys)
sys.setdefaultencoding("utf-8")

def OpenshiftHttpRequest(environ):
    para = {}
    try:
        if "QUERY_STRING" in environ and environ['QUERY_STRING']:
            string = environ['QUERY_STRING']
            string = string.split("&") #分解Get
            for k in string:
                k = k.split("=")
                para[k[0]] = k[1]
        try:
            bodySize = int(environ['CONTENT_LENGTH'])
        except ValueError:
            bodySize = 0
        body = environ['wsgi.input'].read(bodySize)
        if body:
            postData = parse_qs(body)
            for k,v in d.items():
                para[k] = v

    except Exception,ex:
        return Exception,":",ex
    if para:
        return str(para)
    else:
        return "OK"

def OpenshiftWeChatHttpRequest(environ):
    return "WeChatOK"
