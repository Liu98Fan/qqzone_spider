from Spider import *
from Dao import *
from urllib import parse
import json
import re
import os

def get_url_partial(spider):
    url = 'https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_ship_manager.cgi?'
    params = {
        "uin": spider._Spider__username,#我的QQ
        "do": 1,#我在意谁  谁在意我的时候是2
        "fupdate": 1,
        "clean": 0,#谁在意我的时候为0
        "g_tk": getattr(spider,'g_tk'),
        "qzonetoken": getattr(spider,'qztoken'),
    }
    url = url + parse.urlencode(params)
    print('[processing]获取前200亲密度好友链接为:'+url)
    return url

def get_friends_partial(spider):
    if not getattr(spider,'is_login',False):
        print('[Error]:尚未登陆')
        exit(0)
    try:
        url = get_url_partial(spider)
    except Exception as e:
        print("[Error]查询好友url拼接失败"+e)
        exit(1)
    page = ''
    try:
        page = getattr(spider,'req').get(url=url,headers=spider.headers,timeout=60)
    except Exception as e :
        print('[Error]爬取亲密度好友信息出错:'+e)
        exit(1)
    json = parse_page(page)
    save_as_file(json,"friend"+str(spider._Spider__username)+"_json.json")
    process_friend(spider,json)

def save_as_file(jsons,fileName="friend_json.json"):
    try:
        with open('./'+fileName,'w',encoding='utf-8') as w:
            # w.write(str(json))
            json.dump(jsons,w)
        w.close()
        print('[success]json文件写入成功')
    except Exception as e:
        print('[Error]文件写入失败'+str(e))
        exit(1)

def read_from_file(filePath):
    if  os.path.exists(filePath):
        try:         
            file = open(filePath,'r',encoding='utf-8')
            return json.load(file)
        except Exception as e:
            print('[Error]读取文件失败:'+str(e))
    else:
        print('[Error]filePath不存在！')
        exit(1)

def process_friend(spider,json):
    db = spider.db
    if json['code'] == 0 :
        list = json['data']['items_list']
        print('[processing]共查询到'+str(len(list))+'个好友,开始录入数据库')
        for item in list:
            key_list = item.keys()#获取所有的key
            #建表
            if not table_is_exist(db,'all_friends_score_tb'):
                create_table(db,"all_friends_score_tb",key_list)
            item["master"]=spider._Spider__username
            insert_friend(db,"all_friends_score_tb",item)
    else:
        print('[Error]code!=0,爬取好友信息失败')
def parse_page(page):
    try:
        j = json.loads(re.match(".*?({.*}).*",page.text,re.S).group(1))
        return j
    except:
        print('[Error]解析好友数据失败'+str(e))
        exit(1)
if __name__ == '__main__':
    dirPath = 'D:\\spider\\qqzone\\userinfo.ini'
    spider = Spider(dirPath)
    spider.login()
    page = get_friends_partial(spider)
    exit(0)

    # j = read_from_file('./friend_json.json')
    # print(str(j))

    

