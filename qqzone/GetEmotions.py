from Spider import *
from Dao import *
from GetFriends import parse_page
from urllib import parse
import re
import json
import time
import requests

#0表示varchar255 -1表示text 1表示int
emotion_tb_keys = {'id':-2,'name':0,'uin':0,'content':-1,
'createTime':0,'created_time':0,'editMask':0,
'tid':0,'commentlist':-1,'type':0,'pic':-1,'source_name':0,'cmtnum':1}

emotion_number_tb_keys = {'id':-2,'name':0,'uin':0,'total':1,'count_time':0}

def get_emotion_url(spider,qq,pos=0):
    url='https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?'
    params = {
        "sort": 0,
        "ftype": 0,
        "num": 20,
        "cgi_host": "http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6",
        "replynum": 100,
        "callback": "_preloadCallback",
        "code_version": 1,
        "inCharset": "utf-8",
        "outCharset": "utf-8",
        "notice": 0,
        "format": "jsonp",
        "need_private_comment": 1,
        "g_tk": spider.g_tk,
        "qzonetoken": spider.qztoken,
        "uin": qq,
        "pos": pos
    }
    url = url + parse.urlencode(params)
    print('[processing]获取'+str(qq)+'说说链接为:'+url)
    return url
def emotion_save_as_file (jsons,fileName="friend_json.json"):
    try:
        w = open('./'+fileName,'a+',encoding='utf-8')
        # w.write(str(json))
        json.dump(jsons,w,ensure_ascii=False)
        w.close()
        print('[success]json文件写入成功')
    except Exception as e:
        print('[Error]文件写入失败'+str(e))
        exit(1)
def get_emotion(spider,qq):
    con = spider.db
    if not getattr(spider,'is_login',False):
        print('[Error]:尚未登陆')
        exit(0)
    try:
        url = get_emotion_url(spider,qq,0)
    except Exception as e:
        print("[Error]查询好友url拼接失败"+str(e))
        exit(1)
    try:
        page = getattr(spider,'req').get(url=url,headers=spider.headers,timeout=5,verify=False)
        time.sleep(2)
        j = parse_page(page)
    except Exception as e :
        print('[Error]获取total出错:'+str(e))
        j = {}
    if 'total' in list(j.keys()):
        total = j['total']
        if total > 0:
            page_num = int(total/20) if total%20==0 else int(total/20+1)
        else:
            print('[Warning]total为0')
            page_num = 0
    else:
        print('[Warning]没有total这个字段')
        total = -1
        if(j['message']=='对不起,主人设置了保密,您没有权限查看'):
            print('[Warning]'+str(qq)+'设置了权限，无法访问')
            file = open('./permission','a+',encoding='utf-8')
            file.write(str(qq)+'\n')
            file.close()
        page_num = 0
    if not table_is_exist(con,"emotion_total_tb"):
        create_table_from_dict(con,"emotion_total_tb",emotion_number_tb_keys)
    total_item = emotion_number_tb_keys
    total_item['id'] = 'null'
    total_item['name'] = j['usrinfo']['name']
    total_item['uin'] = qq
    total_item['total'] = total
    total_item['count_time'] = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    #记录说说总数
    if  not is_repetitive(con,"emotion_total_tb",total_item['uin'],'uin'):
        insert_emotion_total(con,"emotion_total_tb",total_item)
    else:
        update_emotion_total(con,"emotion_total_tb",total_item)
    # print(j)
    print('[processing]共'+str(page_num)+'页数据，解析开始-----------------------')
    
    if not table_is_exist(con,"emotions_tb"):
        create_table_from_dict(con,"emotions_tb",emotion_tb_keys)
    '''此处开始进行迭代操作了'''
    url_list = []
    for t in range(0,page_num):
        pos = t*20
        url_list.append(get_emotion_url(spider,qq,pos))
    if len(url_list)>0 :
        break_flag = 0
        for index,u in enumerate(url_list):
            print('[processing]正在解析'+str(qq)+'第'+str(index)+'页说说数据')
            try:            
                page = getattr(spider,'req').get(url=u,headers=spider.headers,timeout=5,verify=False)
                time.sleep(2)
                j = parse_page(page)#解析成json数据
                if type(page) == 'ConnectionError':
                    raise ConnectionError()
            except requests.ConnectionError as ce:
                print('[Error]ConnectionError发生在了解析'+str(qq)+'第'+str(index)+'页说说数据时，尝试解析下一页数据,先等待2秒缓冲')
                time.sleep(2)
                if(index<len(url_list)-1):
                    url_list.append(u)
                    continue
                else:
                    error_node = {'uin':qq,'pos':index}
                    print('[Error]当前页是最后一页，记录错误节点:'+str(error_node))
                    if not os.path.exists('./errorNode'):
                        os.mkdir('./errorNode')
                    file = open('./erroNode/error_node_'+str(time.time())+'.json','w+',encoding='utf-8')
                    file.write(str(error_node))
                    print('[Success]error_node记录成功')
                    break
            except Exception as e :
                print('[Error]爬取说说信息出错:'+str(e))
                print('[Error]此时page数据是'+str(page))
                raise e
            template_data = emotion_tb_keys
            if j is None:
                continue 
            try:
                template_data['id'] = 'null'
                template_data['name'] = j['usrinfo']['name']
                template_data['uin'] = j['usrinfo']['uin']
                ##为了防止有些人说说设置权限，一条都看不了
                if j['msglist'] is not None:
                    for index,item in enumerate(j['msglist']):
                        template_data['content'] = str(item['content'].replace("\"","\\\""))
                        template_data['createTime'] = item['createTime']
                        template_data['created_time'] = item['created_time']
                        template_data['editMask'] = item['editMask'] if 'editMask' in list(item.keys()) else 'null'
                        template_data['tid'] = item['tid']
                        template_data['cmtnum'] = item['cmtnum']
                        template_data['type'] = item['conlist'][0]['type'] if 'conlist' in list(item.keys()) and item['conlist']!=None and'type' in list(item['conlist'][0].keys()) else 'null'
                        template_data['source_name'] = item['source_name']
                        template_data['pic'] = item['pic'] if 'pic' in list(item.keys()) else 'null'
                        template_data['commentlist'] = str(item['commentlist']).replace("\"","\\\"") if 'commentlist' in list(item.keys()) else 'null'
                        if  is_repetitive(con,"emotions_tb",template_data['tid'],'tid'):
                            continue
                        insert_emotion(con,"emotions_tb",template_data)
                        emotion_save_as_file(template_data,"emotion_"+str(qq)+"_json.json")
                else:
                    print('[Warning]'+str(template_data['uin'])+'在此页可见数是0')
                    ##也不需要进行接下页的访问，可以直接换人
                    break_flag = 1
            except Exception as e:
                print('[Error]template_data合并错误：'+str(e))
            if break_flag == 1:
                break
def insert_total(con,total_item):
    if not table_is_exist(con,"emotion_total_tb"):
        create_table_from_dict(con,"emotion_total_tb",emotion_number_tb_keys)
    insert_emotion_total(con,"emotion_total_tb",total_item)

def get_template_data_from_page(con,page):
    j = parse_page(page)#解析成json数据
    template_data = emotion_tb_keys
    if j is None:
        raise Exception('None') 
    try:
        template_data['id'] = 'null'
        template_data['name'] = j['usrinfo']['name']
        template_data['uin'] = j['usrinfo']['uin']
        ##为了防止有些人说说设置权限，一条都看不了
        if j['msglist'] is not None:
            for index,item in enumerate(j['msglist']):
                template_data['content'] = item['content']
                template_data['createTime'] = item['createTime']
                template_data['created_time'] = item['created_time']
                template_data['editMask'] = item['editMask'] if 'editMask' in list(item.keys()) else 'null'
                template_data['tid'] = item['tid']
                template_data['cmtnum'] = item['cmtnum']
                template_data['type'] = item['conlist'][0]['type'] if 'conlist' in list(item.keys()) and item['conlist']!=None and'type' in list(item['conlist'][0].keys()) else 'null'
                template_data['source_name'] = item['source_name']
                template_data['pic'] = item['pic'] if 'pic' in list(item.keys()) else 'null'
                template_data['commentlist'] = str(item['commentlist']).replace("\"","\\\"") if 'commentlist' in list(item.keys()) else 'null'
                insert_emotion(con,"emotions_tb",template_data)
                emotion_save_as_file(template_data,"emotion_"+str(qq)+"_json.json")
        else:
            print('[Warning]'+str(template_data['uin'])+'在此页可见数是0')
            ##也不需要进行接下页的访问，可以直接换人
    except Exception as e:
        print('[Error]template_data合并错误：'+str(e))


if __name__ == "__main__":
    dirPath = 'D:\\liufanWorkspace\\qqzone_spider\\qqzone\\userinfo.ini'
    spider = Spider(dirPath)
    spider.login()
    get_emotion(spider,214704958)
    exit(0)

    