from finlab import data
from talib import MA_Type

def My_BBANDS(data):
    return data.indicator('BBANDS',timeperiod=20,nbdevup=2.0, nbdevdn=2.0,matype=MA_Type.EMA)
def rotation_break(data,bband,NDay,break_rate):
  #bband:BBand帶寬%, 5%以下=>窄
  #NDay:帶寬小於bband之連續天數
  #break_rate:布林上(下)軌突破斜率
  print(f"尋找布林帶寬小於{bband}%且持續{NDay}日")

  #get BBand indicator
  upper,middle,lower= data.indicator('BBANDS',timeperiod=20,nbdevup=2.0, nbdevdn=2.0,matype=MA_Type.EMA)
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