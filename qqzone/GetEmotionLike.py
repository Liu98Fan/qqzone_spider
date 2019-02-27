import time
import copy
from urllib import parse
from GetFriends import parse_page
from Dao import *
from Spider import *
from GetFriends import *
#0表示varchar255 -1表示text 1表示int
#点赞数据（一条说说的点赞量）
like_data_keys = {
    'tid':0,
    'like':1,
    'ilike':1,
}
#点赞行为，谁给哪条说说点了赞
like_list_keys = {
    'uin':0,
    'name':0,
    'tid':0,
    'flag':1
}
like_list_keys2 = {
    'uin':0,
    'tid':0,
    'nick':0,
    'portrait':0,
    'gender':0,
    'constellation':0,
    'addr':0,
    'if_qq_friend':1,
    'if_special_care':1,
    'if_special_vip':1
}


'''
第一种爬取点赞信息的链接cgi-bin/user/qz_opcnt2
'''
def get_like_url1(spider,uin,tid):
    url = 'https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/user/qz_opcnt2?'
    param = {
        'unikey':'http://user.qzone.qq.com/'+str(uin)+'/mood/'+str(tid),
        '_stp':time.time(),
        'face':0,
        'fupdate':1,
        'g_tk':spider.g_tk,
        'qzonetoken':spider.qztoken
    }
    url = url + parse.urlencode(param)
    print('[processing]获取说说'+str(tid)+'点赞链接(1号链接)为:'+url)
    return url

'''
第一种爬取点赞信息的链接cgi-bin/likes/get_like_list_app
'''
def get_like_url2(spider,uin,tid,is_first_page):
    url = 'https://user.qzone.qq.com/proxy/domain/users.qzone.qq.com/cgi-bin/likes/get_like_list_app?'
    param = {
        'unikey':'http://user.qzone.qq.com/'+str(uin)+'/mood/'+str(tid),
        'begin_uin':'',#上一查询结果的最后一个uin，第一页则为0
        'is_first_page':is_first_page,
        'query_count':60,
        'g_tk':spider.g_tk,
        'qzonetoken':spider.qztoken,
        'uin':spider._Spider__username
    }
    url = url + parse.urlencode(param)
    print('[processing]获取说说'+str(tid)+'点赞链接(2号链接)为:'+url)
    return url

def get_like_data1(spider,uin,tid):
    con = spider.db
    if not getattr(spider,'is_login',False):
        print('[Error]:尚未登陆')
        exit(0)
    try:
        url = get_like_url1(spider,uin,tid)
    except Exception as e:
        print("[Error]查询点赞url拼接失败"+str(e))
        exit(1)
    try:
        page = getattr(spider,'req').get(url=url,headers=spider.headers,timeout=5,verify=False)
        time.sleep(2)
        j = parse_page(page)
    except Exception as e :
        print('[Error]获取点赞信息时出错:'+str(e))
        j = {}
    try:
        parse_page_json_url1(j,uin,tid,con)
    except NameError as nr:
        print('[Error]解析page_json出错，请确认是否使用了正确的解析策略'+str(nr))

def get_like_data2(spider,uin,tid):
    con = spider.db
    url_list = []
    if not getattr(spider,'is_login',False):
        print('[Error]:尚未登陆')
        exit(0)
    try:
        url = get_like_url2(spider,uin,tid,1)
        url_list.append(url)
    except Exception as e:
        print("[Error]查询点赞url拼接失败"+str(e))
        exit(1)
    try:
        page = getattr(spider,'req').get(url=url,headers=spider.headers,timeout=5,verify=False)
        time.sleep(2)
        j = parse_page(page)
        total_number = j['data']['total_number']
    except Exception as e :
        print('[Error]获取点赞信息时出错:'+str(e))
        j = {}
    try:
        if total_number>0:
            parse_page_json_url2(j,uin,tid,con)
    except NameError as nr:
        print('[Error]解析page_json出错，请确认是否使用了正确的解析策略'+str(nr))



'''
第一种url解析方法
'''    
def parse_page_json_url1(j,uin,tid,con):
    if not table_is_exist(con,"emotion_like_data_tb"):
        create_table_from_dict(con,"emotion_like_data_tb",like_data_keys)
    if not table_is_exist(con,"emotion_like_list_tb"):
        create_table_from_dict(con,"emotion_like_list_tb",like_list_keys)
    if len(j)>0:
        if 'message' in j.keys():
            if j['message'] == 'succ':
                template_like_data = like_data_keys
                template_like_list = like_list_keys
                template_like_data['id']=template_like_list['id']='null'
                template_like_data['tid']=template_like_list['tid']=tid
                template_like_data['like']=j['data'][0]['current']['likedata']['cnt']
                template_like_data['ilike']=j['data'][0]['current']['likedata']['ilike']
                if not is_repetitive(con,"emotion_like_data_tb",template_like_data['tid'],'tid'):
                    insert_like_Data(con,"emotion_like_data_tb",template_like_data)
                else:
                    update_emotion_total(con,"emotion_like_Data_tb",template_like_data)
                like_list = j['data'][0]['current']['likedata']['list']
                for item in like_list:
                    template_like_list['uin'] = item[0]
                    template_like_list['name'] = item[1]
                    template_like_list['flag'] = item[2]
                    if not is_repetitive(con,"emotion_like_list_tb",template_like_list['tid'],'tid',condition={'id':template_like_list['uin'],'column_name':'uin'}):
                        insert_like_Data(con,"emotion_like_list_tb",template_like_list)
                    else:
                        update_emotion_total(con,"emotion_like_list_tb",template_like_list)
                print('[Success]'+str(uin)+'的tid为'+tid+'的说说记录完毕')

'''
第二种url解析方法
'''  
def parse_page_json_url2(j,uin,tid,con):
    if not table_is_exist(con,"emotion_like_data2_tb"):
        create_table_from_dict(con,"emotion_like_data2_tb",like_data_keys)
    if not table_is_exist(con,"emotion_like_list2_tb"):
        create_table_from_dict(con,"emotion_like_list2_tb",like_list_keys)
    if len(j)>0:
        if 'message' in j.keys():
            if j['message'] == 'succ!':
                template_like_data = like_data_keys
                template_like_list = like_list_keys2
                template_like_data['id']=template_like_list['id']='null'
                template_like_data['tid']=template_like_list['tid']=tid
                template_like_data['like']=j['data'][0]['current']['likedata']['cnt']
                template_like_data['ilike']=j['data'][0]['current']['likedata']['ilike']
                if not is_repetitive(con,"emotion_like_data2_tb",template_like_data['tid'],'tid'):
                    insert_like_Data(con,"emotion_like_data2_tb",template_like_data)
                else:
                    update_emotion_total(con,"emotion_like_data2_tb",template_like_data)
                if total_number>0:
                    like_list = j['data']['like_uin_info']
                else:
                    like_list = []
                for item in like_list:
                    template_like_list['fuin'] = item['fuin']
                    template_like_list['nick'] = item['nick']
                    template_like_list['portrait'] = item['portrait']
                    template_like_list['gender'] = item['gender']
                    template_like_list['constellation'] = item['constellation']
                    template_like_list['addr'] = item['addr']
                    template_like_list['if_qq_friend'] = item['if_qq_friend']
                    template_like_list['if_special_care'] = item['if_special_care']
                    template_like_list['if_special_vip'] = item['if_special_vip']
                    if not is_repetitive(con,"emotion_like_list2_tb",template_like_list['tid'],'tid',condition={'id':template_like_list['uin'],'column_name':'fuin'}):
                        insert_like_Data(con,"emotion_like_list2_tb",template_like_list)
                    else:
                        update_emotion_total(con,"emotion_like_list2_tb",template_like_list)
                print('[Success]'+str(uin)+'的tid为'+tid+'的说说点赞记录完毕')

def get_all_like_data(spider,**kwarg):
    ##定义重试次数
    count = 0
    ##如果，给定了重试参数，则进行赋值
    if len(kwarg)>0: 
        #这里把需要处理的好友赋值为重试参数中的剩余列表
        friend_list = kwarg['like_residue_list']
        processed_list = kwarg['like_processed_list']
        count = kwarg['count']
    else:
        #否则获取全部好友数据，初始化处理列表为空，这里应该从第一个好友开始处理
        friend_list = get_friend_list(spider)
        processed_list = []
    print('[logging]好友列表长度为:'+str(len(friend_list))+','+str(friend_list))
    #计算需要处理的好友列表
    residue_list = copy.copy(friend_list)
    try:
        for index,uin in enumerate(friend_list):
            if type(uin) == tuple:
                uin = uin[0]
            print('[processing]开始处理第'+str(index)+'个账号'+str(uin)+'------------------------')
            #首先获取这个好友的说说列表，数据来源于数据库，包括uin和tid字段
            emotion_list = get_emotion(spider.db,str(uin))
            #print(str(emotion_list))
            for item in emotion_list:
                #遍历该好友说说数据，进行爬虫
                get_like_data2(spider,item[0],item[1])
            #处理完成后将改好友加入已处理劫镖
            processed_list.append(uin)
            #剩余列表出栈
            #residue_list.pop(index)
            residue_list.remove(uin)
        print('[Success]全部处理完成--------------------------')
    except Exception as e:
        #如果出现了错误，记录下error_node
        print('[Error]出错了,记录error_node:'+str(e))
        file = open('./like_processed_list','w',encoding='utf-8')
        file.write(str(processed_list))
        file.close()
        file = open('./like_residue_list','w',encoding='utf-8')
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
        get_all_like_data(spider,
                processed_list = param['processed_list'],
                residue_list = param['residue_list'],
                friend_list = param['friend_list'],
                count = param['count']
                )
        # exit(1)



if __name__ == '__main__':
    dirPath = 'D:\\liufanWorkspace\\qqzone_spider\\userinfo.ini'
    spider = Spider(dirPath)
    spider.login()
    get_all_like_data(spider)

    # emotion_list = get_emotion(spider.db,'88665291')
    # print(str(emotion_list))
    # for item in emotion_list:
    #     get_like_data(spider,item[0],item[1])
    #------------------------------
    #get_like_data(spider,'2710802815','7f9193a1a03a29588bff0400')

    