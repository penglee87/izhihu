#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests,sys,os,json,re,time
from bs4 import BeautifulSoup as BS
from queue import Queue
import asyncio
import aiohttp
"""
爬取话题关注人数并判断话题ID是否是最末端话题
"""

@asyncio.coroutine
def topic_info(topic_id):
    try:
        url = 'https://www.zhihu.com/topic/' + topic_id
        response = yield from session.get(url, allow_redirects=True)
        if response.status == 200:
            r = yield from response.text()
            topic_name = re.search(r'data-disabled="1">(.*?)</h1>',r).group(1)
            if re.search(r'<strong>(.*?)</strong> 人关注了该话题',r):
                followers = re.search(r'<strong>(.*?)</strong> 人关注了该话题',r).group(1)
            else:
                followers = '0'
            if re.search(r'"zm-topic-side-organize-title">子话题', r):
                result_list.append((topic_id,topic_name,'1',followers))
            else:
                result_list.append((topic_id,topic_name,'0',followers))
        else:
            result_list.append((topic_id,'tryagain',str(response.status)))
    finally:
        yield from response.release()
    #return result_list
    

def list2file(topics_list):
    f_obj = open('topics_again2.csv', 'w',encoding='utf-8') # w 表示打开方式
    title = ['topic_id','topic_name','have_child', 'followers']
    html = '\t'.join(title)+ '\n'    
    for topic in topics_list:
        html += '\t'.join(topic) + '\n'
    f_obj.write(html)
    f_obj.close()  

    
max_tasks = 10
result_list = []    
topic_list = []
with open('again2.txt', 'r') as f:
    for line in f.readlines():
        topic_list.append(line.strip('\n'))
#topic_list = topic_list[:50]
#topic_list = ['19840694','19553622']


loop = asyncio.get_event_loop()
with aiohttp.ClientSession(loop=loop) as session:
    for i in range(int(len(topic_list)/max_tasks)+1):
        tasks = [topic_info(topic_id) for topic_id in topic_list[i*max_tasks:(i+1)*max_tasks]]
        loop.run_until_complete(asyncio.wait(tasks))
    list2file(result_list)