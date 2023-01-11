from finlab import data
from talib import MA_Type

def price_rotation(data,bband,NDay,upturn):
  #bband:BBand帶寬%, 5%以下=>窄
  #NDay:帶寬小於bband之連續天數
  #upturn:上翹斜率
  
  #get BBand indicator
  upper,middle,lower= data.indicator('BBANDS',timeperiod=20,matype=MA_Type.EMA)
  #calcuate BBand width
  width = ((upper/lower)-1)*100
  #calculate launch rate
  upper_pre = upper.shift(1)
  launch = (1-(upper_pre/upper))*100

  cond_1 = (width < bband).sustain(NDay) #帶寬小於bband且持續NDay天
  cond_2 = launch > upturn        #上翹斜率大於upturn值
  entries = cond_1 & cond_2
  return entries