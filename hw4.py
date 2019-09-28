# Практическое задание к 4 уроку курса "Методы сбора"

# Написать приложение, которое собирает основные новости с сайтов mail.ru, lenta.ru.
# Для парсинга использовать xpath. Структура данных должна содержать:
# * название источника,
# * наименование новости,
# * ссылку на новость,
# * дата публикации

from lxml import html
from pprint import pprint
import requests
from datetime import datetime
import json
from pymongo import MongoClient
import re

headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}


def requests_to_mailru():

    source = 'Mail.ru'

    try:
        request = requests.get('https://www.mail.ru/', headers=headers)
        # pprint(request.text)
        root = html.fromstring(request.text)


        links = root.xpath(
            "//div[contains(@class, 'news-item_main')]/a/@href|//div[contains(@class, 'news-item__inner')]/a[contains(@href, 'https')]/@href")
        if links:
            pass
            # pprint(links)
            # pprint(f'{len(links)} total links')
        else:
            print("At your request no main news link was found. Please check your request.")

        title = root.xpath(
            "//h3[last()]/text()|//div[contains(@class, 'news-item__inner')]/a[contains(@href, 'https')]/text()")
        if title:
            title = [i.replace('\xa0', ' ') for i in title]
            # pprint(title)
            # pprint(f'{len(title)} total titles')

        else:
            print("At your request no main news name was found. Please check your request.")

        collect_time = datetime.now()

        news_list = [{'Source': source,
                      'title': title[i],
                      'link': links[i],
                      'collect_time': collect_time
                      } for i in range(len(title))]
        # pprint(news_list)
        print(f'{len(news_list)} news collected from Mail.ru')
        for news in news_list:
            newsdb.insert_one(news)

    except requests.exceptions.ConnectionError:
        print("No connection to site")
        exit(1)


def requests_to_lentaru():

    source = 'Lenta.ru'

    try:
        request = requests.get('https://lenta.ru', headers=headers)
        # pprint(request.text)
        root = html.fromstring(request.text)

        links = root.xpath(
                        '//div[@class="item"]/a/@href|//div[@class="first-item"]/h2/a/@href'
                         )
        if links:
            for i in range(len(links)):
                if not links[i].startswith('http'):
                    links[i] = 'https://lenta.ru' + links[i]

            # pprint(links)
            # pprint(f'{len(links)} total links')
        else:
            print("At your request no main news link was found. Please check your request.")

        title = root.xpath(
            '//div[@class="item"]/a/text()|//div[@class="first-item"]/h2/a/text()')
        if title:
            title = [i.replace('\xa0', ' ') for i in title]
            # pprint(title)
            # pprint(f'{len(title)} total titles')

        else:
            print("At your request no main news name was found. Please check your request.")

        collect_time = root.xpath(
            '//div[@class="item"]/a/time/@datetime|//div[@class="first-item"]/h2/a/time/@datetime'
                         )
        while len(collect_time) < len(title):
            collect_time.append(datetime.now())

        news_list = [{'Source': source,
                      'title': title[i],
                      'link': links[i],
                      'collect_time': collect_time[i]
                      } for i in range(len(title))]
        # pprint(news_list)
        print(f'{len(news_list)} news collected from Lenta.ru')
        for news in news_list:
            newsdb.insert_one(news)

    except requests.exceptions.ConnectionError:
        print("No connection to site")
        exit(1)


client = MongoClient('mongodb://127.0.0.1:27017')
db = client['newsdb']
newsdb = db.newsdb


requests_to_mailru()
requests_to_lentaru()
