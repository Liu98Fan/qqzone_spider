# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from GetEmotions import *
from Spider import *
from Dao import *
from GetFriends import *
import copy
from ErroTest import get_residue_list




def get_all_emotion(spider,**kwarg):
    count = 0
    if len(kwarg)>0: 
        friend_list = kwarg['residue_list']
        processed_list = kwarg['processed_list']
        count = kwarg['count']
    else:
        friend_list = get_friend_list(spider)
        processed_list = []
    print('[logging]好友列表长度为:'+str(len(friend_list))+','+str(friend_list))
    
    residue_list = copy.copy(friend_list)
    try:
        for index,uin in enumerate(friend_list):
            if type(uin) == tuple
                uin = uin[0]
            print('[processing]开始处理第'+str(index)+'个账号'+str(uin)+'------------------------')
            get_emotion(spider,uin)
            processed_list.append(uin)
            residue_list.pop(index)
        print('[Success]全部处理完成--------------------------')
    except Exception as e:
        print('[Error]出错了,记录error_node:'+str(e))
        file = open('./processed_list','w',encoding='utf-8')
        file.write(str(processed_list))
        file.close()
        file = open('./residue_list','w',encoding='utf-8')
        file.write(str(residue_list))
        file.close()
        if count >2 :
            print('[logging]重试'+str(count)+'次失败，尝试重新登陆')
            spider.login()
            count = 0
        param =  {
            'processed_list':processed_list,
            'residue_list':residue_list,
            'friend_list':residue_list,
            'count':count + 1
            }
        print('[Success]记录成功，尝试重试,重试参数:'+str(param))
        get_all_emotion(spider,
                processed_list = param['processed_list'],
                residue_list = param['residue_list'],
                friend_list = param['friend_list'],
                count = param['count']
                )
        # exit(1)


def get_page_num(spider,qq):
    if not getattr(spider,'is_login',False):
        print('[Error]:尚未登陆')
        exit(0)
    try:
        url = get_emotion_url(spider,qq)
    except Exception as e:
        print("[Error]查询好友url拼接失败"+str(e))
        exit(1)
    try:
        page = getattr(spider,'req').get(url=url,headers=spider.headers,timeout=60)
    except Exception as e :
        print('[Error]爬取说说信息出错:'+str(e))
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
    
    dirPath = 'D:\\spider\\qqzone\\userinfo.ini'
    spider = Spider(dirPath)
    spider.login()
    #get_all_emotion(spider)
    [processed_list,residue_list] = get_residue_list(spider)
    param =  {
            'processed_list':processed_list,
            'residue_list':residue_list,
            'friend_list':residue_list,
            'count':0
            }
    get_all_emotion(spider,processed_list = param['processed_list'],
                residue_list = param['residue_list'],
                friend_list = param['friend_list'],
                count = param['count'])
