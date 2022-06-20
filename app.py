#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from bs4 import BeautifulSoup 
import re
import requests
import sys

from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from elasticsearch import Elasticsearch

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import word_tokenize
import numpy
import math

from flask import Flask, render_template, request

app = Flask(__name__)

es_host="http://localhost:9200" 

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

    list_date1 = []
    list_rain1 = []
    list_high_temp_F = []
    list_low_temp_F = []
    list_high_temp_C = []
    list_low_temp_C = []
    
    list_date = []
    list_rain = []
    list_high_temp_C = []
    list_low_temp_C = []

    cnt = 1
    for idx in res1:
        if (idx == None):
            break
        if (cnt == 11):
            break
        list_date1.append(idx.find('h3').text)
        list_high_temp_F.append(
            idx.find(class_='DetailsSummary--highTempValue--3Oteu').text)
        list_low_temp_F.append(
            idx.find(class_='DetailsSummary--lowTempValue--3H-7I').text)
        tmp = idx.find('div', class_='DetailsSummary--precip--1ecIJ')
        list_rain1.append(tmp.find('span').text)
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
  
    e2={
      "date":list_date1,
      "rain":list_rain1,
      "high_temp":list_high_temp_C,
      "low_temp":list_low_temp_C
       }
                  
    es = Elasticsearch(es_host)
   
    es.index(index='weather', id=2, document=e2) 

    
    data1 = es.search(index="weather", body={"query":{"match_all":{}}})
    if data1['hits']['total']['value']>0:
       for doc in data1['hits']['hits']:
          data=doc['_source']
          list_date=data['date']
          list_rain=data['rain']
          list_high_temp_C=data['high_temp']
          list_low_temp_C=data['low_temp']
          
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

    result_print1 = ''.join(result_tmp)

    tb = soup.find('table', class_='lineTop_tb2')
    tb1 = tb.find('tbody')


    list1 = []
    list2 = []
    list3 = []
    list4 = []
    list5 = []
    
    list11 = []
    list21 = []
    list31 = []
    list41 = []
    list51 = []

    for link in tb1.find_all('tr'):
        name = link.find_all('td')
        if (name == None):
            break
        cnt = 0
        for a in name:
            if(cnt == 0):
                list11.append(a.text)
            elif(cnt == 1):
                list21.append(a.text)
            elif(cnt == 2):
                list31.append(a.text)
            elif(cnt == 3):
                list41.append(a.text)
            elif(cnt == 4):
                list51.append(a.text)

            cnt = cnt+1    
   
    e1={
      "list1":list11,
      "list2":list21,
      "list3":list31,
      "list4":list41,
      "list5":list51,
      "result_print":result_print1
       }
                  
    es = Elasticsearch(es_host)
   
    es.index(index='covid', id=1, document=e1)      
    
    data1 = es.search(index="covid", body={"query":{"match_all":{}}})
    if data1['hits']['total']['value']>0:
       for doc in data1['hits']['hits']:
          data=doc['_source']
          list1=data['list1']
          list2=data['list2']
          list3=data['list3']
          list4=data['list4']   
          list5=data['list5'] 
          result_print=data['result_print']

          
#frequency analysis
word_d = {}
sent_list = []

def process_new_sentence(s):
    sent_list.append(s)
    tokenized = word_tokenize(s)
    for word in tokenized:
        if word not in word_d.keys():
            word_d[word] = 0
        word_d[word] += 1
        
def compute_tf(s):
    bow = set()
    # dictionary for words in the given sentence (document)
    wordcount_d = {} 

    tokenized = word_tokenize(s)
    for tok in tokenized:
        if tok not in wordcount_d.keys():
            wordcount_d[tok]=0
        wordcount_d[tok] += 1
        bow.add(tok)

    tf_d = {}
    for word,count in wordcount_d.items():
        tf_d[word] = count/float(len(bow))
    
    return tf_d
    
def compute_idf():
    Dval = len(sent_list)
    # build set of words
    bow = set()

    for i in range(0, len(sent_list)):
        tokenized = word_tokenize(sent_list[i])
        for tok in tokenized:
            bow.add(tok)

    idf_d = {}
    for t in bow:
        cnt = 0
        for s in sent_list:
            if t in word_tokenize(s):
                cnt += 1
        idf_d[t] = math.log(Dval/float(cnt))
    return idf_d
    
def Youtuber_func(name):
    global res1
    global freq
    global res2
    
    res1=[]
    res2=[]    
    freq={}
    
    #insert youtuber name    
    es = Elasticsearch(es_host)
   
    global original
    original=[]

    data0 = es.search(index="youtuber", body={"query":{"match_all":{}}})
    if es.indices.exists(index='youtuber'):
    #put original data into original(list)
       for doc in data0['hits']['hits']:
          data=doc['_source']
          original=list(data['name'])
       original.append(name)
       e1={
          "name":original
       }
    else:
       e1={
          "name":name
       }
       
    es.index(index='youtuber', id=2, document=e1)   
    
    data1 = es.search(index="youtuber", body={"query":{"match_all":{}}})
    if data1['hits']['total']['value']>0:
       for doc in data1['hits']['hits']:
          data=doc['_source']
          res1=data['name']
         
    #data analysis
    for i in res1:
        process_new_sentence(i)

    idf_d = compute_idf()
    for i in range(0, len(sent_list)):
        tf_d = compute_tf(sent_list[i])
        for word,tfval in tf_d.items():
            freq[word]= tfval*idf_d[word]

    e2={
        "name":original,
        "freq":freq
    }
    
    es.index(index='youtuber', id=2, document=e2)   
    
    data2 = es.search(index="youtuber", body={"query":{"match_all":{}}})
    if data2['hits']['total']['value']>0:
       for doc in data2['hits']['hits']:
          data=doc['_source']
          res2=data['freq']  
    global resultt
    resultt=[]     
    resultt = sorted(res2, key=lambda x : res2[x])
    resultt=resultt[:5]   
  
def func_number(url):
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
    
    list_live_patient1 = []
    list_sum_patient1 = []
    list_death_rate1 = []
    list_vaccinated1 = []

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
                    list_live_patient1.append(k)
                    continue
                elif cnt == 3:
                    list_sum_patient1.append(k)
                    continue
                elif cnt == 4:
                    list_death_rate1.append(k)
                    continue
                elif cnt == 5:
                    list_vaccinated1.append(k)
                    continue

    e2={
      "list_live_patient":list_live_patient1,
      "list_sum_patient":list_sum_patient1,
      "list_death_rate":list_death_rate1,
      "list_vaccinated":list_vaccinated1
       }
                  
    es_host="http://localhost:9200"      
    es = Elasticsearch(es_host)
   
    es.index(index='patientnum', id=2, document=e2) 

    data1 = es.search(index="patientnum", body={"query":{"match_all":{}}})
    if data1['hits']['total']['value']>0:
       for doc in data1['hits']['hits']:
          data=doc['_source']
          list_live_patient=data['list_live_patient']
          list_sum_patient=data['list_sum_patient']
          list_death_rate=data['list_death_rate']
          list_vaccinated=data['list_vaccinated']

#youtube link
def func_ytube(site, country):
    global title_rank
    global view_rank
    global link_rank
    
    global df
    driver = wb.Chrome("/usr/lib/chromium-browser/chromedriver")
    url = (site)
    driver.get(url)
    body = driver.find_element_by_tag_name('body')
    body.send_keys(Keys.PAGE_DOWN)

    for i in range(1, 31):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)

    soup = BeautifulSoup(driver.page_source, 'lxml')

    title = soup.select('a#video-title')
    soup.select('span.style-scope.ytd-video-meta-block')

    view = soup.select('div#metadata-line > span:nth-child(1)')
    link = soup.select('a#video-title')

    title_list = []
    view_list = []
    view_num_list = []
    view_only_num_list = []
    million_billion_list = []
    result_list = []
    link_list = []
    
    for i in link:
        link_list.append('{}{}'.format('https://www.youtube.com',i.get('href')))
   
    for i in range(len(title)):
        title_list.append(title[i].text.strip())
        view_list.append(view[i].text.strip())

    for num in view_list:
        num_list = num.split()
        view_num_list.append(num_list[0])

    for i in range(len(view_num_list)):
        if(view_num_list[i] == 'N' or view_num_list[i] == 'No'):
            view_num_list[i] = '0'
        else:
            continue

    for views in view_num_list:
        view_only_num_list.append(views[:-1])

    for i in range(len(view_num_list)):
        if(view_only_num_list[i] == ''):
            view_only_num_list[i] = '0'
        else:
            continue

    for word in view_num_list:
        million_billion_list.append(re.findall('[a-zA-Z]', word))

    for i in range(len(million_billion_list)):
        if(million_billion_list[i] == ['K']):
            million_billion_list[i] = '1000'
        elif(million_billion_list[i] == ['M']):
            million_billion_list[i] = '1000000'
        else:
            million_billion_list[i] = '1'

    for i in range(len(million_billion_list)):
        result = 0
        result = float(view_only_num_list[i])*int(million_billion_list[i])
        result=int(result)
        result_list.append(result)
        
    df = pd.DataFrame({"title":title_list, "views":result_list, "link":link_list})
    df.sort_values(by='views',ascending=False).groupby('title')
    
    #.head(5)
    title_col = df['title'].tolist()
    view_col = df['views'].tolist()
    link_col = df['link'].tolist()
    
    title_rank1 = []
    view_rank1 = []
    link_rank1 = []
    
    title_rank = []
    view_rank = []
    link_rank = []
    
    for i in range(5):
    	title_rank1.append(title_col[i])
    	
    for i in range(5):
    	view_rank1.append(view_col[i])
    	
    for i in range(5):
    	link_rank1.append(link_col[i])
    	
    link_rank2=[]
    tmp=[]
    for i in link_rank1:
    	tmp=i.split('watch?v=')
    	str=tmp[0]+'embed/'+tmp[1]
    	link_rank2.append(str)
    	   	
    es = Elasticsearch(es_host)
    e1={
          "title":title_rank1,
          "view":view_rank1,
          "link":link_rank2
       }    
    
    es.index(index=country, id=2, document=e1) 	
   
    link_rank=link_rank2 
  
@app.route('/')
def home():
    return render_template('home.html')
    
@app.route('/youtuber', methods=['POST'])
def infor():
   mode=request.form['youtuber']
   x=requests.utils.unquote(mode)
   Youtuber_func(mode)
   return render_template("ela.html", res1=resultt)

@app.route('/info', methods=['POST'])
def info():
    mode = request.form.get('button')
    if mode == 'japan':
        func_weather(
            "https://weather.com/weather/tenday/l/4ba28384e2da53b2861f5b5c70b7332e4ba1dc83e75b948e6fbd2aaceeeceae3")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func_number("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        func_ytube("https://www.youtube.com/results?search_query=%22%EC%9D%BC%EB%B3%B8%22+%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8", "japan")
        return render_template("tabmenu_japan.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated, link_rank=link_rank)

    elif mode == 'china':
        func_weather(
            "https://weather.com/weather/tenday/l/71ca347e2948ee9490525aa5433fa91da6973ae51ea0f765fbe8e85b9f16c5df")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func_number("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        func_ytube("https://www.youtube.com/results?search_query=%22%EC%A4%91%EA%B5%AD%22+%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8", "china")
        return render_template("tabmenu_china.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated, link_rank=link_rank)

    elif mode == 'taiwan':
        func_weather(
            "https://weather.com/weather/tenday/l/fe7393b7f2c8eed2cf692bd079361df362d9f0c1c0f896e6e46a649295e15c7d")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func_number("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        func_ytube("https://www.youtube.com/results?search_query=%22%EB%8C%80%EB%A7%8C%22+%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8", "taiwan")
        return render_template("tabmenu_taiwan.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated, link_rank=link_rank)

    elif mode == 'hongkong':
        func_weather(
            "https://weather.com/weather/tenday/l/8f0658124f5f5b725ca5ed254decc028fd2099a8ac1843faa2ceb206c9b464d1")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func_number("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        func_ytube("https://www.youtube.com/results?search_query=%22%ED%99%8D%EC%BD%A9%22+%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8","hongkong")
        return render_template("tabmenu_hongkong.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated, link_rank=link_rank)

    elif mode == 'vietnam':
        func_weather(
            "https://weather.com/weather/tenday/l/e09d58707a823303a77d65888f867fbe34d5d80ab1e7983a17461491a84474eb")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func_number("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        func_ytube("https://www.youtube.com/results?search_query=%22%EB%B2%A0%ED%8A%B8%EB%82%A8%22+%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8","vietnam")
        return render_template("tabmenu_vietnam.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated, link_rank=link_rank)

    elif mode == 'singapore':
        func_weather(
            "https://weather.com/weather/tenday/l/7b1c4499e4bd335aed1f686d965ea106d29c9c288d68ec4596b1a1e8535640ba")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func_number("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        func_ytube("https://www.youtube.com/results?search_query=%22%EC%8B%B1%EA%B0%80%ED%8F%AC%EB%A5%B4%22+%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8","singapore")
        return render_template("tabmenu_singapore.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated, link_rank=link_rank)

    elif mode == 'thailand':
        func_weather(
            "https://weather.com/weather/tenday/l/61d235a12c8f0b158c472bb5cf4a6a2d17b42270c214e7285c48666e57f21864")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func_number("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        func_ytube("https://www.youtube.com/results?search_query=%22%ED%83%9C%EA%B5%AD%22+%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8","thailand")
        return render_template("tabmenu_thailand.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated, link_rank=link_rank)

    elif mode == 'malaysia':
        func_weather(
            "https://weather.com/weather/tenday/l/260bed6e5564853312a896b040219099674310ce4eb01f31c8526a9bd9b49a7c")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func_number("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        func_ytube("https://www.youtube.com/results?search_query=%22%EB%A7%90%EB%A0%88%EC%9D%B4%EC%8B%9C%EC%95%84%22+%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8","malaysia")
        return render_template("tabmenu_malaysia.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated, link_rank=link_rank)

    elif mode == 'mongolia':
        func_weather(
            "https://weather.com/weather/tenday/l/348a814ea6bfcb894d69d68794ed2708618e351117cc351261fbedeec0aaa4fa")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func_number("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        func_ytube("https://www.youtube.com/results?search_query=%22%EB%AA%BD%EA%B3%A8%22+%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8","mongolia")
        return render_template("tabmenu_mongolia.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated, link_rank=link_rank)

    elif mode == 'laos':
        func_weather(
            "https://weather.com/weather/tenday/l/9d4759220510346ac9b159414847e95a8858a58f5a578eef3c0ea278e37d519f")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func_number("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        func_ytube("https://www.youtube.com/results?search_query=%22%EB%9D%BC%EC%98%A4%EC%8A%A4%22+%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8","laos")
        return render_template("tabmenu_laos.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated, link_rank=link_rank)

    elif mode == 'guam':
        func_weather(
            "https://weather.com/weather/tenday/l/fa9f819c190d7ab04ad7bbd2e1ada726637098fda80935a9d623672b84aea1d6")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func_number("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        func_ytube("https://www.youtube.com/results?search_query=%22%EA%B4%8C%22+%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8","guam")
        return render_template("tabmenu_guam.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated, link_rank=link_rank)

    elif mode == 'saipan':
        func_weather(
            "https://weather.com/weather/tenday/l/433a68edb169672f4079ddfaf42f2b2fc83c8c22bb2837521047f00958bf00a6")
        func_covid(
            "https://www.airport.co.kr/www/cms/frCon/index.do?MENU_ID=2600")
        func_number("https://blog.naver.com/PostList.naver?blogId=sunju2629&from=postList&categoryNo=1")
        func_ytube("https://www.youtube.com/results?search_query=%22%EC%82%AC%EC%9D%B4%ED%8C%90%22+%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8","saipan")
        return render_template("tabmenu_saipan.html", list_date=list_date, list_rain=list_rain, list_temph=list_high_temp_C, list_templ=list_low_temp_C, list_vacci=list1, list_notvacci=list2, list_prov=list3, list_coronatest=list4, list_else=list5, list_updatedate=result_print, list_live_patient=list_live_patient, list_sum_patient=list_sum_patient, list_death_rate=list_death_rate, list_vaccinated=list_vaccinated, link_rank=link_rank)

if __name__ == '__main__':
    app.run()
