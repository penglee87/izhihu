#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests,sys,os,json,re,time
from bs4 import BeautifulSoup as BS
"""
批量关注知乎用户

1: 每一个用户都有一个hash_id应该是其用户标志，可以在chorme浏览器看得到这个，然后在html页面全局搜索即可用正则获得该值
2：可以在批量获得某个话题下面的用户。
3：更换话题，假如想关注NBA底下的所有用户，需要首先获得nba这个话题的link-id
4: start关键字这么来的 t = int(time.time()) 十位数的时间戳
"""

#得到post所需xsrf
def getXsrf():
    r = requests.get(topic_url)
    raw_xsrf = re.findall("xsrf(.*)", r.text)
    _xsrf = raw_xsrf[0][9:-3]
    return _xsrf
    
#得到话题页面要关注用户的hash_id
def getHash():
    hash_id_all = []
    post_url = topic_url
    #header_info["Referer"] = post_url
    xsrf = getXsrf()
    for i in range(3):
        x = 0 + i * 20
        start = int(time.time())
        payload={"offset":x, "start":start, "_xsrf":xsrf}
        # time.sleep(3)
        
        result = requests.get(post_url, data=payload, headers=header_info)
        #saveFile(result.text,"zhihu_focus_test.html")
        #print (result.text)
        raw_hash_id = re.findall("<a href=.*? name=.*? class=.*? id=(.*?)>.*?</a>", result.text)
        #saveFile(str(raw_hash_id),"raw_hash_id.txt")
        for item in raw_hash_id:
           hash_id_all.append(item[4:36])
        print ("get hash_id_page",i)
    return hash_id_all
    
#进行关注操作
def getFocus():
    hash_id = getHash()
    xsrf = getXsrf()
    i = 0
    for x in hash_id:
        i = i + 1
        params = json.dumps({"hash_id":x})
        payload={"method":"follow_member", "params":params, "_xsrf":xsrf}
        click_url = "https://www.zhihu.com/node/MemberFollowBaseV2"
        try:
            #延时
            #time.sleep(1)
            result = requests.post(click_url, data=payload, headers=header_info)
        except Exception as e:
            print ("不能关注了")
        # 这个参数表示返回msg 如果r为0即表示关注成功
        #response = json.loads(result.content)
        response = json.loads(result.text)
        if response["r"] == 0:
            print ("关注成功"," ",response["r"]," ",i)
        else:
            print ("fucking")
    print ("就这么多了！！！！")
    
 
#读取cookie文件   
def loadCookie(cookieFile):
    """读取cookie文件，返回反序列化后的dict对象，没有则返回None"""
    #cookieFile = os.path.join(sys.path[0], "cookie")

    if os.path.exists(cookieFile):
        print("=" * 50)
        with open(cookieFile, "r") as f:
            cookie = json.load(f)
            return cookie
    return None

#保存文件，主要测试用   
def saveFile(data,filename):
    save_path = os.path.join(sys.path[0], filename)
    f_obj = open(save_path, "w",encoding="utf-8") # w 表示打开方式
    f_obj.write(data)
    f_obj.close()

topic_url = "https://www.zhihu.com/topic/19560170/followers"
header_info = {
"Accept":"*/*",
"Accept-Encoding":"gzip,deflate,sdch",
"Accept-Language":"zh-CN,zh;q=0.8",
"Connection":"keep-alive",
"Content-Length":"127",
"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
"DNT":"1",
"Host":"www.zhihu.com",
"Origin":"http://www.zhihu.com",
"Referer":topic_url,
"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
"X-Requested-With":"XMLHttpRequest",
}

requests = requests.Session()    
cookieFile = os.path.join(sys.path[0], "cookie")        
cookie = loadCookie(cookieFile)
if cookie:
    print("检测到cookie文件,直接使用cookie登录")
    requests.cookies.update(cookie)
    soup = BS(requests.get(r"http://www.zhihu.com/").text, "html.parser")
    print("已登陆账号： %s" % soup.find("span", class_="name").getText())
else:
    print("没有找到cookie文件，请调用login方法登录一次！")
        


getFocus()