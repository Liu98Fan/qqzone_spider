
## 1、获取好友
按照空间的亲密度查找前200名好友的链接
https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_ship_manager.cgi?
uin=******& 我的QQ
do=1& 我在意谁  谁在意我的时候是2
rd=0.2158404861506087& 不知道干啥的，可以不加
fupdate=1& 默认为1
clean=1& 谁在意我的时候为0
g_tk=**********& 已拥有
qzonetoken=**********& 已拥有

通过以上获取的数据是:
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

原则上可以搞定200个好友的QQ
## 获取说说

