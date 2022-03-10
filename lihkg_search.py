import json
import random
import string
import pandas as pd

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

def get_resume_position(filename): # filename='search_results.csv'    
    d = pd.read_csv(filename)
    bottom = d.tail(1)
    q = bottom['q'].values[0]
    page = int(bottom['page'].values[0])
    return q,page

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

def get_json_of_position(browser: WebDriver, context: WebElement, q: str, page: int) -> object:
    url = f'https://lihkg.com/api_v2/thread/search?q={q}&page={page}&count=30&sort=score&type=thread'
    obj = get_json(browser, context, url)
    return obj


def json_csv(data,q,page):
    try:       
        # comments
        threads = data['response']['items']
        threads = pd.DataFrame(threads)
        threads['q'] = str(q)
        threads['page'] = page
        threads.to_csv('search_results.csv', header=True, index=None, mode='a', encoding='utf-8')
    except:
        pass


def start_browser(q, page):
    browser = init_browser()
    context = init_lihkg_context(browser)
    has_exception = False

    try:
        while page<=100:
            obj = get_json_of_position(browser, context, q, page)
            json_csv(obj,q,page)
            page = page+1

    except(TimeoutException, WebDriverException):
        has_exception = True

    browser.quit()
    return has_exception, q, page

# keywords:"打針", "疫苗", "科興", "復必泰", "BioNTech"
import urllib.parse
queries = ["打針", "疫苗", "科興", "復必泰", "BioNTech"]
queries = [urllib.parse.quote_plus(q) for q in queries]

q = queries[4]
page = 1
#q, page = get_resume_position('search_results.csv')           
while True:
    has_exception, q, page = start_browser(q, page)
    if not has_exception:
        break
