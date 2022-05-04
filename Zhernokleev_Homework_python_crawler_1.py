#!/usr/bin/env python
# coding: utf-8

import requests as rq
import bs4
from bs4 import BeautifulSoup
import os
import re
from requests.exceptions import MissingSchema, InvalidURL, ConnectionError


path_dir = os.path.join(os.getcwd(), 'data')
if not os.path.exists(path_dir):
    os.makedirs(path_dir)
path_urls = os.path.join(os.getcwd(), 'urls.txt')
print(path_dir, path_urls)

def parsing_func(url, cur_depth, depth, identifier, path_dir, path_urls):
    if cur_depth <= depth:
        try:
            if url.startswith('//'):
                url = 'https:' + url
            r = rq.get(url)
            r.encoding = 'utf-8'
        except (MissingSchema, InvalidURL):
            print(url, 'Invalid url')
        except ConnectionError:
            print('Error Connecting:')
        else:
            if r.status_code == rq.codes.ok:
                soup = BeautifulSoup(r.text)
                if os.path.isfile(path_urls):
                    with open(path_urls, 'a+') as urls:
                        urls.seek(0)
                        for line in urls:
                            if url == line.split()[1]:
                                print('url ', url, ' уже встречался')
                                return None
                        identifier = int(line.split()[0]) + 1
                        urls.write(str(identifier) + ' ' + url + '\n')
                else:
                    with open(path_urls, 'a') as urls:
                        urls.write(str(identifier) + ' ' + url + '\n')
                with open(os.path.join(path_dir, str(identifier) + '.html'), 'a',
                          encoding="utf-8") as html_f:
                    html_f.write(soup.prettify())
                for link in soup.find_all(
                        'a', attrs={'href': re.compile("(^https://|^//)")}):
                    parsing_func(link.get('href'), cur_depth + 1, depth, identifier,
                                 path_dir, path_urls)
            else:
                print(r.url, ': Ошибка ' + str(r.status_code))


print('Введите url, затем глубину обхода:')
print('url:', end='')
url = input()
print('depth:', end='')
depth = int(input())
while depth < 0:
    print('Глубина обхода не может быть отрицательна, введите depth > 0:',
          end='')
    depth = int(input())

cur_depth = 0
identifier = 1

parsing_func(url, cur_depth, depth, identifier, path_dir, path_urls)
