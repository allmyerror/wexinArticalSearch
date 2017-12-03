# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     spider.py
   Description :
   Author :       Sean
   date：          2017/12/3
-------------------------------------------------
   Change Activity:
                   2017/12/3:
-------------------------------------------------
   how to use:
                   1.运行https://github.com/Python3WebSpider/ProxyPool的代理池工具
                   2.自定义config.py配置文件
                   3.使用微信登陆http://weixin.sogou.com/weixin，并修改init_page函数的headers信息
                   4.运行本程序
-------------------------------------------------
"""

import requests
from bs4 import BeautifulSoup
from config import *
from pyquery import PyQuery as pq
import pymongo

# 初始化mongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

# 初始化proxy为空
proxy = None


def get_proxy():
    try:
        url = 'http://localhost:5555/random'
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
        return None
    except ConnectionError:
        return None


def init_page(pageNum, count=1):
    # original access
    url = 'http://weixin.sogou.com/weixin'
    # query string for the Request
    params = {
        "query": KEYWORD,
        "type": "2",
        "page": str(pageNum),
        "ie": "utf8"
    }
    # 插入cookie到header，维持会话，需要定期更新
    headers = {
        "Cookie": "IPLOC=CN3201; SUID=130ACEB71F13940A000000005A2393A9; SUV=1512281005297416; ABTEST=0|1512281005|v1; weixinIndexVisited=1; JSESSIONID=aaaMQIN_TkwuF81cuOv8v; ppinf=5|1512281985|1513491585|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZToxNTpLZWVwJTIwdGhpbmtpbmd8Y3J0OjEwOjE1MTIyODE5ODV8cmVmbmljazoxNTpLZWVwJTIwdGhpbmtpbmd8dXNlcmlkOjQ0Om85dDJsdVA4M3ZEYUZNVk9LS2JzU2FyeWRhZEVAd2VpeGluLnNvaHUuY29tfA; pprdig=Kb7qvwwz9pQ0D4Auvhe-_bU9nsLnJqiwW3UDnJpADAGznY292kRea3AOfef-K-97THNnd2Un3Ihdtaggo74DhOh_bhsJ5_Bf009cC3i3FEPkHEkt46mHMxB28VBgQi6D2sr2dSYvOtt_WnkFqxpiOXUxZXDkaan4btsRo-CiGfM; sgid=07-30164517-AVojl4G6JqoRUsU0icnv8avA; PHPSESSID=mf8jglp1o6ta6la8rs9t05ura7; SUIR=445C99E15653093E0A74461C570BA1FA; sct=2; ppmdig=1512301905000000c965b1c19699b0d6a14e48ffab13b916; SNUID=3923E79E292F76474E48CE652AF08452; seccodeRight=success; successCount=1|Sun, 03 Dec 2017 12:08:41 GMT",
        "Host": "weixin.sogou.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    }
    global proxy
    print('******************************************************************************')
    print('*     使用代理*{0}*爬取中，初始化{1}页，第{2}次尝试...     *'.format(proxy, pageNum, count))
    print('******************************************************************************')
    if count >= MAXCOUNT:
        print('达到最大尝试次数，程序结束')
        return None
    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy
            }
            response = requests.get(url, params=params, headers=headers, allow_redirects=False, proxies=proxies,
                                    timeout=15)
        else:
            response = requests.get(url, params=params, headers=headers, allow_redirects=False)
        if response.status_code == 200:
            # print(pageNum, '请求成功', response.status_code)
            return response.text
        if response.status_code == 302:
            print('CODE = 302:重定向，需要使用代理访问.....')
            proxy = get_proxy()
            if proxy:
                return init_page(pageNum)
            else:
                print('使用代理失败，程序终止')
                return None
    except Exception as e:
        print('发生错误', e, '尝试切换代理')
        proxy = get_proxy()
        count += 1
        return init_page(pageNum, count)


def get_wexin_url(html):
    soup = BeautifulSoup(html, 'lxml')
    items = soup.select(".news-box .news-list li")
    for item in items:
        yield item.find(target="_blank")['href']


def parse_wexin_url(url):
    html = requests.get(url).text
    doc = pq(html)
    wexinArticleAttrs = {
        'articleTitle': doc("#activity-name").text(),
        # 'originalTag': doc("#copyright_logo").text(),
        'postDate': doc("#post-date").text(),
        # 'authorNickName': doc("#meta_content > em:nth-child(3)").text(),
        'officialAccount': doc("#js_profile_qrcode > div > strong").text(),
        'officialAccountWeChatID': doc("#js_profile_qrcode > div > p:nth-child(3) > span").text(),
        'articleText': doc("#js_content").text()
    }
    return wexinArticleAttrs


def save_to_mongo(data):
    try:
        if db[MONGO_TABLE].insert_one(data):
            print('存储到MongoDB成功...', data['articleTitle'])
    except Exception as e:
        print('存储到MongoDB失败...', e, data['articleTitle'])


def main():
    for pageNum in range(1, 101):
        html = init_page(pageNum)
        if html:
            urlList = get_wexin_url(html)
            for url in urlList:
                data = parse_wexin_url(url)
                if data:
                    save_to_mongo(data)


if __name__ == '__main__':
    main()
