#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests,sys,os,json,re,time
from bs4 import BeautifulSoup as BS
"""
批量取消关注的知乎用户
都是用cookie 直接登录
1: 每一个用户都有一个hash_id应该是其用户标志，可以在chorme浏览器看得到这个，然后在html页面全局搜索即可用正则获得该值
2：在关注的人页面下获取用户的hash_id，默认只显示20个用户，通过post 获取所有用户。
"""

#得到post所需的xsrf
def getXsrf():
    r = requests.get(followees_url)
    raw_xsrf = re.findall("xsrf(.*)", r.text)
    _xsrf = raw_xsrf[0][9:-3]
    return _xsrf
    
#得到post所需的个人 user_hash_id
def my_hash_id():
    r = requests.get(followees_url)
    my_hash_id = re.findall("user_hash(.*)", r.text)
    _hash_id = my_hash_id[0][3:35]
    #print(_hash_id)
    return _hash_id



def cancelFocus():
    hash_id_all = []
    post_url = followees_url
    xsrf = getXsrf()
    hash_id = my_hash_id()
    #得到关注的人页面下用户的hash_id
    for i in range(3):
        x = 0 + i * 20
        params = {"offset":x,"order_by":"created","hash_id":hash_id}
        params = json.dumps(params)
        payload={"method":"next", "params":params,"_xsrf":xsrf}
        #time.sleep(3)
        #result = requests.post(post_url, data=payload, headers=header_info)
        result = requests.get(post_url, data=payload, headers=header_info)
        raw_hash_id = re.findall("data-id=(.*?) class=.*?", result.text)
        #saveFile(str(raw_hash_id),"raw_hash_id.txt")
        #针对用户的hash_id进行取消关注
        for item in raw_hash_id:
           #hash_id_all.append(item[1:-1])
           
           x = item[1:-1]
           cancel_params = json.dumps({"hash_id":x})       
           cancel_payload={"method":"unfollow_member", "params":cancel_params, "_xsrf":xsrf}
           click_url = "https://www.zhihu.com/node/MemberFollowBaseV2"
           try:
               #延时
               #time.sleep(1)
               #result = requests.post(click_url, data=json.dumps(payload), headers=header_info)   将data字典转化为普通string后直接发布
               cancel_result = requests.post(click_url, data=cancel_payload, headers=header_info)  #data数据字典 在发出请求时会自动编码为表单形式
           except Exception as e:
               print ("异常,不能取消了")
           #这个参数表示返回msg 如果r为0即表示成功
           #response = json.loads(cancel_result.content)           
           response = json.loads(cancel_result.text)
           if response["r"] == 0:
               print ("取消关注成功"," ",response["r"]," ",i)
           else:
               print ("fucking")
           #print ("get hash_id_page",i)
           #saveFile(str(hash_id_all),"hash_id_all.txt")


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


followees_url = "https://www.zhihu.com/people/lee-82-75-31/followees"

header_info = {
"Accept":"*/*",
"Accept-Encoding":"gzip,deflate,sdch",
"Accept-Language":"zh-CN,zh;q=0.8",
"Connection":"keep-alive",
"Content-Length":"171",
"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
"DNT":"1",
"Host":"www.zhihu.com",
"Origin":"http://www.zhihu.com",
"Referer":followees_url,
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
    print("没有找到cookie文件,请调用login方法登录一次！")
        

cancelFocus()


"""  
#得到关注的人页面下用户的hash_id
def getHash():
    hash_id_all = []
    post_url = followees_url
    xsrf = getXsrf()
    hash_id = my_hash_id()
    for i in range(3):
        x = 0 + i * 20
        params = {"offset":x,"order_by":"created","hash_id":hash_id}
        params = json.dumps(params)
        payload={"method":"next", "params":params,"_xsrf":xsrf}
        #time.sleep(3)
        #result = requests.post(post_url, data=payload, headers=header_info)
        result = requests.get(post_url, data=payload, headers=header_info)
        raw_hash_id = re.findall("data-id=(.*?) class=.*?", result.text)
        #saveFile(str(raw_hash_id),"raw_hash_id.txt")
        
        for item in raw_hash_id:
           hash_id_all.append(item[1:-1])         
        #print ("get hash_id_page",i)
        #saveFile(str(hash_id_all),"hash_id_all.txt")
    return hash_id_all
    

    
#取消关注操作
def cancelFocus():
    hash_id = getHash()
    xsrf = getXsrf()
    i = 0
    for x in hash_id:
        i = i + 1
        params = json.dumps({"hash_id":x})
        payload={"method":"unfollow_member", "params":params, "_xsrf":xsrf}
        click_url = "https://www.zhihu.com/node/MemberFollowBaseV2"
        try:
            #延时
            #time.sleep(1)
            #result = requests.post(click_url, data=json.dumps(payload), headers=header_info)   将data字典转化为普通string后直接发布
            result = requests.post(click_url, data=payload, headers=header_info)  #data数据字典 在发出请求时会自动编码为表单形式
        except Exception as e:
            print ("异常,不能取消了")
        #这个参数表示返回msg 如果r为0即表示成功
        #response = json.loads(result.content)
        response = json.loads(result.text)
        if response["r"] == 0:
            print ("取消关注成功"," ",response["r"]," ",i)
        else:
            print ("fucking")
    print ("就取消关注这么多了！！！！")
"""
