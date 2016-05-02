#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import time
import datetime
import json
import os
import re
import sys
import subprocess
from bs4 import BeautifulSoup as BS
"""
从自己关注的人开始，递归遍历关注的人所关注的人，并提取他们粉丝数
"""

def get_followees(url):
    follows = [] 
    url_content = requests.get(url).text
    soup = BS(url_content, 'html.parser') # 开始解析 
    followeetable = soup.find_all('div',attrs={"class": "zm-profile-card zm-profile-section-item zg-clear no-hovercard"})

    # 循环遍历关注列表
    for simplefollowee in followeetable:
        subsoup = BS(str(simplefollowee), 'html.parser') # 
        user_name = subsoup.a['title'] #
        urer_url = subsoup.h2.a['href'] + '/followers'
        follow_num = subsoup.find(text=re.compile("关注者")).string.strip(' 关注者')
        follows.append((user_name, follow_num,urer_url))        
    return follows


#读取cookie文件，返回反序列化后的dict对象，没有则返回None
def loadCookie(cookieFile):
    if os.path.exists(cookieFile):
        print("=" * 50)
        with open(cookieFile, "r") as f:
            cookie = json.load(f)
            return cookie
    return None
    

def saveFile(data,file_name):
    """
    保存文件
    """
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    save_path = os.path.join(sys.path[0], file_name+".csv")
    f_obj = open(save_path, 'w',encoding='gbk') # w 表示打开方式
    title = ['用户名','关注者','链接']
    html = '\t'.join(title)+ '\n'
    for page in data:
        for luntai in page:
            html += '\t'.join(luntai) + '\n'
    f_obj.write(html)
    f_obj.close()
    

requests = requests.Session()    
cookieFile = os.path.join(sys.path[0], "cookie")        
cookie = loadCookie(cookieFile)
if cookie:
    print("检测到cookie文件,直接使用cookie登录")
    requests.cookies.update(cookie)
    soup = BS(requests.get(r"http://www.zhihu.com/").text, "html.parser")
    print("已登陆账号： %s" % soup.find("span", class_="name").get_text())
else:
    print("没有找到cookie文件，请调用login方法登录一次！")
    
followss_list = []   
url = 'https://www.zhihu.com/people/lee-82-75-31/followees'
follows = get_followees(url)
followss_list.append(follows)  #元组构成的列表构成的列表[[(),()],[(),()]]

for x in range(5):  #递归多少层
#while len(followss_list)<500:
    for url_table in followss_list[-1]:
        urll = url_table[2]
        followss_list.append(get_followees(urll))
   
    
saveFile(followss_list,"zhihu_followees")
