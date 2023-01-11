from finlab.dataframe import FinlabDataFrame
from finlab import data, backtest
import pandas as pd
import finlab
from talib import MA_Type

# broker_name = data.get('broker_mapping')
# bt = data.get('broker_transactions',save_to_storage=True).tail(200)

#(1) 找發動信號-->以bband為例，輸出stock_id與launch_date
#(2) 對stock_id的launch_date前N日內找出是否有分點對這隻股票累積囤貨

#盤整時，某券商持續吃貨，並發動突破 1)盤整：布林帶寬[(上軌/下軌)-1]<5%
#參考https://www.youtube.com/watch?v=NF2Fwa99i0o&t=1707s
#參考https://doc.finlab.tw/tools/2330_bband_rebound/

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

if __name__=="__main__":
    with open("finlab_token.txt",mode='r') as f:
        finlab.login(f.readline())
    data.set_storage(data.CacheStorage())
    #BBand帶寬%, 5%以下=>窄
    W=5
    #帶寬小於W之連續天數
    N=20
    #突破斜率%
    G=1

    result = rotation_break(data,W,N,G)
    

    #開始觀察日
    observe_date = '2023-1-11'
    #觀察日數(開始觀察日往前的日數)
    N=10
    #發動後觀察天數
    days_after_launch = 10
    #觀察時突破比例(%)
    breaking_ratio = 5

    period_result = result[(pd.to_datetime(observe_date)-pd.Timedelta(days=N)):pd.to_datetime(observe_date)]
    cbi = data.get('company_basic_info')
    close = data.get('price:收盤價')

    #列出股票代號：發動日期
    for c in period_result.columns:
        stock_series = period_result[c]
        day_with_signal = stock_series[stock_series==True]
        info = []
        if len(day_with_signal) > 0:
            P1 = close[c]
            if G > 0:
                P2 = close[c].shift(-1*days_after_launch).rolling(days_after_launch).max() # days_after_launch天內最大價格
            else:
                P2 = close[c].shift(-1*days_after_launch).rolling(days_after_launch).min() # days_after_launch天內最小價格
            
            try:
                name = cbi[cbi['stock_id'] == c].values[-1][-1]
            except:
                name = "N/A"
            name = name+"("+c+"):"
            for i in day_with_signal.index:
                day = i.strftime('%Y/%m/%d')
                if (abs(P2[i]-P1[i])/P1[i]) > (breaking_ratio/100):
                    info.append(day+"["+str(days_after_launch)+"d_"+str(breaking_ratio)+"%]")
                else:
                    info.append(day)
                    
            print(name+",".join(info)) 
    