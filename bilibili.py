#coding=utf8
import time
import json
import re
import os

import requests
import pandas as pd
from selenium import webdriver
from lxml import html

HEADERS1 = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "www.bilibili.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
}


HEADERS2 = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "api.bilibili.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
}


if not os.path.exists("htmls"):
    os.mkdir("htmls")


if not os.path.exists("jsons"):
    os.mkdir("jsons")


if not os.path.exists("excels"):
    os.mkdir("excels")

def getHtml(aid, driver):
    url = "https://www.bilibili.com/video/av{}/".format(aid)
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    content = driver.page_source.encode('utf8')
    with open('./htmls/{}.html'.format(aid), 'wb') as f:
            f.write(content)
    item = dict()
    dom = html.fromstring(content)
    collect_xpath = '//div[@id="arc_toolbar_report"]/'
    item["collect"] = "".join([i for i in dom.xpath('//span[@class="t fav_btn"]/@title')])
    item["coins2"] = "".join([i for i in dom.xpath('//div[@class="block coin"]//span[@class="t"]/@title')])
    item["share"] = "".join([i for i in dom.xpath('//div[@class="share-tool-bar"]//span[@class="num"]/@title')])
    item["comment"] = "".join([i for i in dom.xpath('//span[@class="b-head-t results"]/text()')])
    item["breadcrumb"] = "".join([i for i in dom.xpath('//div[@class="tminfo"]//text()')])
    return item

def getRank():
    '''json数据'''
    url = 'https://www.bilibili.com/index/rank/all-07-0.json'
    req = requests.get(url, headers = HEADERS1)
    content = req.content
    now = time.time()
    with open('all-07-0.json','wb') as f:
        f.write(content)
    json_data = json.loads(content)
    data = json_data["rank"]["list"]
    driver=webdriver.PhantomJS('./phantomjs/phantomjs.exe',service_args=['--load-images=no','--disk-cache=yes'])
    for item in data:
        aid = item["aid"]
        item2 = getHtml(aid, driver)
        for tmp in item2:
            item[tmp] = item2[tmp]
        getVideoTags(aid)
        getTagLog(aid)
        print(aid)
        # break

    df = pd.DataFrame(data)
    df.to_excel('top100.xlsx')




def getVideoTags(aid):
    url = "http://api.bilibili.com/x/tag/archive/tags?aid={}&jsonp=jsonp".format(aid)
    req = requests.get(url.strip(), headers = HEADERS2)
    content = req.content
    print(content)
    f_path = os.path.join('jsons', aid+'-tags.json')
    with open(f_path, 'wb') as f:
        f.write(content)
    json_data = json.loads(content)
    data = json_data["data"]
    df = pd.DataFrame(data)
    df.to_excel('./excels/{}-tags.xlsx'.format(aid))

def getTagLog(aid):
    datas = []
    url = 'https://api.bilibili.com/x/tag/archive/log?&aid={}&pn={}&ps=20&jsonp=jsonp'
    for i in range(1,1000):
        n_url = url.format(aid, i)
        req = requests.get(n_url, headers = HEADERS2)
        content = req.content
        f_path = os.path.join('jsons', aid+'-logs-{}.json'.format(i))
        with open(f_path, 'wb') as f:
            f.write(content)
        json_data = json.loads(content)
        data = json_data["data"]
        if isinstance(data,list) and len(data)>0:
            datas.extend(data)
            continue
        else:
            break
    df = pd.DataFrame(datas)
    df.to_excel('./excels/{}-logs.xlsx'.format(aid))



def main():
    # getRank()
    # getTagLog("15751210")
    getVideoTags("15751210")


if __name__ == '__main__':
    main()