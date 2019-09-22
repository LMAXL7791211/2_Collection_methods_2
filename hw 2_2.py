# Домашняя работа к уроку 2 курса "Методы сбора..". Задача 2

# 2)Задание похожее, но подход к сбору данных здесь другой.
# Необходимо собрать информацию по продуктам питания с сайтов:
# https://rskrf.ru/ratings/produkty-pitaniya/ и
# https://roscontrol.com/category/produkti/
# Получившийся список должен содержать:
#
#     *Наименование продукта
#     *Категорию продукта        (например Бакалея)
#     *Подкатегорию продукта    (например "Рис круглозерный")
#     *Параметр "безопасность"
#     *Параметр "качество"
#     *Общий балл
#     *Сайт, откуда получена информация
#
# Данная структура должна быть одинаковая для продуктов с обоих сайтов.
# Общий результат можно вывести с помощью dataFrame через pandas.
#
# Можно выполнить по своему желанию одно любое задание или оба при желании и возможности.


from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import re
from time import sleep
from random import randint
import pandas as pd
import json


def get_html_text(link):
    html = requests.get(link, headers=headers)
    html.encoding = html.apparent_encoding
    return html.content


def category_block(html):
    parsed_html = bs(html, 'html.parser')
    catblock = parsed_html.find(name='div', attrs={'class': "categories"})
    return catblock.find_all(name='div', attrs={'class': "category-item"})


main_link = 'https://rskrf.ru'
start_link = '/ratings/produkty-pitaniya/'
headers = {'User-agent': 'Mozilla/5.0'}

html = get_html_text(main_link + start_link)

# with open('products.htm', 'wb', encoding='utf-8') as f:
#     f.write(html)
#     exit()


# with open('products.htm', 'rb', encoding='utf-8') as f:
#     html = f.read()

cats = category_block(html)
subcategories = []
for cat in cats:
    cat_name = cat.find(name='span', attrs={'class': "h5"}).text
    cat_link = main_link + cat.find(name='a')['href']
    sleep(2 + randint(0, 2))
    html = get_html_text(cat_link)
    subcats = category_block(html)
    for subcat in subcats:
        subcategories.append({'cat_name': cat_name,
                              'subcat_name': subcat.find(name='span', attrs={'class': "d-xl-none d-block"}).text,
                              'subcat_link': main_link + subcat.find(name='a')['href'],
                              'site': 'rskrf.ru'
                              })

pprint(subcategories)


# Далее незаконченная часть - проблема со скачиванием  html, скачивается другое содержимое

subcat_link = 'https://rskrf.ru/ratings/produkty-pitaniya/bakaleya/sukhie-zavtraki/'
html = get_html_text(subcat_link)

#
# with open('product.htm', 'wb') as f:
#     f.write(html)
#     exit()
#
# with open('product.htm', 'rb', encoding='utf-8') as f:
#     html = f.read()


# parsed_html = bs(html, 'html.parser')
# pprint(parsed_html)
# prodblock = parsed_html.find(name='div', attrs={'class': "product-row row rating-id"})
# products = prodblock.find_all(name='div', attrs={'class': "col-xl-4 col-lg-4 col-md-4 product"})
# # pprint(products[0])
# # print('\n\n')
# # pprint(products[-1])
# prodlist = []
# for product in products:
# #     sleep(2 + randint(0, 2))
#     prodlist.append({'product_name': product.find(name='h5', attrs={'class': "card-title with-text"}).text,
#                      'safety': '',
#                      'quality': '',
#                      'common_score': ''
#                      })
#
# pprint(prodlist)
