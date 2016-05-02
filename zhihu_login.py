#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
import os
import re
import sys
import subprocess
import time
from bs4 import BeautifulSoup as BS

'''
python3 登录知乎,并保存cookie
'''

# 登录
def login( username, password):
    """
    验证码错误返回：
    {'errcode': 1991829, 'r': 1, 'data': {'captcha': '请提交正确的验证码 :('}, 'msg': '请提交正确的验证码 :('}
    登录成功返回：
    {'r': 0, 'msg': '登陆成功'}
    """
    #抓包发现使用手机号登陆时,用户名的key是phone_num。登陆网址是：http://www.zhihu.com/login/phone_num
    loginURL = r"https://www.zhihu.com/login/{0}"
    loginURL = loginURL.format(getUsernameType(username))
    
    
    # 随便开个网页，获取登陆所需的_xsrf
    html = session.get(homeURL).text    
    soup = BS(html, "html.parser") 
    _xsrf = soup.find("input", {"name": "_xsrf"})["value"]
    print('_xsrf',_xsrf)
    # 下载验证码图片
    while True:
        captcha = session.get(captchaURL)
        sessionCookies = captcha.cookies
        captchacookies = session.cookies.get_dict()
        scookies = '; '.join(['='.join(item) for item in captchacookies.items()])
        #captchacookies2 = requests.utils.dict_from_cookiejar(captchacookies)
        #d=json.dumps(captchacookies)
        #f=json.loads(d)
        print('captchacookies',captchacookies)
        #print('captchacookies2',captchacookies2)
        
        with open(captchaFile, "wb") as output:
            output.write(captcha.content)
        # 人眼识别
        print("=" * 50)
        print("已打开验证码图片，请识别！")
        subprocess.call(captchaFile, shell=True)  #重开一个进程打开验证码图片
        captcha = input("请输入验证码：")
        os.remove(captchaFile)
        # 发送POST请求
        data = {
            "_xsrf": _xsrf,
            "password": password,
            "captcha": captcha,
            "remember_me": "true",
            getUsernameType(username): username,
            
        }
        headers["cookie"] = scookies   #必须,session会自动重新加载
        #session.headers = headers
        
        res = session.post(loginURL, data=data)
        #res = session.post(loginURL, data=data,cookies=sessionCookies)
        print("=" * 50)
        print(res.status_code)
        print(res.json())
        if res.json()["r"] == 0:
            print("登录成功")
            saveCookie(cookieFile)
            break
        else:
            print("登录失败")
            print("错误信息 --->", res.json()["msg"])

def getUsernameType(username):
    """判断用户名类型
    经测试，网页的判断规则是纯数字为phone_num ,其他为email
    """
    if username.isdigit():
        return TYPE_PHONE_NUM
    return TYPE_EMAIL

def saveCookie(cookieFile):
    """cookies 序列化到文件
    即把dict对象转化成字符串保存
    """
    with open(cookieFile, "w") as output:
        cookies = session.cookies.get_dict()  #requests.Session().cookies 方法
        json.dump(cookies, output)
        print("=" * 50)
        print("已在同目录下生成cookie文件：", cookieFile)

def loadCookie(cookieFile):
    """读取cookie文件，返回反序列化后的dict对象，没有则返回None"""
    if os.path.exists(cookieFile):
        print("=" * 50)
        with open(cookieFile, "r") as f:
            cookie = json.load(f)
            return cookie
    return None

        
# 网址参数是账号类型
TYPE_PHONE_NUM = "phone_num"
TYPE_EMAIL = "email"

loginURL = r"http://www.zhihu.com/login/{0}"
homeURL = r"http://www.zhihu.com"
captchaURL = r"http://www.zhihu.com/captcha.gif?r=" + str(int(time.time() * 1000)) + "&type=login"

headers = {
    "accept":"*/*",
    "accept-encoding":"gzip, deflate",
    "accept-language":"zh-CN,zh;q=0.8",
    "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
    "cookie":"",
    "origin":"https://www.zhihu.com",
    "referer":"https://www.zhihu.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.zhihu.com",
    #"Upgrade-Insecure-Requests": "1",
    "x-requested-with":"XMLHttpRequest"
}



captchaFile = os.path.join(sys.path[0], "captcha.gif")
cookieFile = os.path.join(sys.path[0], "cookie")



os.chdir(sys.path[0])  # 设置脚本所在目录为当前工作目录

session = requests.Session()
session.headers = headers

# 若已经有 cookie 则直接登录
cookie = loadCookie(cookieFile)

if cookie:
    print("检测到cookie文件,直接使用cookie登录")
    session.cookies.update(cookie)
    soup = BS(session.get(r"http://www.zhihu.com/").text, "html.parser")  
    print("已登陆账号： %s" % soup.find("span", class_="name").getText())
else:
    print("没有找到cookie文件，请调用login方法登录一次！")
    username = input("请输入用户名：")
    password = input("请输入密码：")
    login(username, password)

    