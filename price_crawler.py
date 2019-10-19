# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import requests, time
from string import Template

url = Template("https://www.twse.com.tw/exchangeReport/STOCK_DAY_AVG?response=csv&date=${month}&stockNo=0056")
years = range(2019,2020)
months = range(1,10)
output = ''

f = open('output2.csv','wb')
for y in years:
    for m in months:
        y_m = f'{y:04d}{m:02d}01'
        r = requests.get(url.substitute(month=str(y_m)), allow_redirects=True)
        f.write(r.content)
        time.sleep(5)

f.close