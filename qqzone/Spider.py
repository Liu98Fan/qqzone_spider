# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import configparser
from selenium import webdriver
import requests
import logging
import time
import os
import re
import pymysql as mysql

class Spider(object):
    

    def __init__(self, dir):
        #读取配置文件
        config = configparser.ConfigParser(allow_no_value=False)
        config.read(dir)
        self.__config = config
        #读取账号和密码
        self.__username = config.get('my_info', 'number')
        self.__password = config.get('my_info', 'password')
        print('读取的账号信息为:number=' + self.__username)
        #初始化浏览器模拟器
        self.web = webdriver.Chrome()
        self.web.get('https://qzone.qq.com/')
        self.req = requests

        self.headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'Cookie': '',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
            ,'kepp_alive':'False'
        }
        print('[success]初始化webdriver.chrom成功！')

        self.init_db()

        self.log_file = open('./errorlog.txt','w+',encoding='utf-8')
        self.log_file.write('-----------------------'+str(time.asctime( time.localtime(time.time())))+'----------------')
    #初始化数据库连接
    def init_db(self):
        try:
            self.__db_url = self.__config.get('db_info','url')
            self.__db_user = self.__config.get('db_info','username')
            self.__db_password = self.__config.get('db_info','password')
            self.__db_name = self.__config.get('db_info','name')
        except:
            print('[Error]数据库信息读取错误，请检查配置文件是否配置正确！')
            exit(1)
        #进行数据库的链接
        try:
            self.db = mysql.connect(self.__db_url,self.__db_user,self.__db_password,self.__db_name)
            print('[success]数据库连接成功')
        except:
            print('[Error]数据库连接错误')
            exit(1)

    def __del__(self):
        try:
            self.db.close()
            self.log_file.close()
            self.web.close()
        except AttributeError as e:
            print(e)

    def close(self):
        try:
            self.db.close()
            self.log_file.close()
            self.web.close()
        except AttributeError as e:
            print(e)

    
    def login(self,**kwargs):
        if 'cookie' not in list(kwargs.keys()):
            self.web.switch_to_frame('login_frame')
            # 跳转到账号密码登陆界面
            log = self.web.find_element_by_id("switcher_plogin")
            log.click()
            time.sleep(1)
            # 填充账号密码
            username = self.web.find_element_by_id('u')
            username.send_keys(self.__username)
            ps = self.web.find_element_by_id('p')
            ps.send_keys(self.__password)
            # 登陆按钮
            btn = self.web.find_element_by_id('login_button')
            time.sleep(1)
            btn.click()
            time.sleep(2)
            self.web.get('https://user.qzone.qq.com/{}'.format(self.__username))
            c = self.web.get_cookies()
            cookie = ''
            for elem in c:
                cookie += elem["name"] + "=" + elem["value"] + ";"
            self.cookies = cookie
            self.req.session().kepp_alive = False
            
        else:
            self.cookies = kwargs['cookie']
        #获取g_tk参数，这个参数很重要
        self.get_g_tk()
        self.headers['Cookie'] = self.cookies
        #print('登陆成功，headers = ' + str(self.headers))
        self.get_qzone_token()
        print('[success]登陆成功')
        self.is_login = True
        self.web.quit()
    
    def get_g_tk(self):
        p_skey = self.cookies[self.cookies.find('p_skey=') + 7: self.cookies.find(';', self.cookies.find('p_skey='))]
        h = 5381
        for i in p_skey:
            h += (h << 5) + ord(i)
        # print('g_tk',h&2147483647)
        self.g_tk = h & 2147483647
        print('计算的q_tk值为'+str(self.g_tk))

    def get_qzone_token(self):
        #还要获取一个qzonetoken，它也很重要
        html = self.web.page_source
        g_qzonetoken = re.search('window\.g_qzonetoken = \(function\(\)\{ try\{return (.*?);\} catch\(e\)',html)  # 从网页源码中提取g_qzonetoken
        g_qzonetoken = str(g_qzonetoken.group(0)).split('\"')[1]
        self.qztoken = g_qzonetoken
        print('计算的qzonetoken值为'+g_qzonetoken)

    def get_url_response(self,url):
        try:
            page = self.req.get(url=url,headers=self.headers,timeout=60)
        except Exception as e :
            print('[Error]爬取说说信息出错:'+e)
            exit(1)
        return page
if __name__ == '__main__':
    dirPath = 'D:\\spider\\qqzone\\userinfo.ini'
    spider = Spider(dirPath)
    spider.login()
    exit(0)