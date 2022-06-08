#!/usr/bin/python3
from selenium import webdriver as wb
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import re

driver = wb.Chrome("/usr/lib/chromium-browser/chromedriver")
url = ('https://www.youtube.com/results?search_query=%23%EC%9D%BC%EB%B3%B8%EC%97%AC%ED%96%89%EB%B8%8C%EC%9D%B4%EB%A1%9C%EA%B7%B8')
driver.get(url)


body = driver.find_element_by_tag_name('body')
body.send_keys(Keys.PAGE_DOWN)

for i in range(1, 51):
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.5)

soup = bs(driver.page_source, 'lxml')

title = soup.select('a#video-title')
# 영상 제목만 전체 조회
#for i in title:
#	print(i.text.strip())

soup.select('span.style-scope.ytd-video-meta-block')
# 조회수만 가져오기 (nth-child():몇 번째 자식인지)
view = soup.select('div#metadata-line > span:nth-child(1)')

#for i in view:
#    print(i.text.strip())

title_list = []
view_list = []


for i in range(len(title)):
    title_list.append(title[i].text.strip())
    view_list.append(view[i].text.strip())


#print(view_list)

view_num_list = []
for num in view_list:
	num_list = num.split()
	view_num_list.append(num_list[0])

#print(view_num_list)

for i in range(len(view_num_list)):
    if (view_num_list[i] == ''):
        view_num_list[i] = '0'
    else:
        continue
#only numbers....
view_only_num_list = []
for views in view_num_list:
	view_only_num_list.append(views[:-1])
print(view_only_num_list)

million_billion_list = []
for word in view_num_list:
    	million_billion_list.append(re.findall('[a-zA-Z]',word))

#print("check the K, M in it")
#print(million_billion_list)
#for i in million_billion_list:
	#print(i)

for i in range(len(million_billion_list)):
    if (million_billion_list[i] == ['K']):
        million_billion_list[i] = '1000'
    elif (million_billion_list[i] == ['M']):
        million_billion_list[i] = '1000000'
    else:
        million_billion_list[i] = '1'
print(million_billion_list)
result_list = []
for i in range(len(million_billion_list)):
   result = 0
   result = float(view_only_num_list[i])*int(million_billion_list[i])
   result_list.append(result)
   
print(result_list)

total_dic = dict(zip(title_list, result_list))
# total_dic.items()


total_dic = sorted(total_dic.items(), key=lambda item: item[1], reverse=True)
for i in range(5):
    k = total_dic[i]
    k = list(k)
    k[1] = str(k[1])
    k[0]
    print("{:<7}".format(k[0]), end=" ")
    print("조회수 : {:>7} 회".format(k[1]))
