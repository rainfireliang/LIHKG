# -*- coding: utf-8 -*-
"""
Created on Sat Aug 03 15:04:58 2019

@author: Dr Hai Liang
"""

import json
import os.path
import random
import string
import pandas as pd

from typing import Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def random_string() -> str:
    '''
    Generate a random string that is suitable to be an identifier.
    '''

    length = random.randrange(10, 20)
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def get_next_page_from_json(obj: object, thread_id: int, page: int) -> Tuple[int, int]:
    '''
    Determine the next `thread_id` and `page` from the JSON object.
    If the current value of `page` is equal to `total_page`, we go to the next thread.
    Otherwise we increment the value of `page`.
    '''

    if 'response' not in obj:
        return thread_id + 1, 1

    total_pages = obj['response'].get('total_page', 0)
    if page >= total_pages:
        return thread_id + 1, 1

    return thread_id, page + 1

def get_resume_position(filename: str, from_thread: int) -> Tuple[int, int]:
    if not os.path.exists(filename):
        return from_thread, 1

    with open(filename) as f:
        for line in f:
            pass  # locate the last line
    thread_id_str, page_str, obj_str = line.rstrip('\n').split('\t')
    thread_id = int(thread_id_str)
    page = int(page_str)
    obj = json.loads(obj_str)  # will throw an exception if the string is not a valid json object

    thread_id_new, page_new = get_next_page_from_json(obj, thread_id, page)
    print('INFO: Resuming from thread', thread_id_new, 'page', page_new)
    return thread_id_new, page_new

def init_browser() -> WebDriver:
    options = webdriver.ChromeOptions()
    options.add_argument('start-maximized')
    options.add_argument('disable-blink-features=AutomationControlled')
    s=Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=s,options=options)
    return browser

def init_lihkg_context(browser: WebDriver) -> WebElement:
    '''
    We need to open a LIHKG page and then jump to the API URL.
    This process is wrapped as the LIHKG context.
    '''

    browser.get('https://lihkg.com/thread/2256553/page/1')
    body = WebDriverWait(browser, timeout=5).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )
    element_id = random_string()
    browser.execute_script(f'a = document.createElement("a"); a.id = arguments[1]; a.target = "_blank"; arguments[0].appendChild(a)', body, element_id)
    context = browser.find_element(By.ID, element_id)
    return context

def get_json(browser: WebDriver, context: WebElement, url: str) -> object:
    browser.execute_script('arguments[0].href = arguments[1]', context, url)
    browser.execute_script('arguments[0].click()', context)
    browser.switch_to.window(browser.window_handles[1])
    pre = WebDriverWait(browser, timeout=5).until(
        EC.presence_of_element_located((By.TAG_NAME, 'pre'))
    )
    text = pre.text
    obj = json.loads(text)
    browser.close()
    browser.switch_to.window(browser.window_handles[0])
    return obj

def get_json_of_position(browser: WebDriver, context: WebElement, thread_id: int, page: int) -> object:
    url = f'https://lihkg.com/api_v2/thread/{thread_id}/page/{page}?order=reply_time'
    obj = get_json(browser, context, url)
    return obj

def minimize_json(obj: object) -> str:
    '''
    Return the most compact representation of a JSON object.
    '''

    return json.dumps(obj, separators=(',', ':'), ensure_ascii=False)

def json_csv(data):
    try:
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
        pass   
        comments.to_csv('comments20.csv', header=True, index=None, mode='a', encoding='utf-8') #20/21/22
    except:
        pass


def start_browser(thread_id: int, to_thread: int, page: int):
    browser = init_browser()
    context = init_lihkg_context(browser)

    has_exception = False

    try:
        while thread_id < to_thread:
            obj = get_json_of_position(browser, context, thread_id, page)
            json_csv(obj)
            thread_id_new, page = get_next_page_from_json(obj, thread_id, page)
            if thread_id_new > thread_id:
                thread_id = thread_id_new
                print(str(thread_id))
    except (TimeoutException, WebDriverException):
        has_exception = True

    browser.quit()
    return has_exception, thread_id, page

thread_id = 2348830
to_thread = 2370290
page = 1            

while True:
    has_exception, thread_id, page = start_browser(thread_id, to_thread, page)
    if not has_exception:
        break
