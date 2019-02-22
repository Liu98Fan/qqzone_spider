from Spider import *
from Dao import *
from GetFriends import parse_page
from urllib import parse
import re
import json

#0表示varchar255 -1表示text 1表示int
emotion_tb_keys = {'id':-2,'name':0,'uin':0,'content':-1,
'createTime':0,'created_time':0,'editMask':0,
'tid':0,'commentlist':-1,'type':0,'pic':-1,'source_name':0,'cmtnum':1}

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
        "qzonetoken":spider.qztoken,
        "uin":qq,
        "pos":pos
    }
    url = url + parse.urlencode(params)
    print('[processing]获取'+str(qq)+'说说链接为:'+url)
    return url
def emotion_save_as_file (jsons,fileName="friend_json.json"):
    try:
        w = open('./'+fileName,'a+',encoding='utf-8')
        # w.write(str(json))
        json.dump(jsons,w)
        w.close()
        print('[success]json文件写入成功')
    except Exception as e:
        print('[Error]文件写入失败'+str(e))
        exit(1)
def get_emotion(spider,qq):
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
    con = spider.db
    if not table_is_exist(con,"emotions_tb"):
        create_table_from_dict(con,"emotions_tb",emotion_tb_keys)
    '''此处开始进行迭代操作了'''
    url_list = []
    for t in range(0,page_num):
        pos = t*20
        url_list.append(get_emotion_url(spider,qq,pos))
    if len(url_list)>0 :
        for index,u in enumerate(url_list):
            time.sleep(2)
            try:
                print('[processing]正在解析'+str(qq)+'第'+str(index)+'页说说数据')
                page = getattr(spider,'req').get(url=url,headers=spider.headers,timeout=60)
            except Exception as e :
                print('[Error]爬取说说信息出错:'+e)
                exit(1)
            j = parse_page(page)#解析成json数据
            template_data = emotion_tb_keys
            try:
                template_data['id'] = 'null'
                template_data['name'] = j['logininfo']['name']
                template_data['uin'] = j['logininfo']['uin']
                for index,item in enumerate(j['msglist']):
                    template_data['content'] = item['content']
                    template_data['createTime'] = item['createTime']
                    template_data['created_time'] = item['created_time']
                    template_data['editMask'] = item['editMask']
                    template_data['tid'] = item['tid']
                    template_data['cmtnum'] = item['cmtnum']
                    template_data['type'] = item['conlist'][0]['type']
                    template_data['source_name'] = item['source_name']
                    template_data['pic'] = item['pic'] if 'pic' in list(item.keys()) else 'null'
                    template_data['commentlist'] = str(item['commentlist']).replace("\"","\\\"") if 'commentlist' in list(item.keys()) else 'null'
                    insert_emotion(con,"emotions_tb",template_data)
                    emotion_save_as_file(template_data,"emotion_"+str(qq)+"_json.json")
            except Exception as e:
                print('[Error]不存在字段：'+str(e))
if __name__ == "__main__":
    dirPath = 'D:\\spider\\qqzone\\userinfo.ini'
    spider = Spider(dirPath)
    spider.login()
    get_emotion(spider,214704958)
    exit(0)

    