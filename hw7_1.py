# Практическое задание к 7 уроку курса "Методы сбора"

# 1) Написать программу, которая собирает входящие письма из своего или тестового
#  почтового ящика и сложить данные о письмах в базу данных (от кого, дата отправки,
#  тема письма, текст письма полный)


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions
from pymongo import MongoClient

from pprint import pprint
from time import sleep


def parse_element (element, css_selector):
    return WebDriverWait(element, 95).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))).text

def parse_email (element):
    item = {}

    item['from_name'] = parse_element(element, 'span[class~="ns-view-message-head-sender-name"]')
    item['from_email'] = parse_element(element, 'span[class~="mail-Message-Sender-Email"]')
    item['date'] = parse_element(element, 'div[class~="ns-view-message-head-date"]')
    item['subject'] = parse_element(element, 'div[class~="mail-Message-Toolbar-Subject"]')
    item['text_message'] = parse_element(element, 'div.mail-Message-Body-Content')

    return item

client = MongoClient('localhost', 27017)
mongo_base = client['mail_db']
collection = mongo_base['messages']



driver = webdriver.Chrome()
driver.get('https://passport.yandex.ru/auth/add?from=mail&origin=hostroot_homer_auth_L_ru&retpath=https%3A%2F%2Fmail.yandex.ru%2F&backpath=https%3A%2F%2Fmail.yandex.ru%3Fnoretpath%3D1')

assert 'Авторизация' in driver.title

elem = driver.find_element_by_id("passp-field-login")
elem.send_keys('tash3rt')
elem.send_keys(Keys.RETURN)


elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'passp-field-passwd'))) # driver.find_element_by_id("")
elem.send_keys('lbvecty')
elem.send_keys(Keys.RETURN)

elem = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'ns-view-messages-item-wrap'))) # .find_element_by_class_name()

elem.click()

while True:
    try:
        parsed_mail = parse_email(driver)
        pprint(parsed_mail)
        collection.insert_one(parsed_mail)

        bnext = WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, 'след.'))
        )
        bnext.click()
        sleep(0.5)
    except exceptions.TimeoutException:
        print('All emails on collected')
        driver.quit()
        exit()

