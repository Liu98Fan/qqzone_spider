# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import re
import json
import time
#判断表是否存在
def table_is_exist(con,table_name):
    sql = "show tables;"
    con = con.cursor()
    con.execute(sql)
    tables = [con.fetchall()]
    table_list = re.findall('(\'.*?\')',str(tables))
    table_list = [re.sub("'",'',each) for each in table_list]
    if table_name in table_list:
        return True
    else:
        return False
    
def create_table(con,table_name,key_list):
    sql = "CREATE TABLE `"+table_name+"` (`id` int(11) NOT NULL AUTO_INCREMENT,"
    for key in key_list:
        sql += "`"+key+"`"+" varchar(255) NOT NULL,"
    sql += "PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    print('[processing]create_table拼接sql为:'+sql)
    try:
        con.cursor().execute(sql)
        print('[Success]建表成功')
    except Exception as e:
        print('[Error]建表失败'+str(e))
        exit(1)

def create_table_from_dict(con,table_name,key_dict):
    sql = "CREATE TABLE `"+table_name+"` (`id` int(11) NOT NULL AUTO_INCREMENT,"
    for key,value in key_dict.items():
        if key in['pic','commentlist']:
            sql += "`"+key+"`"+" text DEFAULT NULL,"
            continue
        if key in ['editMask','type']:
            sql += "`"+key+"`"+" varchar(255) DEFAULT NULL,"
            continue
        if value == -1:
            sql += "`"+key+"`"+" text NOT NULL,"
        if value == 1:
            sql += "`"+key+"`"+" int(11) NOT NULL,"
        if value == 0:
            sql += "`"+key+"`"+" varchar(255) NOT NULL,"
    sql += "PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    print('[processing]create_table拼接sql为:'+sql)
    try:
        con.cursor().execute(sql)
        print('[Success]建表成功')
    except Exception as e:
        print('[Error]建表失败'+str(e))
        exit(1)

def insert_friend(con,table_name,item):
    
    sql = "insert into "+table_name +"(id,"+ list_as_param(list(item.keys()))[1:]+"values(null,"+list_as_param_hascode(list(item.values()))[1:]+";";
    print('[processing]insert_friend拼接sql为:'+sql)
    execute_sql(con,sql,item)

def insert_emotion(con,table_name,item):
    sql = "insert into "+table_name + list_as_param(list(item.keys()))+"values"+list_as_param_hascode(list(item.values()))+";";
    print('[processing]insert_emotion拼接sql为:'+sql)
    execute_sql(con,sql,item)

def insert_emotion_total(con,table_name,item):
    sql = "insert into "+table_name + list_as_param(list(item.keys()))+"values"+list_as_param_hascode(list(item.values()))+";";
    print('[processing]insert_emotion_total拼接sql为:'+sql)
    execute_sql(con,sql,item)

def execute_sql(con, sql,item):
    try:
        con.cursor().execute(sql)
        con.commit()
        print('[Success]执行成功')
    except Exception as e:
        print('[Error]记录插入失败'+str(e))
        er = open('./error_'+str(item['uin'] if item['uin'] is not None else 'unkown')+str(int(time.time()))+'_emotion.json','a+',encoding='utf-8')
        json.dump(item,er,ensure_ascii=False)
        print('[Logging]错误说说记录成功')

def list_as_param_hascode(list):
    param = "("
    for index,p in enumerate(list):
        if p != 'null':
            param += "\""+str(p)+"\""
        else:
            param += str(p)
        if index != len(list)-1:
            param +=","
    return param+")"

def list_as_param(list):
    param = "("
    for index,p in enumerate(list):
        param +="`"+ str(p)+"`"
        if index != len(list)-1:
            param +=","
    return param+")"

def get_friend_number(con,master):
    sql = "select uin from all_friends_score_tb where master="+str(master)
    con = con.cursor()
    try:
        con.execute(sql)
        result = con.fetchall()
        return list(result)
    except Exception as e:
        print('[Error]获取数据库好友uin失败'+str(e))
        exit(1)
        
if __name__ =="__main__":
    list = ['uin', 'name', 'index', 'chang_pos', 'score', 'special_flag', 'uncare_flag', 'img']
    param = ''
    for j,p in enumerate(list):
        param += str(p)
        if j != len(list)-1:
            param +=","
    print( param+")")