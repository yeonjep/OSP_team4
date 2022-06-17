#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import requests
import sys

from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

# weather


def func_weather(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")

    global list_date
    global list_rain
    global list_high_temp_C
    global list_low_temp_C

    res1 = soup.find_all(
        'div', class_='DetailsSummary--DetailsSummary--2HluQ DetailsSummary--fadeOnOpen--vFCc_')

    list_date = []
    list_rain = []
    list_high_temp_F = []
    list_low_temp_F = []
    list_high_temp_C = []
    list_low_temp_C = []

    cnt = 1
    for idx in res1:
        if (idx == None):
            break
        if (cnt == 11):
            break
        list_date.append(idx.find('h3').text)
        list_high_temp_F.append(
            idx.find(class_='DetailsSummary--highTempValue--3Oteu').text)
        list_low_temp_F.append(
            idx.find(class_='DetailsSummary--lowTempValue--3H-7I').text)
        tmp = idx.find('div', class_='DetailsSummary--precip--1ecIJ')
        list_rain.append(tmp.find('span').text)
        cnt = cnt+1

    for idx in list_high_temp_F:
        if idx == "--":
            list_high_temp_C.append(27)
            continue
        idx = ''.join(e for e in idx if e.isalnum())
        i = float(idx)
        tmp = (i-32)*5/9
        tmp = int(tmp)
        list_high_temp_C.append(tmp)

    for idx in list_low_temp_F:
        if idx == "--":
            list_high_temp_C.append(27)
            continue
        idx = ''.join(e for e in idx if e.isalnum())
        i = float(idx)
        tmp = (i-32)*5/9
        tmp = int(tmp)
        list_low_temp_C.append(tmp)

# covid


def func_covid(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")

    global list1
    global list2
    global list3
    global list4
    global list5
    global result_print

    res1 = soup.find_all('div', class_='contTit')
    i = 1
    for idx in res1:
        if (i == 2):
            res2 = idx.text
            break
        i = i+1

    result_tmp = []
    index = -1
    for idx in res2:
        index = index+1
        if (index < 17):
            continue
        elif (index > 23):
            break
        else:
            result_tmp.append(idx)

    result_print = ''.join(result_tmp)

    tb = soup.find('table', class_='lineTop_tb2')
    tb1 = tb.find('tbody')

    list1 = []
    list2 = []
    list3 = []
    list4 = []
    list5 = []

    for link in tb1.find_all('tr'):
        name = link.find_all('td')
        if (name == None):
            break
        cnt = 0
        for a in name:
            if(cnt == 0):
                list1.append(a.text)
            elif(cnt == 1):
                list2.append(a.text)
            elif(cnt == 2):
                list3.append(a.text)
            elif(cnt == 3):
                list4.append(a.text)
            elif(cnt == 4):
                list5.append(a.text)

            cnt = cnt+1


@app.route('/')
def home():
    func_weather(
        "https://weather.com/weather/tenday/l/4ba28384e2da53b2861f5b5c70b7332e4ba1dc83e75b948e6fbd2aaceeeceae3")
    func_covid("https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
    return render_template("tabmenu.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print)


if __name__ == '__main__':
    app.run()
