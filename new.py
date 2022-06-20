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


def func(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    res1 = soup.find('table', class_='se-table-content')
    body = res1.find_all('tr')

    global list_live_patient
    global list_sum_patient
    global list_death_rate
    global list_vaccinated

    list_live_patient = []
    list_sum_patient = []
    list_death_rate = []
    list_vaccinated = []

    idx = 0
    for i in body:
        cnt = 0
        idx = idx+1
        if idx == 1:
            continue
        body1 = i.find_all('td')
        for j in body1:
            cnt = cnt+1
            if cnt > 5:
                break
            if cnt == 1:
                continue
            elif cnt >= 2:
                k = j.text.lstrip('\n')
                k = k.rstrip('\n')
                if cnt == 2:
                    list_live_patient.append(k)
                    continue
                elif cnt == 3:
                    list_sum_patient.append(k)
                    continue
                elif cnt == 4:
                    list_death_rate.append(k)
                    continue
                elif cnt == 5:
                    list_vaccinated.append(k)
                    continue


@app.route('/')
def home():
    return render_template('home.html')
    # func_weather(
    #     "https://weather.com/weather/tenday/l/4ba28384e2da53b2861f5b5c70b7332e4ba1dc83e75b948e6fbd2aaceeeceae3")
    # func_covid("https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
    # return render_template("tabmenu_china.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print)


@app.route('/info', methods=['POST'])
def info():
    mode = request.form.get('button')
    if mode == 'japan':
        func_weather(
            "https://weather.com/weather/tenday/l/4ba28384e2da53b2861f5b5c70b7332e4ba1dc83e75b948e6fbd2aaceeeceae3")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        return render_template("tabmenu_japan.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated)

    elif mode == 'china':
        func_weather(
            "https://weather.com/weather/tenday/l/71ca347e2948ee9490525aa5433fa91da6973ae51ea0f765fbe8e85b9f16c5df")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        return render_template("tabmenu_china.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated)

    elif mode == 'taiwan':
        func_weather(
            "https://weather.com/weather/tenday/l/fe7393b7f2c8eed2cf692bd079361df362d9f0c1c0f896e6e46a649295e15c7d")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        return render_template("tabmenu_taiwan.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated)

    elif mode == 'hongkong':
        func_weather(
            "https://weather.com/weather/tenday/l/8f0658124f5f5b725ca5ed254decc028fd2099a8ac1843faa2ceb206c9b464d1")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        return render_template("tabmenu_hongkong.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated)

    elif mode == 'vietnam':
        func_weather(
            "https://weather.com/weather/tenday/l/e09d58707a823303a77d65888f867fbe34d5d80ab1e7983a17461491a84474eb")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        return render_template("tabmenu_vietnam.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated)

    elif mode == 'singapore':
        func_weather(
            "https://weather.com/weather/tenday/l/7b1c4499e4bd335aed1f686d965ea106d29c9c288d68ec4596b1a1e8535640ba")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        return render_template("tabmenu_singapore.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated)

    elif mode == 'thailand':
        func_weather(
            "https://weather.com/weather/tenday/l/61d235a12c8f0b158c472bb5cf4a6a2d17b42270c214e7285c48666e57f21864")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        return render_template("tabmenu_thailand.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated)

    elif mode == 'malaysia':
        func_weather(
            "https://weather.com/weather/tenday/l/260bed6e5564853312a896b040219099674310ce4eb01f31c8526a9bd9b49a7c")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        return render_template("tabmenu_malaysia.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated)

    elif mode == 'laos':
        func_weather(
            "https://weather.com/weather/tenday/l/9d4759220510346ac9b159414847e95a8858a58f5a578eef3c0ea278e37d519f")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        return render_template("tabmenu_laos.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_lilist_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated)

        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        return render_template("tabmenu_mongolia.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated)

    elif mode == 'guam':
        func_weather(
            "https://weather.com/weather/tenday/l/fa9f819c190d7ab04ad7bbd2e1ada726637098fda80935a9d623672b84aea1d6")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        return render_template("tabmenu_guam.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated)

    elif mode == 'saipan':
        func_weather(
            "https://weather.com/weather/tenday/l/433a68edb169672f4079ddfaf42f2b2fc83c8c22bb2837521047f00958bf00a6")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        return render_template("tabmenu_saipan.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated)


if __name__ == '__main__':
    app.run()
