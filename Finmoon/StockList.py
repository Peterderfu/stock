# -*- coding:utf-8 -*-
import xml.dom.minidom
import requests,re,chardet,codecs
from bs4 import BeautifulSoup
from xml.etree.ElementTree import Element, SubElement, Comment
# from ElementTree_pretty import prettify
from pandas.core.dtypes.missing import isnull
from xml.etree import ElementTree
from xml.dom import minidom
def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

Date_prefix = u"最近更新日期:"
dateUpdated = ""
labels = [s.strip() for s in ["有價證券代號","有價證券名稱 ","ISIN","上市日"," 市場"," 產業別","CFI"]]
# AllStocks = dict{}
# URL = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2" #本國上市證券國際證券辨識號碼一覽表
# r = requests.get(URL, allow_redirects=True)
# if r.status_code != 200:
#     exit
# 
# webpage = r.text.encode('utf-8')
webpage = open("C_public.html","r").read()
if isnull(webpage):
    exit("無法擷取來源")

top = Element('top')


soup = BeautifulSoup(webpage,'html.parser') # encode as utf-8 is very important

tags = soup.find("font",class_="h1") # get title
if tags:
    title = SubElement(top, 'title')
    title.text = tags.text.strip()
    
tags = soup.find_all('center',limit=2) # date is contained in one of <center> tags  
if tags:
    for t in tags:
        if t.text.startswith(Date_prefix):   # date is prefixed with Date_prefix
            dateUpdated = t.text.split(":")[-1] # date is behind ":"
            datelisted = SubElement(top, 'dateUpdated')
            datelisted.text = dateUpdated.strip()
            break

try:
    table = soup.find_all('table')[1] # the 2nd table is desired
except:
    exit("Can't catch stock table")
# labels = [s for s in table.next.next.strings]  # fetch all the column lables
rows = table.next.contents[1:]  #ignore the 1st row

for r in rows:
    try:
        if (r.td['colspan']):
            serurityType = SubElement(top, 'serurityType',id = r.td.text.strip())
#             serurityType.text = r.td.text.strip()
    except:
#         [id,name,isin,listingDate,market,industry,CFI] = " ".join([s for s in r.strings]).split()
        properties = " ".join([s for s in r.strings]).split()
        security = SubElement(serurityType, 'security')
        for i in range(0,len(properties)):
            f = SubElement(security, 'property', id = labels[i])
            f.text = properties[i]
        
with codecs.open("output.xml",'w','utf-8') as f:
    f.write(prettify(top))
    f.close()

