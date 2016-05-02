#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests,sys,os,json,re,time
from bs4 import BeautifulSoup
import mysql.connector
import asyncio
import aiohttp
"""
获取知乎某话题下所有用户信息
"""

def fetch(topic_url):
    result = session.get(topic_url)
    global topic_name,file_success,file_fail
    topic_name = re.search(r'data-disabled="1">(.*?)</h1>',result.text).group(1)
    topic_follow_num = re.search(r'<strong>(.*?)</strong></a> 人关注了该话题',result.text).group(1)
    file_success = open(topic_name + "_user_info.txt", "wt",encoding='utf-8')
    file_fail = open(topic_name + "_user_fail.txt", "wt",encoding='utf-8')
    _xsrf = re.search(r'name="_xsrf" value="(.*?)"', result.text).group(1)
    start = re.findall(r'class="zm-person-item" id="mi-(.*?)"',result.text)[-1]
    user_url_list = re.findall(r'class="zm-list-avatar-medium" href="(.*?)"',result.text)
    loop = asyncio.get_event_loop()
    tasks = [get_user_info(user_url) for user_url in user_url_list]
    loop.run_until_complete(asyncio.wait(tasks))
    headers_info["referer"] = topic_url
    headers_info["content-length"] = 65
    session.headers = headers_info
    page_num = int(int(topic_follow_num)/20)
    for i in range(2,4):
        x = i * 20
        #print('start',start)
        print("page_num",i)
        payload={"offset":x, "start":start, "_xsrf":_xsrf}
        time.sleep(3)
        result = session.post(topic_url, data=payload)
        #saveFile(result.json()["msg"][1],'result'+str(i)+'.json')
        
        user_url_list = re.findall(r'class="zm-list-avatar-medium" href="(.*?)"',result.json()["msg"][1])
        start = re.findall(r'class="zm-person-item" id="mi-(.*?)"',result.json()["msg"][1])[-1]
        
        tasks = [get_user_info(user_url) for user_url in user_url_list]
        loop.run_until_complete(asyncio.wait(tasks))
    file_success.close()
    file_fail.close()

@asyncio.coroutine
def get_user_info(user_url):
    url = 'https://www.zhihu.com' + user_url
    
    try :
        result = yield from aiohttp.get(url, allow_redirects=True)
        if result.status == 200:
            result_text = yield from result.text()
            soup = BeautifulSoup(result_text, "html.parser")
            if re.search(r'<span class="item gender" ><i class="icon icon-profile-(.*?)">',result_text):
                gender = re.search(r'<span class="item gender" ><i class="icon icon-profile-(.*?)">',result_text).group(1)
            else:
                gender = 'unknow'
            user_name = soup.find("div",class_="title-section ellipsis").span.string
            agree = soup.find("span",attrs={"class": "zm-profile-header-user-agree"}).strong.string
            thanks = soup.find("span",attrs={"class": "zm-profile-header-user-thanks"}).strong.string
            followees = soup.find("a",class_ = "item",href = re.compile("followees")).strong.string
            followers = soup.find("a",class_ = "item",href = re.compile("followers")).strong.string
            file_success.write("\t".join([user_url,user_name,gender,agree,thanks,followees,followers]) + "\n")
            #cursor.execute('insert into zhihu_user (user_url, gender,agree,thanks,followees,followers) values (%s, %s,%s, %s,%s, %s)', [user_url, str(gender),str(agree),str(thanks),str(followees),str(followers)])

        else:
            file_fail.write(user_url + "\t" + str(result.status) + "\n")
    except:
        file_fail.write(user_url + "\t" + "except" + "\n")
    finally:
        yield from result.release()
        #result.close()
        


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
    f_obj.write(str(data))
    f_obj.close()

#topic_url = "https://www.zhihu.com/topic/19552832/followers"  #python 8.8万
topic_url = "https://www.zhihu.com/topic/19550429/followers"  #电影 697万
headers_info = {
    "accept":"*/*",
    "accept-encoding":"gzip, deflate",
    "accept-language":"zh-CN,zh;q=0.8",
    "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
    "origin":"https://www.zhihu.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.zhihu.com",
    "x-requested-with":"XMLHttpRequest"
}

t1 = time.time()
session = requests.Session()

cookieFile = os.path.join(sys.path[0], "cookie")        
cookie = loadCookie(cookieFile)
if cookie:
    print("检测到cookie文件,直接使用cookie登录")
    session.cookies.update(cookie)
    soup = BeautifulSoup(session.get(r"http://www.zhihu.com/").text, "html.parser")
    print("已登陆账号： %s" % soup.find("span", class_="name").get_text())
else:
    print("没有找到cookie文件，请调用login方法登录一次！")
    

#file_success = open("user_info.txt", "wt",encoding='utf-8')
#file_fail = open("user_fail.txt", "wt",encoding='utf-8')
fetch(topic_url)
#file_success.close()
#file_fail.close()
"""
conn = mysql.connector.connect(user='zhihu', password='zhihu', database='zhihu')
cursor = conn.cursor()
fetch(topic_url)
conn.commit()
cursor.close()
conn.close()
"""

t2 = time.time()
print(t2-t1)