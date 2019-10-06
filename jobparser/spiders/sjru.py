# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
from pprint import pprint
import re


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python']

    def parse(self, response: HtmlResponse):
        # pprint(response.text)
        next_page = response.xpath(
            "//a[@class='icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-dalshe']/@href").get()
        print(next_page)

        yield response.follow(next_page, callback=self.parse)
        vacancy = response.xpath(
            "//a[contains(@class, 'icMQ_ _1QIBo')]/@href").getall()
        # print(vacancy)
        for link in vacancy:
            # print(link)
            yield response.follow(link, self.vacancy_parse)#,
                                  # cb_kwargs={'link':link}
                                  # )

    def vacancy_parse (self, response: HtmlResponse):#, link):
        name = response.xpath("//h1[@class='_3mfro rFbjy s1nFK _2JVkc']/text()").get()

        salary_parse = response.xpath(
            "//span[@class='_3mfro _2Wp8I ZON4b PlM3e _2JVkc']/*/text()"
                    ).getall()
        salary = str([item.replace('\xa0', '') for item in salary_parse])
        salary_currency = 'RUR'
        link = response.url
        source = 'www.superjob.ru'

        if re.search('\d', salary):
            if re.search('от', salary):
                salaryfrom = ''.join(re.findall('\d', 'salary'))
                salaryto = None
            elif re.search('до', salary):
                salaryfrom = None
                salaryto = ''.join(re.findall('\d', salary))
            elif re.search('-|—', salary):
                salaryfork = re.split('-|—', salary)
                salaryfrom = ''.join(re.findall('\d', salaryfork[0]))
                salaryto = ''.join(re.findall('\d', salaryfork[1]))
            else:
                salaryfrom = ''.join(re.findall('\d', salary))
                salaryto = ''.join(re.findall('\d', salary))
        else:
            salaryfrom = None
            salaryto = None

        # print(f'{name} {salary} {salary_currency} {salaryfrom} {salaryto} {link} {source}')

        yield JobparserItem(name=name,
                            # salary=salary,
                            link=link,
                            source=source,
                            salary_currency=salary_currency,
                            salaryfrom=salaryfrom,
                            salaryto=salaryto
                            )
