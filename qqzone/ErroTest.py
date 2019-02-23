import pymysql as mysql 
import os
from Spider import Spider 
'''
此文件用于错误测试，因为空间说说量大，内容较多，且很乱，
很多bug错误都不明白怎么回事，因此可以通过此文件对某个链接或文本进行单独测试
'''
db_url = 'localhost'
db_username = 'root'
db_password = 'password'
db_base = 'qqzone'


def get_connection():
    try:
        connection = mysql.connect(db_url,db_username,db_password,db_password)
        return connection 
    except:
        print('【Error】数据库连接错误')
        exit(1)


def save_cookies(cookies):
    if cookies is not None:
        try:
            file = open('./qqzone/cookies','w+',encoding='utf-8')
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
    if os.path.exists('./qqzone/cookies'):
        try:
            file = open('./qqzone/cookies','r+',encoding='utf-8')
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

if __name__ == '__main__':
    dirPath = 'D:\\spider\\qqzone\\userinfo.ini'
    spider = Spider(dirPath)
    spider.login()
    save_cookies(spider.cookies)
