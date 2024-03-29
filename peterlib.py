import requests
import re
import finlab
import pandas as pd
from finlab import data
from talib import MA_Type
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
from selenium.webdriver.common.action_chains import ActionChains
import plotly.express as px
def init():
  with open("finlab_token.txt",mode='r') as f:
    finlab.login(f.readline())
  data.set_storage(data.FileStorage()) 
def My_BBANDS(data):
    return data.indicator('BBANDS',timeperiod=20,nbdevup=2.0, nbdevdn=2.0,matype=MA_Type.SMA)
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
def price_below_bband_upper(data):
  upper,middle,lower= My_BBANDS(data)
  return (upper > data.get('price:最高價'))

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
def get_stockname_by_ID(stock_id):
  cbi = data.get('company_basic_info')
  try:
    name = cbi[cbi['stock_id'] == stock_id].values[-1][-1]
  except:
    name = "N/A"
  return name
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
  return False
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

  elem_input = driver.find_element(By.XPATH,'(//input[@type="text"])[2]')
  elem_input.click()
  elem_input.send_keys(stock_id)

  elem_query = driver.find_element(By.LINK_TEXT,"查詢")
  elem_query.click()

  elem_export = driver.find_element(By.LINK_TEXT,"匯出excel")
  elem_export.click()
  
  assert elem_select is not None
def get_warrant_info_kgi(stock_id=2330):
  service = ChromeService(executable_path=ChromeDriverManager().install())
  driver = webdriver.Chrome(service=service)
  url = 'https://warrant.kgi.com/EDWebSite/Views/WarrantSearch/WarrantSearch.aspx'  
  driver.get(url)
  elem_reset = driver.find_element(By.CLASS_NAME,"k-input")
  assert elem_reset is not None
def get_HTML_info(url,xpath):
  resp = requests.get(url, allow_redirects=True)
  parser = etree.HTMLParser()
  tree   = etree.parse(StringIO(resp.text), parser)
  result = tree.xpath(xpath)
  if result:
    return result[0].text
  return None
def search_BB_Uband_hit(data):
    upper,middle,lower= My_BBANDS(data)
    close = data.get('price:收盤價')
    close_pre = close.shift(-1)
    cbi = data.get('company_basic_info')
    x=(close>upper) & (close_pre<upper)
    for c in x.columns:
        stock_series = x[c]
        days_with_signal = x[x==True]
        info = []
        if len(days_with_signal) > 0:
            try:
                name = cbi[cbi['stock_id'] == c].values[-1][-1]
            except:
                name = "N/A"
            name = name+"("+c+"):"
            for i in days_with_signal.index:
                day = i.strftime('%Y/%m/%d')
                info.append(day)
                    
            print(name+",".join(info)) 

def get_K_GT(period,stocks,length=9,threshold_high=80,threshold_low=50):
#return the dates with K>threshold_high of the stock
#取得股價K值=threshold_high時，往前K值=threshold_low的日期
    K = data.indicator('kdj',length=length,save_to_storage=True)[0]
    output=dict()
    for s in stocks:
        tmp = []
        if len(period)>0:
            K_H = K[K.loc[K.index.intersection(period),s]>threshold_high][s].dropna()
        else:
            K_H = K[K.loc[:,s]>threshold_high][s].dropna()
        
        for dH in K_H.index:
        # for r in K_H.iterrows():
            K_L = K[K.loc[K.index<dH,[s]]<threshold_low][s].dropna()
            if not K_L.empty:
                dL = K_L.index[-1]
                tmp.append({'H':(dH.strftime('%Y-%m-%d'),K_H[dH]),
                             'L':(dL.strftime('%Y-%m-%d'),K_L[dL])})
        output[s]=tmp
    return output
def break_nextday_stat(data, bband, NDay, break_rate):
  lines = []
  df_break = rotation_break_period(720,data, bband, NDay, break_rate)
  close = data.get('price:收盤價')
  close_next = close.shift(-1)
  for d in df_break:
    m = re.match('(?P<date>\d{4}-\d{2}-\d{2})(?=:).+(?P<stock>(?<=\()\d+(?=\)))',d)
    if m:
      date = m.group('date')
      stock = m.group('stock')
      c1 = close.loc[date,stock]
      c2 = close_next.loc[date,stock]
      v = str(((c2-c1)/c1)*100)
      lines.append(date + ','+ stock + ',' + v + '\n')
  with open('log.csv','w') as f:
      f.writelines(lines)
def volume_profile(date):
  date = '2022-12-01'
  
  close = data.get('price:收盤價')
  vol = data.get('price:成交股數')
  date = close.index>=date 
  # close.index<='2023-02-17'
  date="'2022-12-01':'2023-02-17'"
  stock = '2706'
  # close = close[date][stock]
  # vol = vol[date][stock]
  close = close.loc['2022-12-01':'2023-02-17',[stock]]
  vol = vol.loc['2022-12-01':'2023-02-17',[stock]]

  close = close.reset_index()
  vol = vol.reset_index()
  vol_close = vol.merge(close,on='date')
  h = px.histogram(vol_close, x=vol_close.columns[1], y=vol_close.columns[2], nbins=50, orientation='h').show()
  pass

def investors_conference():
  conf = data.get('investors_conference')
  close = data.get('price:收盤價')
  # data.get('price:最低價')
  # data.get('price:最高價')
  DATE = '2020'
  # selected_dates = conf.index > '2020'
  close = close[close.index > DATE]
  close_next = close.shift(-1)
  conf = conf[conf.index > DATE]
  
  df_raw_column_label = ['日期','代號','名稱','漲幅']
  df_stat_column_label = ['代號','名稱','說明會次數','上漲機率','下跌機率','平均幅度','平均上漲幅度','平均下跌幅度','權證']

  df_raw = pd.DataFrame(columns=df_raw_column_label)
  for date,row in conf.iterrows():
    stock_id = row['stock_id']
    stock_name = row['公司名稱']
    try:
      c1 = close.loc[date,[stock_id]][-1]
      c2 = close_next.loc[date,[stock_id]][-1]
    except KeyError:
      continue
    v = ((c2-c1)/c1)*100
    new_row = {df_raw_column_label[0]:date.strftime('%Y-%m-%d'), 
               df_raw_column_label[1]:stock_id, 
               df_raw_column_label[2]:stock_name,
               df_raw_column_label[3]:v}
    df_raw = df_raw.append(new_row, ignore_index=True)
    
  stock_ids = df_raw[df_raw_column_label[1]].unique()
  if len(stock_ids) > 0:
    df_stat = pd.DataFrame(columns=df_stat_column_label)
    for s in stock_ids:
      current_stock_info = df_raw.loc[df_raw[df_raw_column_label[1]]==s]
      count = len(current_stock_info.index)
      up_rows = current_stock_info[df_raw_column_label[3]]>=0
      down_rows = current_stock_info[df_raw_column_label[3]]<0
      v1 = up_rows.values.sum()/count                                         #上漲機率
      v2 = 1 - v1                                                             #下跌機率
      v3 = current_stock_info[df_raw_column_label[3]].abs().mean()            #平均幅度
      v4 = current_stock_info[up_rows][df_raw_column_label[3]].mean()         #平均上漲幅度
      v5 = abs(current_stock_info[down_rows][df_raw_column_label[3]].mean())  #平均下跌幅度
      new_row = {
        df_stat_column_label[0]:s, 
        df_stat_column_label[1]:get_stockname_by_ID(s),
        df_stat_column_label[2]:count, 
        df_stat_column_label[3]:v1, 
        df_stat_column_label[4]:v2,
        df_stat_column_label[5]:v3,
        df_stat_column_label[6]:v4,
        df_stat_column_label[7]:v5,
        df_stat_column_label[8]:has_warrant(s)}
      df_stat = df_stat.append(new_row, ignore_index=True)
    
    with pd.ExcelWriter('output.xlsx') as writer: # dump data to excel file
      df_raw.to_excel(writer, sheet_name='Raw data')
      df_stat.to_excel(writer, sheet_name='Statistic')
def get_investors_conference_date(id_file):
  with open(id_file,'r') as f:
    stock_date = {}
    for l in f.readlines():
      stock_date[l.strip()] = 'N/A'
    # df = pd.DataFrame(index=[l.strip() for l in f.readlines()])
  today = datetime.now()
  
  conf = data.get('investors_conference')
  conf = conf[conf.index > today]

  for id in stock_date.keys():
    row = conf.loc[conf['stock_id']==id]
    if not row.empty:
      conf_date = ";".join([s.strftime('%Y-%m-%d') for s in row.index])
      stock_date[id] = conf_date
      # df = df.append({'date':conf_date}, ignore_index=True)
      # df.at[id] = conf_date
  df = pd.DataFrame.from_dict(stock_date,orient='index')
  df.to_csv('date.csv',index=True)
  pass
  
def tmp():
  pass
  # NLargest = 15 # N largest brokers of stock amount
    # accDays = 30 #accumulation days
    # period = pd.date_range(start='2021',end='2023')
    # K_GT = get_K_GT(period=period,stocks=stocks,length=24,threshold_high=80,threshold_low=50)
    # output = dict()
    # for stock,dates in K_GT.items():
    #     D = pd.Series([d['L'][0] for d in dates]).drop_duplicates()
    #     tmpOutput = dict()
    #     for endDate in D:
    #         p = pd.date_range(end=endDate,periods=accDays,freq='D')
    #         period_data=bt.loc[bt.index.intersection(p)]
    #         x=period_data.reset_index().groupby(['stock_id','broker']).sum().loc[stock]
    #         y=x.assign(balance=x['buy']-x['sell']).nlargest(NLargest,'balance')['balance']
    #         y.index=broker_mapping.loc[y.index]['name']
    #         tmpOutput[p[0].strftime('%Y-%m-%d')+':'+p[-1].strftime('%Y-%m-%d')] = [i+'('+str(y[i])+')' for i in y.index]
    #     output[stock] = tmpOutput
    # with open('00733.json','w') as f:
    #     json.dump(output,f)
    
    # search_BB_Uband_hit(data)
if __name__=="__main__":
  init()
  # volume_profile('2022-07-01')
  # investors_conference()
  get_investors_conference_date('stock_id.txt')