#!/usr/bin/python3
import sys
from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import re

from elasticsearch import Elasticsearch

from flask import Flask, render_template, request

app = Flask(__name__)


def func_ytube(site):
  
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

    soup = bs(driver.page_source, 'lxml')

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
    
    title_rank = []
    view_rank = []
    link_rank = []
    
    for i in range(5):
    	title_rank.append(title_col[i])
    	
    for i in range(5):
    	view_rank.append(view_col[i])
    	
    for i in range(5):
    	link_rank.append(link_col[i])
    
    	
 
@app.route('/')
def home():
    func_ytube("https://www.youtube.com/results?search_query=%EC%9D%BC%EB%B3%B8%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8")
    return render_template("bok2.html", title_rank=title_rank, view_rank=view_rank,link_rank=link_rank)


if __name__ == '__main__':
    app.run()
