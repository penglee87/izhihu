#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests,sys,os,json,re,time
from bs4 import BeautifulSoup as BS
from queue import Queue
"""
话题量比想象多很多,速度待优化
"""
#得到post所需xsrf
def getXsrf():
    r = requests.get(paraent_url)
    raw_xsrf = re.findall("xsrf(.*)", r.text)
    _xsrf = raw_xsrf[0][9:-3]
    return _xsrf


#得到子话题JSON
def get_topic():
    post_url = "https://www.zhihu.com/topic/19776749/organize/entire"
    #params = {'child': '', 'parent': '19778317'}
    xsrf = getXsrf()
    payload={"_xsrf":xsrf}
    ROOT_TOPIC = ('19776749', '根话题', '')
    topic_queue = Queue()
    topic_queue.put(ROOT_TOPIC)
    while not topic_queue.empty():
        topic = topic_queue.get()
        if topic[0] == '19776749':
            params = {}
        else:
            params = {'child': topic[2], 'parent': topic[0]}
    
        try:
            result = requests.post(post_url, params = params, data=payload, headers=header_info)
        except:
            continue
        try:
            msg_list = result.json()['msg']
        except:
            continue
        file = open("topics.txt", "at",encoding='utf-8')
        for msg in msg_list[1]:
            if msg[0][0] == 'topic':
                topic_title, topic_id = msg[0][1], msg[0][2]
                #topic_result_list.append((topic_id, topic_title))
                file.write(topic_id + "\t" + topic_title + "\n")
                if len(msg[1]) != 0:
                    if msg[1][0][0][0] == 'load':
                        child, parent, title = '', msg[1][0][0][3], topic_title
                        topic_queue.put((parent, title, child))
                    else:
                        print("Not 显示子话题, message type:" + msg[0][0])
            elif msg[0][0] == 'load':
                child, parent, title = msg[0][2], msg[0][3], topic[1]
                topic_queue.put((parent, title, child))
            else:
                print("Not 加载更多, message type:" + msg[0][0])
        file.close()
    #return topic_result_list


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


paraent_url = "https://www.zhihu.com/topic/19776749/organize/entire"
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
"Referer":paraent_url,
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
   

get_topic()
