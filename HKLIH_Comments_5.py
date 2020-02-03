# -*- coding: utf-8 -*-
"""
Created on Sat Aug 03 15:04:58 2019

@author: Dr Hai Liang
"""
# add refere

import requests
import pandas as pd
import time,random

for i in range(1553401,1564800):
    cp = 0
    tp = 1
    while cp < tp:
        cp = cp+1
        url = "https://lihkg.com/api_v2/thread/"+str(i)+"/page/"+str(cp)+"?order=reply_time"
        my_referer = "https://lihkg.com/thread/"+str(i)+"/page/"+str(cp)
        #url = "https://lihkg.com/api_v2/thread/1100000/page/1?order=reply_time"
        
        try:
            page = requests.get(url,headers={'referer': my_referer,'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'})
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
            comments['like_count'] = threads['like_count']
            comments['dislike_count'] = threads['dislike_count']
            comments['create_time'] = threads['create_time']
            comments['last_reply_time'] = threads['last_reply_time']
            comments['total_page'] = threads['total_page']
            comments['page'] = threads['page']
            
            cp = int(threads['page'])
            tp = int(threads['total_page'])
            comments.to_csv('comments5.csv', header=True, index=None, mode='a', encoding='utf-8')
            time.sleep(random.randint(1,3))
        except Exception as e:
            print(e)
            print(data)
            time.sleep(random.randint(4,9))
        
        print(str(i))
        
        