# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from GetEmotions import *
from Spider import *
from Dao import *

def get_all_emotion(spider):
    friend_list = get_friend_number(spider.db,spider._Spider__username)
    print('[logging]好友列表:'+str(friend_list))
    processed_list = []
    try:
        for index,uin in enumerate(friend_list):
            uin = uin[0]
            print('[processing]开始处理第'+str(index)+'个账号'+str(uin)+'------------------------')
            get_emotion(spider,uin)
            processed_list.append(uin)
        print('[Success]全部处理完成--------------------------')
    except Exception as e:
        print('[Error]出错了'+str(e))
        file = open('./processed_list','w',encoding='utf-8')
        file.write(str(processed_list))
        file.close()
        exit(1)

def get_page_num(spider,qq):
    if not getattr(spider,'is_login',False):
        print('[Error]:尚未登陆')
        exit(0)
    try:
        url = get_emotion_url(spider,qq)
    except Exception as e:
        print("[Error]查询好友url拼接失败"+e)
        exit(1)
    try:
        page = getattr(spider,'req').get(url=url,headers=spider.headers,timeout=60)
    except Exception as e :
        print('[Error]爬取说说信息出错:'+e)
        exit(1)
    j = parse_page(page)
    if 'total' in list(j.keys()):
        total = j['total']
        if total > 0:
            page_num = int(total/20) if total%20==0 else int(total/20+1)
        else:
            print('[Warning]total为0')
    else:
        print('[Warning]没有total这个字段')
    # print(j)
    print('[processing]共'+str(page_num)+'页数据，解析开始-----------------------')
    return page_num

if __name__ == "__main__":
    dirPath = 'D:\\liufanWorkspace\\qqzone_spider\\userinfo.ini'
    spider = Spider(dirPath)
    spider.login()
    get_all_emotion(spider)