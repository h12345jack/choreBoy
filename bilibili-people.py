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
from selenium.webdriver.support import expected_conditions as EC

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

if not os.path.exists("people"):
    os.mkdir("people")

class favlist_rendered(object):
  """An expectation for checking that an element has a particular css class.

  locator - used to find the element
  returns the WebElement once it has the particular css class
  """
  def __init__(self, locator1, locator2):
    self.locator1 = locator1
    self.locator2 = locator2

  def __call__(self, driver):
    print(driver.find_element_by_xpath(self.locator1))
    ele1 = driver.find_element_by_xpath(self.locator1)   # Finding the referenced element
    ele2 = dirver.find_element_by_xpath(self.locator2)
    return ele1 or ele2


class BilibiliPeopleTask(object):
    """docstring for BilibiliTask"""
    def __init__(self):
        super(BilibiliPeopleTask, self).__init__()
        self.init_phantomjs()
        self.init_phantomjs2()


    def init_phantomjs(self):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        )
        self.phantom_driver = webdriver.PhantomJS('./phantomjs/phantomjs.exe',service_args=['--load-images=no','--disk-cache=yes','--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'], desired_capabilities=dcap)
        self.phantom_driver.set_page_load_timeout(10)

    def init_phantomjs2(self):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        )
        self.phantom_driver2 = webdriver.PhantomJS('./phantomjs/phantomjs2.exe',service_args=['--load-images=no','--disk-cache=yes','--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'], desired_capabilities=dcap)
        self.phantom_driver2.set_page_load_timeout(10)
   
    def getHtml(self, mid):
        url = "https://space.bilibili.com/{}#/".format(mid)
        time_try = 20
        while time_try:
            try:
                self.phantom_driver.get(url.strip())
                self.phantom_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                element = WebDriverWait(self.phantom_driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="s-space"]'))
                )
            except Exception as e:
                print(url, e)
                time_try -= 1
                time.sleep(1.5)
                self.phantom_driver.quit()
                self.init_phantomjs()
            else:
                content = self.phantom_driver.page_source.encode('utf8')
                with open('./people/{}.html'.format(mid), 'wb') as f:
                        f.write(content)

                dom = html.fromstring(content)

                item = dict()

                item['user_id'] = mid

                
                # 用户ID, 性别，注册时间
                male_xpath = '//*[@id="h-gender"]/@class'
                male = "".join([i for i in dom.xpath(male_xpath)])
                item['gender'] = 'male' if male.find('male') > -1 else 'female'

                register_time_xpath = '//div[@class="item regtime"]//text()'

                item['regtime'] =  "".join([i.strip() for i in dom.xpath(register_time_xpath) if i.strip()])

                guanzhu_xpath = '//a[@class="n-data n-gz"]/@title'
                guanzhu = [i for i in dom.xpath(guanzhu_xpath)]
                if len(guanzhu) > 0:
                    item['guanzhu'] = guanzhu[0]

                fan_xpath = '//a[@class="n-data n-fs"]/@title'
                fan = [i for i in dom.xpath(fan_xpath)]
                if len(fan) > 0:
                    item['fan'] = fan[0]


                bofang_xpath = '//a[@class="n-data n-bf"]/@title'
                bofang = [i for i in dom.xpath(bofang_xpath)]
                if len(bofang) > 0:
                    item['bofang']= bofang[0]


                # 关注数，粉丝数,收藏视频数

                #收藏视频数、视频数、用户等级
                vip_xpath = '//a[@class="h-level m-level"]/@lvl'
                item['vip'] = "".join([i for i in dom.xpath(vip_xpath)])                
                
                video_xpath = '//a[contains(@class,"n-video")]/span[@class="n-num"]/text()'
                video = [i.strip() for i in dom.xpath(video_xpath) if i.strip()]
                if len(video) > 0:
                    item['video'] = video[0]

                channel_xpath ='//a[contains(@class, "n-channel")]/span[@class="n-num"]/text()'
                channel = [i.strip() for i in dom.xpath(channel_xpath) if i.strip()]
                if len(channel) > 0:
                    item['channel'] = channel[0]

                zhuanlan_xpath = '//a[contains(@class, "n-article")]/span[@class="n-num"]/text()'
                zhuanlan = [i.strip() for i in dom.xpath(zhuanlan_xpath) if i.strip()]
                if len(zhuanlan) > 0:
                    item["zhuanlan"] = zhuanlan[0]

                dingyue_xpath = '//h3[@class="section-title"]' 
                dingyue = []
                except_list = ['代表作', '更多','仅自己可见', '公告', '最近玩过的游戏', '直播间',"最新发布","最多播放","最多收藏"]
                for dy in dom.xpath(dingyue_xpath):
                    k_v = ":".join([i.strip() for i in dy.xpath('.//text()') if i not in except_list and len(i.strip())>0])
                    if k_v:
                        dingyue.append(k_v)

                item['dingyue'] = ";".join(dingyue)
                item['collection_num'] = self.getCollectNumber(mid)
                return item



    def getCollectNumber(self, mid):
        url = 'https://space.bilibili.com/{}#/favlist'.format(mid)
        time_try = 20
        while time_try:
            try:
                self.phantom_driver2.get(url.strip())
                self.phantom_driver2.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                element = WebDriverWait(self.phantom_driver2, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//ul[@class="fav-list"]/li'))
                    # favlist_rendered('//div[@class="wrapper guest full-fav-empty"]','//ul[@class="fav-list"]')
                )
            except Exception as e:
                print(url, e)
                time_try -= 1
                time.sleep(1.5)
                self.phantom_driver2.quit()
                self.init_phantomjs2()
            else:
                content = self.phantom_driver2.page_source.encode('utf8')
                with open('./people/{}-favlist.html'.format(mid), 'wb') as f:
                        f.write(content)
                li_xpath = '//ul[@class="fav-list"]/li'
                dom = html.fromstring(content)
                count_sum = 0
                for li in dom.xpath(li_xpath):
                    v = "".join([i for i in li.xpath('.//span[@class="num"]/text()')])
                    count_sum += int(v)

                return count_sum




    def quit(self):
        self.phantom_driver.quit()




def get_people_list():
    f_list =[os.path.join('tsv', i) for i in os.listdir('./tsv')] 
    mids = []
    for f_path in f_list:
        with open(f_path) as f:
            df = pd.read_csv(f, sep='\t')
            mids.extend(df['mid'])


def getUsers():
    f_lists =[os.path.join('tsv', i) for i in os.listdir('./tsv') if i.find('log') > -1] 
    mid_rs = []
    for fname in f_lists:
        df = pd.read_csv(fname, sep='\t')
        if 'mid' in df:
            mids = df["mid"].tolist()
            mid_rs.extend(mids)
        else:
            print(fname)
    mid_rs = list(set(mid_rs))
    print(len(mid_rs))

    return mid_rs

def main():
    test = ['9331087', '777536', '31273277']
    v = [198, 0, 68]
    user_list = getUsers()


    # userlist
    bili = BilibiliPeopleTask()
       
    for user in user_list:
        user_json_path = os.path.join('people_json', str(user)+'.json')
        if not os.path.exists(user_json_path):
            with open(user_json_path, 'w') as f:
                item = bili.getHtml(user)
                f.write(json.dumps(item) + '\n')
                print(user, 'done')


    # # item = bili.getCollectNumber(9331087)
    # item = bili.getHtml(16105473)
    # item = bili.getHtml(777536)

    print(item)
    # # bili.getHtml(aid='16874218')
    bili.quit()

if __name__ == '__main__':
    main()