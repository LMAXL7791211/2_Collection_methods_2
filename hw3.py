# Домашняя работа к 3 уроку курса "Методы сбора"

#
# 1) Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
#  записывающую собранные вакансии в созданную БД
# 2) Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой
#  больше введенной суммы
# 3*)Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта

from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import re
from time import sleep
from random import randint
import pandas as pd
import json
from pymongo import MongoClient


def vacsearch(testdb, min_salary):
    return testdb.find({'salaryfrom': {'$gt': min_salary}})


def vacblock(html, attr_vaclist, attr_vacblock):
    parsed_html = bs(html, 'html.parser')
    vaclist = parsed_html.find(name='div', attrs=attr_vaclist)
    if vaclist:
        return vaclist.find_all(name='div', attrs=attr_vacblock)
    else:
        return []


PAGES = int(input('Input how many pages to search --> '))
PROFESSION = input('Input profession to search --> ')
PROFESSION_SJ = PROFESSION.replace(' ', '%20')
PROFESSION_HH = PROFESSION.replace(' ', '+')
vacs = []

link_sj = 'https://www.superjob.ru/vacancy/search/?keywords=' + PROFESSION_SJ + '&geo%5Bc%5D%5B0%5D=1&page='
link_hh = 'https://hh.ru/search/vacancy?only_with_salary=false&area=1&clusters=true&search_field=name&enable_snippets=true&salary=&text=' + PROFESSION_HH + '&page='
headers = {'User-agent': 'Mozilla/5.0'}

# SJ
print(f'Search {PAGES} pages on Superjob:')
for i in range(PAGES):
    html = requests.get(link_sj + str(i)).text

    # with open('sj.htm', 'w', encoding='utf-8') as f:
    #    f.write(html)

    # with open('sj.htm', 'r', encoding='utf-8') as f:
    #     html = f.read()

    vacblocks = vacblock(html, {'style': "display:block"}, {'class': "_212By _37XTu"})
    print(f'Page {i+1}, {int(len(vacblocks) / 2)} positions on page')
    if len(vacblocks) == 0:
        break
    for block in vacblocks:
        if vacblocks.index(block) % 2 == 1:
            vacs.append({'vacname': block.find(name='div', attrs={'class': "_3mfro CuJz5 PlM3e _2JVkc _3LJqf"}).text,
                         'salary': block.find(name='span', attrs={'class': re.compile(r"salary*")}).text.replace(u'\xa0', ' '),
                         'link': 'https://www.superjob.ru' + block.find(name='a', href=re.compile(r"/vakansii*"))['href'],
                         'source': 'superjob.ru'
                         })
    sleep(2 + randint(0, 2))

# HH
print(f'Search {PAGES} pages on HH:')
for i in range(PAGES):
    html = requests.get(link_hh + str(i), headers=headers).text

    # with open('hh.htm', 'w', encoding='utf-8') as f:
    #     f.write(html)
    # exit(0)

    # with open('hh.htm', 'r', encoding='utf-8') as f:
    #     html = f.read()

    vacblocks = vacblock(html, {'class': "vacancy-serp"},
                         {'data-qa':
                          ["vacancy-serp__vacancy",
                           "vacancy-serp__vacancy vacancy-serp__vacancy_premium"]})
    print(f'Page {i+1}, {int(len(vacblocks))} positions on page')
    if len(vacblocks) == 0:
        break
    for block in vacblocks:
        sal = block.find(name='div', attrs={'data-qa': "vacancy-serp__vacancy-compensation"})
        if sal:
            sal = sal.text.replace(u'\xa0', ' ')
        else:
            sal = 'Не указана'
        vacs.append({'vacname': block.find(name='a').text,
                     'salary': sal,
                     'link': block.find(name='a')['href'],
                     'source': 'hh.ru'
                     })
    sleep(2 + randint(0, 2))




# with open("vacs.json", "w", encoding="utf-8") as f:
#     json.dump(vacs, f)
# exit(0)

# with open('vacs.json', 'r', encoding='utf-8') as f:
#      vacs = json.load(f)


# узнаём курс доллара и евро с API от ЦБР
linkCB = 'http://www.cbr.ru/scripts/XML_daily.asp?'
headers = {'User-agent': 'Mozilla/5.0'}

req = requests.get(linkCB, headers=headers).text

KURSUSD = float(re.search("США</Name><Value>(\d\d,\d\d\d\d)</Value>", req).groups()[0].replace(',', '.'))
KURSEUR = float(re.search("Евро</Name><Value>(\d\d,\d\d\d\d)</Value>", req).groups()[0].replace(',', '.'))


vacssal = []

for vac in vacs:
    if re.search('USD', vac['salary']):
        KURS = KURSUSD
    elif re.search('EUR', vac['salary']):
        KURS = KURSEUR
    else:
        KURS = 1

    if re.search('\d', vac['salary']):
        if re.search('от', vac['salary']):
            salaryfrom = int(''.join(re.findall('\d', vac['salary']))) * KURS
            salaryto = None
        elif re.search('до', vac['salary']):
            salaryfrom = None
            salaryto = int(''.join(re.findall('\d', vac['salary']))) * KURS
        elif re.search('-|—', vac['salary']):
            salaryfork = re.split('-|—', vac['salary'])
            salaryfrom = int(''.join(re.findall('\d', salaryfork[0]))) * KURS
            salaryto = int(''.join(re.findall('\d', salaryfork[1]))) * KURS
        else:
            salaryfrom = int(''.join(re.findall('\d', vac['salary']))) * KURS
            salaryto = int(''.join(re.findall('\d', vac['salary']))) * KURS
    else:
        salaryfrom = None
        salaryto = None

    vacnew = {'link': vac['link'],
              'vacname': vac['vacname'],
              'salaryfrom': salaryfrom,
              'salaryto': salaryto,
              'source': vac['source']
              }
    vacssal.append(vacnew)

print('All positions on both resources:\n')

data = pd.DataFrame(vacssal)
print(data)
data.to_pickle('vacssal_DF.pkl')

print(f'{len(vacssal)} total positions.')

client = MongoClient('mongodb://127.0.0.1:27017')
db = client['testdb']
testdb = db.testdb

added_vac = 0
vacs_exists = 0

for vac in vacssal:
    if testdb.find_one({'link': vac['link']}):
        print(f'{vac}\n exists in database!')
        vacs_exists += 1
    else:
        testdb.insert_one(vac)
        added_vac += 1

print(f' Total added {added_vac}, exists in DB {vacs_exists}.')


#  testdb.insert_many(vacssal)


min_salary = int(input('Input your desired salary minimum, roubles --> '))
objects = vacsearch(testdb, min_salary)
print(f'Positions with salary more than {min_salary}:\n')
for i in objects:
    print(i)
