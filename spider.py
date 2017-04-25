# -*-coding:utf-8-*-
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from hashlib import md5
from multiprocessing import Pool
from urllib.parse import urlencode
import requests, re, os, json, threading


def get_index_page(offset):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': 20,
        'cur_tab': 1,
    }
    url = 'http://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('爬虫异常')
        return None


def parser_index_page(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for url in data.get('data'):
            yield url.get('article_url')


def get_image_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('爬虫异常')
        return None


def parser_image_page(html):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    image_src = re.compile('var gallery = (.*?);', re.S)
    result = re.search(image_src, html)
    if result:
        data = json.loads(result.group(1))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for url in images:
                down_image(url, title)
            return {
                'title': title,
                'images': images
            }


def down_image(url, title):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content, title)
        return None
    except RequestException:
        print('爬虫异常')
        return None


def save_image(content, title):
    path = 'F:/pic/' + str(title)
    if not os.path.exists(path):
        os.mkdir(path)
    file_name = '{0}/{1}.{2}'.format(path, md5(content).hexdigest(), '.jpg')
    if not os.path.exists(file_name):
        with open(file_name, 'wb') as f:
            f.write(content)
            print('保存成功', title, path)
            f.close()


def main(offset):
    html = get_index_page(offset)
    for url in parser_index_page(html):
        html = get_image_page(url)
        if html:
            parser_image_page(html)

if __name__ == '__main__':
    group = [x for x in range(1, 20)]
    pool = Pool()
    pool.map(main, group)
