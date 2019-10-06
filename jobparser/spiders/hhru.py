# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?text=Python&area=113&st=searchVacancy']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        yield response.follow(next_page,callback=self.parse)
        vacancy = response.css(
            'div.vacancy-serp div.vacancy-serp-item div.vacancy-serp-item__row_header a.bloko-link::attr(href)').extract()
        for link in vacancy:
            yield response.follow(link, self.vacancy_parse)#,
                                  # cb_kwargs={'link':link}
                                  # )

    def vacancy_parse (self, response: HtmlResponse):#, link):
        name = response.css('div.vacancy-title h1.header::text').extract_first()
#        salary = response.css('div.vacancy-title p.vacancy-salary::text').extract_first()
        salary_currency = response.xpath(
            "//div[contains(@class,'vacancy-title')]//meta[contains(@itemprop, 'currency')]/@content").get()
        salaryfrom = response.xpath(
            "//div[contains(@class,'vacancy-title')]//meta[contains(@itemprop, 'minValue')]/@content").get()
        salaryto = response.xpath(
            "//div[contains(@class,'vacancy-title')]//meta[contains(@itemprop, 'maxValue')]/@content").get()

        link = response.url
        source = 'www.hh.ru'

        #print(f'{name} {salary}')
        yield JobparserItem(name=name,
                            # salary=salary,
                            link=link,
                            source=source,
                            salary_currency=salary_currency,
                            salaryfrom=salaryfrom,
                            salaryto=salaryto
                            )
