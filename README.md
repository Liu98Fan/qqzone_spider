**本人python经验不足，大一到大三多数在写java（目前大三），所以python的结构比较混乱，但是勉强实现了爬取10W+条说说的功能，且具有一点的错误处理机制。欢迎大佬指正不足，本人QQ214704958**

# 项目依赖
- configparser
- selenium
- pymysql

# 配置文件
初始化Spider的时候要传入一个配置文件的地址
例如:
```python
if __name__ == "__main__":
    
    dirPath = 'D:\\spider\\qqzone\\userinfo.ini'
    spider = Spider(dirPath)
```
配置文件格式如下:
```properties
[my_info]
number = QQ号
password = 密码
[db_info]
url = 数据库url
username = 数据库账号
password = 密码
name = 数据库名称
```
# 具体内容
- Spider.py 爬虫主类，包含个人信息，requests，driver，数据库连接等
- Dao.py 与数据库交互用，里面包含所需的所有数据库操作方法
- GetFriends.py 获取好友方法，目前只实现了根据关注度获取前200个好友，支持json文件存储和数据库存储
- GetEmotions.py 爬取指定QQ的全部说说方法
- GetFreiendEmotion.py 爬取指定QQ的好友说说方法，支持json文件存储和数据库存储，支持断点继续（比较low）
- ErroTest.py 错误测试用




# 链接分析
## 1、获取好友
按照空间的亲密度查找前200名好友的链接
```python
https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_ship_manager.cgi?
uin=******& #我的QQ
do=1& #我在意谁  谁在意我的时候是2
rd=0.2158404861506087& #不知道干啥的，可以不加
fupdate=1& #默认为1
clean=1& #谁在意我的时候为0
g_tk=**********& 已拥有
qzonetoken=**********& #已拥有
```

通过以上获取的数据是:
```json
_Callback({
	"code":0,
	"subcode":0,
	"message":"",
	"default":0,
	"data":
    {
        "items_list":[{"uin":**********, QQ号
            "name":"********", 备注
            "index":1, 排名
            "chang_pos":0, **
            "score":92, 亲密度得分
            "special_flag":"0", 特别关心标志
            "uncare_flag":"0", **
            "img":"**********"} 头像,{...},{...}{...}],
        "not_relation":[],
        "dirty_rate":0,
        "dirty_list":[]}
    }
);
```
原则上可以搞定200个好友的QQ
## 2、获取说说

获取链接为:
```python
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
        "uin": qq, 要获取的qq号
        "pos": pos 要获取的起始number
    }
```
返回的是jsonp格式
