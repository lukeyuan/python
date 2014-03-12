#!/usr/bin/env python
#-*-coding:utf-8-*-

def priority(n):
    if  n == ')':
        return 4
    elif n == '(':
        return 3
    elif n == '&&' or n == '||':
        return 2
    else:
        return 1

def mongoChange(string):
    '''
    中缀转后缀表达式
    字符串要求：1.必须使用空格分隔 2.如若数字需要当作字符处理，需显示加引号 3.字符串需要加引号
    '''
    listValue = [] #值栈
    listOpr = [] #运算符栈
    operator = ['(', ')', '==', '!=', '>', '<', '>=', '<=', "&&", '||']
    exchangeDict = {"==": "{%r: %s}", "!=": "{%r: {'$ne': %s}}",
            ">": "{%r: {'$gt': %s}}", "<": "{%r: {'$lt': %s}}",
            ">=": "{%r: {'$gte': %s}}", "<=": "{%r: {'$lte': %s}}",
            "&&": "{'$and': [ %s ]}", "||": "{'$or': [ %s ]}",
            "(": "{ %s }"}#转换方式
    listStr = string.split()

    try:
        tag = 0#跳过迭代的标记
        for index,l in enumerate(listStr):
            if l in operator:
                if l == '(':#左括号直接插入
                    listOpr.append(l)
                elif listOpr and priority(l) <= priority(listOpr[-1]):
                    #栈非空+后者优先级比前者低
                    listOpr.append(l)
                elif listOpr:#非空+后者优先级高
                    tempOpr = listOpr.pop()
                    if l == ')': #区域结束，搜寻前一个(
                        while tempOpr != '(':
                            if tempOpr == "&&":
                                while listOpr and listOpr[-1] == "&&": #连续的&
                                    value = listValue.pop()
                                    key = listValue.pop()
                                    listValue.append(','.join([key,value]))
                                    listOpr.pop()#弹出&
                                value = listValue.pop()
                                key = listValue.pop()
                                tmp = exchangeDict[tempOpr] % ','.join([key, value])
                                listValue.append(tmp)
                            elif tempOpr == "||":
                                while listOpr and listOpr[-1] == "||":#连续的|
                                    value = listValue.pop()
                                    key = listValue.pop()
                                    listValue.append(','.join([key,value]))
                                    listOpr.pop()
                                value = listValue.pop()
                                key = listValue.pop()
                                tmp = exchangeDict[tempOpr] % ','.join([key, value])
                                listValue.append(tmp)
                            else:
                                value = listValue.pop()
                                key = listValue.pop()
                                tmp = exchangeDict[tempOpr] % (key, value)
                                listValue.append(tmp)
                            tempOpr = listOpr.pop()
                        #找到(
                        #什么都不用做
                    else:#处理&&,||     > < = != >= <=
                        value = listValue.pop()
                        key = listValue.pop()
                        tmp = exchangeDict[tempOpr] % (key, value)
                        listValue.append(tmp)
                        listOpr.append(l)
                else:
                    print l
                    listOpr.append(l)
            else:
                listValue.append(l)

        while listOpr:#全部读取完毕后操作栈非空
            tempOpr = listOpr.pop()#取出一个操作数
            if tempOpr == "&&":
                while listOpr and listOpr[-1] == "&&": #连续的&
                    value = listValue.pop()
                    key = listValue.pop()
                    listValue.append(','.join([key,value]))
                    listOpr.pop()#弹出&
                value = listValue.pop()
                key = listValue.pop()
                tmp = exchangeDict[tempOpr] % ','.join([key, value])
                listValue.append(tmp)
            elif tempOpr == "||":
                while listOpr and listOpr[-1] == "||":#连续的|
                    value = listValue.pop()
                    key = listValue.pop()
                    listValue.append(','.join([key,value]))
                    listOpr.pop()
                value = listValue.pop()
                key = listValue.pop()
                tmp = exchangeDict[tempOpr] % ','.join([key, value])
                listValue.append(tmp)
            else:
                value = listValue.pop()
                key = listValue.pop()
                tmp = exchangeDict[tempOpr] % (key, value)
                listValue.append(tmp)

        #print listOpr
        #print listValue
        return listValue[0]#返回最后结果
    except Exception,ex:
        return False #Exception,": ",ex

def mysqlChange(string):
    exchangeDict = {"==": "=", "&&": "AND", "||": "OR"}
    listStr = string.split()
    listResult = []
    for l in listStr:
        if l in exchangeDict:
            listResult.append(exchangeDict[l])
        else:
            listResult.append(l)

    return ' '.join(listResult)

if __name__ == '__main__':
    test = '( a != 1 && b >= 2 ) && ( c <= 3 || ( d < 6 && e >= 5 ) ) && ( f <= 6 ) && ( g == 5 && g == 6 ) && ( i == 7 || i == 8 )'
    #test = 'name == "Jack" || name == "Alice"'
    print mongoChange(test)
    print mysqlChange(test)
