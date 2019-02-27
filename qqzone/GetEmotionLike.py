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



def get_like_url(spider,uin,tid):
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
    print('[processing]获取说说'+str(tid)+'点赞链接为:'+url)
    return url

def get_like_data(spider,uin,tid):
    con = spider.db
    if not getattr(spider,'is_login',False):
        print('[Error]:尚未登陆')
        exit(0)
    try:
        url = get_like_url(spider,uin,tid)
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

def get_all_like_data(spider,**kwarg):
    count = 0
    if len(kwarg)>0: 
        friend_list = kwarg['like_residue_list']
        processed_list = kwarg['like_processed_list']
        count = kwarg['count']
    else:
        friend_list = get_friend_list(spider)
        processed_list = []
    print('[logging]好友列表长度为:'+str(len(friend_list))+','+str(friend_list))
    
    residue_list = copy.copy(friend_list)
    try:
        for index,uin in enumerate(friend_list):
            if type(uin) == tuple:
                uin = uin[0]
            print('[processing]开始处理第'+str(index)+'个账号'+str(uin)+'------------------------')
            emotion_list = get_emotion(spider.db,str(uin))
            #print(str(emotion_list))
            for item in emotion_list:
                get_like_data(spider,item[0],item[1])
            processed_list.append(uin)
            residue_list.pop(index)
        print('[Success]全部处理完成--------------------------')
    except Exception as e:
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
    