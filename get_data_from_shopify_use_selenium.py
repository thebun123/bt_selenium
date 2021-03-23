import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from argparse import Namespace
import time
import requests
from urllib.parse import urlparse
import os

DELAY = 15
URL = 'https://truongnxx.myshopify.com'
EMAIL = 'thebun1234@gmail.com'
PASSWD = 'Lite2021'
API_VERSION = '2020-10'

def url_process(func):
    def wrapper(*args, **kwargs):
        requires = ['url']
        for require in requires:
            if require not in kwargs:
                return False
        u = urlparse(kwargs['url'])
        kwargs['url'] = os.path.join(f'{u.scheme}://', u.netloc, 'admin')

        return func(*args, **kwargs)

    return wrapper

@url_process
def get_cookies(*args, **kwargs):
    """Get cookies from Shopify shopping site"""
    browser = webdriver.Chrome()
    browser.get(kwargs['url'])
    try:
        time.sleep(5)
        WebDriverWait(browser, DELAY).until(ec.presence_of_element_located((By.CLASS_NAME, 'ui-button--primary')))
        email_field = browser.find_element_by_id('account_email')
        email_field.send_keys(kwargs['email'])
        next_btn = browser.find_element_by_class_name('ui-button--primary')
        next_btn.click()
        time.sleep(5)
    except TimeoutException:
        print("Loading took too much time!")

    try:
        WebDriverWait(browser, DELAY).until(ec.presence_of_element_located((By.CLASS_NAME, 'ui-button--primary')))
        account_password = browser.find_element_by_id('account_password')
        account_password.send_keys(kwargs['passwd'])

        next_btn = browser.find_element_by_class_name('ui-button--primary')
        next_btn.click()
        print("Login completed!")
    except TimeoutException:
        print("Loading took too much time!")
    cookies = browser.get_cookies()
    browser.quit()
    return cookies


@url_process
def get_entity(*args, **kwargs):
    """Get entity from shopify via api depend cookies"""

    n = Namespace(**kwargs)
    if 'id' in n:
        entity = f'{n.entity}.json?id={n.id}'
    elif 'since_id' in n:
        if 'limit' in n:
            entity = f'{n.entity}.json?since_id={n.since_id}&limit={n.limit}'
        else:
            entity = f'{n.entity}.json?since_id={n.since_id}'
    else:
        entity = f'{n.entity}.json'
    real_url = os.path.join(n.url, 'api', n.api_version, entity)

    session = requests.Session()
    for cookie in n.cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    response = session.get(real_url)
    if response.status_code == 200:
        return response.text
    else:
        print('Error.')


def write_file(data, file_name='data.json'):
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)

if '__name__' == '__main__':
    cookies = get_cookies(url=URL, email=EMAIL, passwd=PASSWD)
    list_product = get_entity(url=URL, entity='products', cookies=cookies, api_version=API_VERSION)
    write_file(data=list_product, file_name='data.json')

