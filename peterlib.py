from finlab import data
from talib import MA_Type
from datetime import datetime,timedelta

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
  #calculate launch rate
  upper_pre = upper.shift(1)
  lower_pre = lower.shift(1)
  if break_rate>0:
    brk = (abs(upper-upper_pre)/upper_pre)*100    
  else:
    brk = (abs(lower-lower_pre)/lower_pre)*100
    
  cond_1 = (width < bband).sustain(NDay) #帶寬小於bband且持續NDay天
  cond_2 = abs(brk) > abs(break_rate)     #突破斜率大於break_rate值
  entries = cond_1 & cond_2
  return entries

def rotation_break_today(data,bband,NDay,break_rate):
  cbi = data.get('company_basic_info')
  df = rotation_break(data,bband,NDay,break_rate)
  now = datetime.now()
  if now.hour < 18: # if time is earlier than 18 o'clock, go to previous day
    now = now - timedelta(days = 1)
  d = now.strftime("%Y-%m-%d")
  stocks = df.loc[d]
  name_list = []
  for s in stocks.index:
    if (stocks[s] == True):
      try:
        name = cbi[cbi['stock_id'] == s].values[-1][-1]        
      except:
        name = "N/A"        
      name = name+"("+s+")"
      name_list.append(d + ":" + name)
  return name_list