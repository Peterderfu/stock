import requests
import re
import finlab
import pandas as pd
from finlab import data
# from talib import MA_Type
from datetime import datetime, timedelta
from string import Template
# import xml.etree.ElementTree as ET
from lxml import etree
from io import StringIO
# from lxml.html import parse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def My_BBANDS(data):
    return data.indicator('BBANDS',timeperiod=20,nbdevup=2.0, nbdevdn=2.0,matype=MA_Type.EMA)
def rotation_break(data,bband,NDay,break_rate):
  #bband:BBand帶寬%, 5%以下=>窄
  #NDay:帶寬小於bband之連續天數
  #break_rate:布林上(下)軌突破斜率
  print(f"尋找布林帶寬小於{bband}%且持續{NDay}日")

  #get BBand indicator, parameter {timeperiod=20,nbdevup=2.0, nbdevdn=2.0,matype=MA_Type.SMA} is identical to XQs'
  upper,middle,lower= data.indicator('BBANDS',timeperiod=20,nbdevup=2.0, nbdevdn=2.0,matype=MA_Type.SMA)
  #calculate BBand width
  width = ((upper/lower)-1)*100
  cond_1 = (width < bband).sustain(NDay) #帶寬小於bband且持續NDay天
  #calculate launch rate
  upper_pre = upper.shift(1)
  lower_pre = lower.shift(1)
  if break_rate>0:
    brk = ((upper-upper_pre)/upper_pre)*100    
    cond_2 = brk > break_rate     #突破斜率大於break_rate值
  else:
    brk = ((lower-lower_pre)/lower_pre)*100
    cond_2 = abs(brk) > abs(break_rate)     #突破斜率大於break_rate值
  
  entries = cond_1 & cond_2  
  cond_3 = volumn_below(3)
  entries = entries & cond_3
  return entries
def volumn_below(N):
  vol = data.get('price:成交股數')/1000
  vol_MA5 = vol.rolling(5).mean()
  entries = vol_MA5*N > vol
  return entries

def rotation_break_period(period,data, bband, NDay, break_rate):
  start = datetime.now()
  if start.hour < 18:  # if time is earlier than 18 o'clock, go to previous day
    start = start - timedelta(days=1)
  
  cbi = data.get('company_basic_info')
  df = rotation_break(data, bband, NDay, break_rate)
  remains = period
  start = pd.to_datetime(start)
  
  while True: # select the starting day
    if start.strftime("%Y-%m-%d") in df.axes[0]:
      break
    else:
      start = start-timedelta(days=1)
  start = df.axes[0].get_loc(start.strftime("%Y-%m-%d"))
  stocks = df.iloc[start-remains+1:start+1]
  name_list = []
  for s in stocks.columns:
    for d in stocks[s].index:
      if (stocks[s][d] == True):
        try:
          name = cbi[cbi['stock_id'] == s].values[-1][-1]
        except:
          name = "N/A"
        name = name+"("+s+")"
        name_list.append(d.strftime("%Y-%m-%d") + ":" + name)
  return name_list

def rotation_break_month(data, bband, NDay, break_rate):
  return rotation_break_period(30,data, bband, NDay, break_rate)

def rotation_break_week(data, bband, NDay, break_rate):
  return rotation_break_period(7,data, bband, NDay, break_rate)

def rotation_break_today(data, bband, NDay, break_rate):
  return rotation_break_period(1,data, bband, NDay, break_rate)
  

def get_price_twyahoo(stock_id=2702):
  url = f"https://tw.stock.yahoo.com/quote/{stock_id}"
  #xpath of close price
  xpath = '/html/body/div[1]/div/div/div/div/div[5]/div[1]/div[1]/div/div[3]/div/section[1]/div[2]/div[2]/div/ul/li[1]/span[2]'
  result = get_HTML_info(url,xpath)
  if result:
    return result
  return None

def has_warrant(stock_id=2330):
  url = f"https://tw.stock.yahoo.com/quote/{stock_id}"
  #xpath of warrant list
  xpath = r'//*[@id="qsp-overview-warrants"]/div[1]/h2'
  result = get_HTML_info(url,xpath)
  if result:
    return True
  return None
def get_warrant_info(stock_id=2330):
  service = ChromeService(executable_path=ChromeDriverManager().install())
  driver = webdriver.Chrome(service=service)
  url = 'https://www.warrantwin.com.tw/eyuanta/Warrant/Search.aspx'
  # driver = webdriver.Chrome()
  driver.get(url)
  # xpath_reset = '//*[@id="mm-0"]/div[2]/div[1]/div/div[1]/div[2]/div[3]/a[2]' #重設按鈕
  # elem = driver.find_element(By.XPATH, xpath_reset)
  # elem.click()
  elem_reset = driver.find_element(By.LINK_TEXT,"重設")
  elem_reset.click()
  elem_select = Select(driver.find_element(By.XPATH,'//*[@id="mm-0"]/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[1]/table/tbody/tr[3]/td/div/select'))
  elem_select.select_by_visible_text('全部')

  # try:
  #   elem_input = WebDriverWait(driver, 10).until(
  #       EC.presence_of_element_located((By.XPATH,'//*[@id="mm-0"]/div[2]/div[1]/div/div[1]/div[2]/div[1]/table/tbody/tr[1]/td/div/input')))
  # finally:
  #   driver.quit()
  # elem_input = driver.find_element(By.XPATH,'//*[@id="mm-0"]/div[2]/div[1]/div/div[1]/div[2]/div[1]/table/tbody/tr[1]/td/div/input')
  # elem_input.clear()
  elem_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH,'//*[@id="mm-0"]/div[2]/div[1]/div/div[1]/div[2]/div[1]/table/tbody/tr[1]/td/div/input')))
 
  elem_input.send_keys(stock_id)
  elem_query = driver.find_element(By.LINK_TEXT,"查詢")
  elem_query.click()
  assert elem_select is not None

def get_HTML_info(url,xpath):
  resp = requests.get(url, allow_redirects=True)
  parser = etree.HTMLParser()
  tree   = etree.parse(StringIO(resp.text), parser)
  result = tree.xpath(xpath)
  if result:
    return result[0].text
  return None

if __name__=="__main__":
  print(has_warrant(2702))