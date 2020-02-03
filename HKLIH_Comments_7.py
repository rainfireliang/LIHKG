# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 14:42:39 2019

@author: user
"""


from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import requests
import pandas as pd
import time,random

## selenium manually verify

binary = r'C:/Program Files/Mozilla Firefox/firefox.exe'
options = Options()
options.binary = binary
cap = DesiredCapabilities().FIREFOX
cap["marionette"] = True #optional
driver = webdriver.Firefox(options=options, capabilities=cap, executable_path="E:/geckodriver.exe")
driver.get("https://lihkg.com/thread/1637586/page/1")

###
for i in range(1599888,1638226):
    cp = 0
    tp = 1
    while cp < tp:
        cp = cp+1
        url = "https://lihkg.com/api_v2/thread/"+str(i)+"/page/"+str(cp)+"?order=reply_time"
        my_referer = "https://lihkg.com/thread/"+str(i)+"/page/"+str(cp)
        #url = "https://lihkg.com/api_v2/thread/1100000/page/1?order=reply_time"
        
        try:
            driver.get(my_referer)
            s = requests.Session()
            cookies = driver.get_cookies()
            for cookie in cookies:
                s.cookies.set(cookie['name'], cookie['value'])
            
            page = s.get(url,headers={'Referer': my_referer,'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'})            
            #page = requests.get(url,headers={'referer': my_referer,'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'})
            data = page.json()
        
            # thread
            threads = data['response']
            
            # comments
            comments = data['response']['item_data']
            comments = pd.DataFrame(comments)
            
            comments['title'] = threads['title']
            comments['cat_id'] = threads['category']['cat_id']
            comments['name'] = threads['category']['name']
            comments['no_of_reply'] = threads['no_of_reply']
            comments['no_of_uni_user_reply'] = threads['no_of_uni_user_reply']
            comments['like_count_thread'] = threads['like_count']
            comments['dislike_count_thread'] = threads['dislike_count']
            comments['create_time'] = threads['create_time']
            comments['last_reply_time'] = threads['last_reply_time']
            comments['total_page'] = threads['total_page']
            comments['page'] = threads['page']
            
            cp = int(threads['page'])
            tp = int(threads['total_page'])
            comments.to_csv('comments7.csv', header=True, index=None, mode='a', encoding='utf-8')
            time.sleep(random.randint(1,2))
        except Exception as e:
            print(e)
            print(data)
            time.sleep(random.randint(2,3))
        
        print(str(i))













driver.quit()
