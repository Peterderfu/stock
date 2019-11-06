# -*- coding:utf-8 -*-
from xml.etree.ElementTree import Element, SubElement
from pandas.core.dtypes.missing import isnull
from xml.etree import ElementTree
from bs4 import BeautifulSoup
from xml.dom import minidom
import requests,codecs

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

Date_prefix = u"最近更新日期:"
dateUpdated = ""
labels = [s.strip() for s in ["代號","名稱 ","ISIN","上市日"," 市場"," 產業別","CFI"]]
URL = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2" #本國上市證券國際證券辨識號碼一覽表
r = requests.get(URL, allow_redirects=True)
if r.status_code != 200:
    exit("".join(["無法存取網頁:" , URL]))
webpage = r.text.encode('utf-8')
# webpage = open("C_public.html","r").read()
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
    rows = soup.find('tr')
    rows = rows.next_sibling #ignore the 1st row
except:
    exit("Can't catch stock table")

newSerurityType = True
while (rows):
    newSerurityType = rows.td.has_attr("colspan")
    if (newSerurityType):
        serurityType = SubElement(top, 'serurityType',id = rows.td.text.strip())
    else:
        properties = " ".join([s for s in rows.strings]).split()
        security = SubElement(serurityType, 'security')
        for i in range(0,len(properties)):
            f = SubElement(security, 'property', id = labels[i])
            f.text = properties[i]
    rows = rows.next_sibling
        
with codecs.open("output.xml",'w','utf-8') as f:
    f.write(prettify(top))
    f.close()