
import pymysql as mysql 
from GetEmotions import *
import os
import json
from Spider import Spider 
'''
此文件用于错误测试，因为空间说说量大，内容较多，且很乱，
很多bug错误都不明白怎么回事，因此可以通过此文件对某个链接或文本进行单独测试
'''
db_url = 'localhost'
db_username = 'root'
db_password = 'root'
db_base = 'qq'
config = {
          'host':'127.0.0.1',
          'port':3306,
          'user':'root',
          'password':'root',
          'db':'qq',
          'charset':'utf8mb4'   
          }

def get_connection():
    try:
        connection = mysql.connect(**config)
        return connection 
    except:
        print('【Error】数据库连接错误')
        exit(1)


def save_cookies(cookies):
    if cookies is not None:
        try:
            file = open('./cookies','w+',encoding='utf-8')
            file.write(cookies)
            print('【Success】cookie写入成功\n【cookie】:'+str(cookies))
        except Exception as e:
            print('【Error】cookie写入错误:'+str(e))
        finally:
            file.close()
    else:
        print('【Warning】cookie无效，为None')
        exit(0)

def read_cookies():
    if os.path.exists('./cookies'):
        try:
            file = open('./cookies','r+',encoding='utf-8')
            cookie = file.read()
            if cookie is not None:
                return cookie
            else:
                print('【Warning】cookie读取错误，为None')
        except Exception as e:
            print('【Error】cookie读出错误:'+str(e))
        finally:
            file.close()
    else:
        print('【Warning】找不到cookie文件')
        exit(0)

def get_cookie(dirPath):
    #dirPath = 'D:\\liufanWorkspace\\qqzone_spider\\userinfo.ini'
    spider = Spider(dirPath)
    spider.login()
    save_cookies(spider.cookies)

def emoj_test():

    con = get_connection()
    emotion_tb_keys = {'id':-2,'name':0,'uin':0,'content':-1,
    'createTime':0,'created_time':0,'editMask':0,
    'tid':0,'commentlist':-1,'type':0,'pic':-1,'source_name':0,'cmtnum':1}
    if not table_is_exist(con,"emotion_tb_test"):
        create_table_from_dict(con,"emotion_tb_test",emotion_tb_keys)
    cursor = con.cursor()
    
    test_data = get_test_data(emotion_tb_keys)
    print(test_data)
    test_data['id'] = 'null'
    test_data['commentlist'] = "[{'create_time': 1539058403, 'reply_num': 0, 'tid': 1, 't2_source': 1, 'createTime': '2018年10月09日', 'createTime2': '2018-10-09 12:13:23', 'source_name': '', 'uin': 1140373223, 'abledel': 0, 't2_subtype': 2, 'source_url': '', 'stored_extend_info': [{'k': 'diy_font_id', 'v': '16164'}, {'k': 'diy_font_type', 'v': '2'}, {'k': 'diy_font_url', 'v': 'https://qzonestyle.gtimg.cn/qzone/space_item/material/CustomFont/org/4/16164/TTTGB-Medium.zip'}], 'IsPasswordLuckyMoneyCmtRight': '', 'name': '晨妹🦄', 'content': '哈哈哈', 'private': 0, 't2_termtype': 2}, {'create_time': 1539060591, 'pic': [{'s_height': 0, 'b_height': 0, 's_width': 0, 'who': 1, 'b_width': 0, 's_url': 'http://b218.photo.store.qq.com/psb?/V10r61W42vvkEv/tx5QUHq*GvCbbKQO7rLSPsfM34qL7sOFw6G6qjmtNKQ!/b/dNoAAAAAAAAA&bo=ZAIRAgAAAAAREFI!', 'hd_height': 0, 'hd_width': 0, 'hd_url': 'http://b218.photo.store.qq.com/psb?/V10r61W42vvkEv/tx5QUHq*GvCbbKQO7rLSPsfM34qL7sOFw6G6qjmtNKQ!/b/dNoAAAAAAAAA&bo=ZAIRAgAAAAAREFI!', 'b_url': 'http://b218.photo.store.qq.com/psb?/V10r61W42vvkEv/tx5QUHq*GvCbbKQO7rLSPsfM34qL7sOFw6G6qjmtNKQ!/b/dNoAAAAAAAAA&bo=ZAIRAgAAAAAREFI!', 'o_url': 'http://b218.photo.store.qq.com/psb?/V10r61W42vvkEv/tx5QUHq*GvCbbKQO7rLSPsfM34qL7sOFw6G6qjmtNKQ!/b/dNoAAAAAAAAA&bo=ZAIRAgAAAAAREFI!'}], 'tid': 2, 'rich_info': [{'type': 1, 'who': 1, 'burl': 'http://b218.photo.store.qq.com/psb?/V10r61W42vvkEv/tx5QUHq*GvCbbKQO7rLSPsfM34qL7sOFw6G6qjmtNKQ!/b/dNoAAAAAAAAA&bo=ZAIRAgAAAAAREFI!'}], 'createTime': '2018年10月09日', 'createTime2': '2018-10-09 12:49:51', 'source_name': '', 'uin': 649531016, 'content': '', 'abledel': 0, 't2_subtype': 2, 'reply_num': 0, 'source_url': '', 't2_source': 1, 'IsPasswordLuckyMoneyCmtRight': '', 'name': '\u202d\u202d \u202d\u202d', 'pictotal': 1, 'private': 0, 't2_termtype': 2}]"
    insert_emotion(con,"emotion_tb_test",test_data)

def get_test_data(key_dict):
    for key,values in key_dict.items():           
        if values != 1:
            values = 'test'
    return key_dict
            
if __name__ == '__main__':
    # dirPath = 'D:\\liufanWorkspace\\qqzone_spider\\userinfo.ini'
    # #cookie = read_cookies()
    # spider = Spider(dirPath)
    # spider.login()
    # uin = 214704958
    # pos = 0
    # url = get_emotion_url(spider,uin,pos)
    # page = spider.get_url_response(url)
    # get_template_data_from_page(spider.db,page)
    emoj_test()


