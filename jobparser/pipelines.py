# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient




class JobparserPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy206

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name + '123']
        kursdict = {'RUR': 1, 'USD': 65, 'EUR': 75}
        if item['salary_currency']:
            kurs = kursdict[item['salary_currency']]
        else:
            kurs = 1  # RUR by default
            item['salary_currency'] = 'не указана'
        if item['salaryfrom']:
            item['salaryfrom'] = int(item['salaryfrom']) * kurs
        else:
            item['salaryfrom'] = 'не указана'
        if item['salaryto']:
            item['salaryto'] = int(item['salaryto']) * kurs
        else:
            item['salaryto'] = 'не указана'

        print(item)
        # print(f'kurs = {kurs}')
        collection.insert_one(item)
        return item
