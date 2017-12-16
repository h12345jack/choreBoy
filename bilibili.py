#coding=utf8
import time
import json
import re
import os

import requests
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

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


if not os.path.exists("tsv"):
    os.mkdir("tsv")

class comment_rendered(object):
  """An expectation for checking that an element has a particular css class.

  locator - used to find the element
  returns the WebElement once it has the particular css class
  """
  def __init__(self, locator):
    self.locator = locator

  def __call__(self, driver):
    element = driver.find_element(*self.locator)   # Finding the referenced element
    value = element.text
    if driver.find_element_by_xpath('//div[@class="baffle"]'):
        return True
    return len(value.strip()) > 0


class BilibiliTask(object):
    """docstring for BilibiliTask"""
    def __init__(self):
        super(BilibiliTask, self).__init__()
        self.init_phantomjs()
        self.init_chrome()


    def init_phantomjs(self):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        )
        self.phantom_driver = webdriver.PhantomJS('./phantomjs/phantomjs.exe',service_args=['--load-images=no','--disk-cache=yes','--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'], desired_capabilities=dcap)
        self.phantom_driver.set_page_load_timeout(5)

    def init_chrome(self):
        profile_dir = r'C:\Users\Jackhuang\AppData\Local\Google\Chrome\User Data'
        option = webdriver.ChromeOptions()
        option.add_argument("--disable-extensions")
        option.add_argument(r'--user-data-dir='+os.path.abspath(profile_dir)) 
        self.chrome_driver = webdriver.Chrome('./phantomjs/chromedriver.exe',chrome_options=option)

    def getHtml(self, aid):
        url = "https://www.bilibili.com/video/av{}/".format(aid)
        time_try = 20
        while time_try:
            try:
                self.phantom_driver.get(url.strip())
                self.phantom_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                element = WebDriverWait(self.phantom_driver, 10).until(
                    comment_rendered((By.XPATH, '//span[@class="b-head-t results"]'))
                )

            except Exception as e:
                print(url, e)
                time_try -= 1
                time.sleep(1.5)
                try:
                    content = self.phantom_driver.page_source.encode('utf8')
                except Exception as e:
                    content = ''
                    #用chrome浏览器
                self.phantom_driver.quit()
                self.init_phantomjs()
                if str(content).find('class="error-container"') > -1:
                    self.chrome_driver.get(url.strip())
                    self.chrome_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    element = WebDriverWait(self.chrome_driver, timeout=10).until(
                        comment_rendered((By.XPATH, '//span[@class="b-head-t results"]'))
                    )
                    content_chrome = self.chrome_driver.page_source.encode('utf8')
                    with open('./htmls/{}.html'.format(aid), 'wb') as f:
                            f.write(content_chrome)
                    item = dict()
                    dom = html.fromstring(content_chrome)
                    collect_xpath = '//div[@id="arc_toolbar_report"]/'
                    item["collect"] = "".join([i for i in dom.xpath('//span[@class="t fav_btn"]/@title')])
                    item["coins2"] = "".join([i for i in dom.xpath('//div[@class="block coin"]//span[@class="t"]/@title')])
                    item["share"] = "".join([i for i in dom.xpath('//div[@class="share-tool-bar"]//span[@class="num"]/@title')])
                    item["comment"] = "".join([i for i in dom.xpath('//span[@class="b-head-t results"]/text()')])
                    item["breadcrumb"] = "".join([i for i in dom.xpath('//div[@class="tminfo"]//text()')])
                    if item["collect"]:
                        return item
                else:
                    print(aid, 'continue!')
                    continue
            else:
                content = self.phantom_driver.page_source.encode('utf8')

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
                if item["collect"]:
                    print(aid,item["breadcrumb"])
                    return item
                # else:
                # time.sleep(2)
                # continue

    def getRank(self):
        '''json数据
        parts = ["all-30-0","all-30-1","all-30-168","all-30-3","all-30-129","all-30-4",\
                 "all-30-36","all-30-160","all-30-119","all-30-155","all-30-5","all-30-181"]


        '''

        parts = ["all-30-0","all-30-1","all-30-168","all-30-3","all-30-129","all-30-4",\
                 "all-30-36","all-30-160","all-30-119","all-30-155","all-30-5","all-30-181"]
        # parts = ["all-30-0"]

        for part in parts:
            if os.path.exists('{}-top100.tsv'.format(part)):
                continue
            url = 'https://www.bilibili.com/index/rank/{}.json'.format(part)
            print(url)
            req = requests.get(url, headers = HEADERS1)
            content = req.content
            now = time.time()
            with open('{}.json'.format(part),'wb') as f:
                f.write(content)
            json_data = json.loads(content, encoding='utf8')
            data = json_data["rank"]["list"]
            for item in data:
                aid = item["aid"]
                item2 = self.getHtml(aid)
                for tmp in item2:
                    item[tmp] = item2[tmp]
                times_try = 100
                self.getVideoTags(aid)
                while times_try:
                    try:
                        self.getTagLog(aid)
                    except:
                        times_try -=1
                    else:
                        break

                print(aid)
                # break
            df = pd.DataFrame(data)
            df.to_csv('{}-top100.tsv'.format(part), sep='\t')
            print(part, 'done!')
            time.sleep(5)



    def getVideoTags(self, aid):
        url = "http://api.bilibili.com/x/tag/archive/tags?aid={}&jsonp=jsonp".format(aid)
        req = self.chrome_driver.get(url.strip())
        html_page = self.chrome_driver.page_source.encode('utf8')
        f_path = os.path.join('htmls', aid+'-tags.html')
        with open(f_path, 'wb') as f:
            f.write(html_page)

        dom = html.fromstring(html_page.decode('utf8')) 
        content = dom.xpath("//pre/text()")[0]  
        json_data = json.loads(content, encoding='utf8')

        f_path = os.path.join('jsons', aid+'-tags.json')
        with open(f_path, 'w') as f:
            f.write(json.dumps(json_data))
        data = json_data["data"]
        df = pd.DataFrame(data)
        df.to_csv('./tsv/{}-tags.tsv'.format(aid), encoding='utf8',sep='\t')


    def getTagLog(self, aid):
        datas = []
        url = 'https://api.bilibili.com/x/tag/archive/log?&aid={}&pn={}&ps=20&jsonp=jsonp'
        for i in range(1,1000):
            n_url = url.format(aid, i)
            req = requests.get(n_url, headers = HEADERS2)
            content = req.content
            f_path = os.path.join('jsons', aid+'-logs-{}.json'.format(i))
            with open(f_path, 'wb') as f:
                f.write(content)
            json_data = json.loads(content, encoding='utf8')
            data = json_data["data"]
            if isinstance(data,list) and len(data)>0:
                datas.extend(data)
                continue
            else:
                break
        df = pd.DataFrame(datas)
        df.to_csv('./tsv/{}-logs.tsv'.format(aid), sep='\t')

    def quit(self):
        self.phantom_driver.quit()
        self.chrome_driver.quit()



def validate():
    aid_rs = []
    f_lists = [i for i in os.listdir('.') if i.find('.tsv') > -1]
    for fname in f_lists:
        print(fname)
        df = pd.read_csv(fname, sep='\t')
        aids = df["aid"].tolist()
        aid_rs.extend(aids)
        for aid in aids:
            a = os.path.exists("./tsv/"+str(aid)+"-logs.tsv")
            b = os.path.exists("./tsv/"+str(aid)+"-tags.tsv")
            if (not a) or (not b):
                print(aid)
    from collections import Counter
    c = Counter(aid_rs)
    for i in c:
        if c[i] > 1:
            print(i)




def main():
    # bili = BilibiliTask()
    # bili.getRank()
    # # item = bili.getHtml(aid='16418759')
    # # print(item)
    # bili.quit()
    validate()


if __name__ == '__main__':
    main()