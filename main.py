from finlab.dataframe import FinlabDataFrame
from finlab import data, backtest
import pandas as pd
import finlab
from talib import MA_Type
from peterlib import rotation_break,My_BBANDS
import pandas_ta as ta
# broker_name = data.get('broker_mapping')
# bt = data.get('broker_transactions',save_to_storage=True).tail(200)

#(1) 找發動信號-->以bband為例，輸出stock_id與launch_date
#(2) 對stock_id的launch_date前N日內找出是否有分點對這隻股票累積囤貨

#盤整時，某券商持續吃貨，並發動突破 1)盤整：布林帶寬[(上軌/下軌)-1]<5%
#參考https://www.youtube.com/watch?v=NF2Fwa99i0o&t=1707s
#參考https://doc.finlab.tw/tools/2330_bband_rebound/



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
# def rotation_break


if __name__=="__main__":
    with open("finlab_token.txt",mode='r') as f:
        finlab.login(f.readline())
    data.set_storage(data.CacheStorage())
    # close = data.get('price:收盤價')
    # high  = data.get('price:最高價')
    # low   = data.get('price:最低價')

    K = data.indicator('kdj')[0]
    # xx=ta.kdj(high=high,low=low,close=data)
    K_GT_80 = K[K.loc['2021':'2022',['2231']]>80].dropna()
    print(K_GT_80)
    pass
    # search_BB_Uband_hit(data)
#############################################################
    # #BBand帶寬%, 5%以下=>窄
    # W=6
    # #帶寬小於W之連續天數
    # N=20
    # #突破斜率%
    # G=1
    # rotation_break_result = rotation_break(data,W,N,G)
    # #開始觀察日
    # observe_date = '2023-1-16'
    # #觀察日數(開始觀察日往前的日數)
    # N=10
    # #發動後觀察天數
    # days_after_launch = 10
    # #觀察時突破比例(%)
    # breaking_ratio = 5
    # period_result = rotation_break_result[(pd.to_datetime(observe_date)-pd.Timedelta(days=N)):pd.to_datetime(observe_date)]
    # cbi = data.get('company_basic_info')
    # close = data.get('price:收盤價')
    # #列出股票代號：發動日期
    # for c in period_result.columns:
    #     stock_series = period_result[c]
    #     day_with_signal = stock_series[stock_series==True]
    #     info = []
    #     if len(day_with_signal) > 0:
    #         P1 = close[c]
    #         if G > 0:
    #             P2 = close[c].shift(-1*days_after_launch).rolling(days_after_launch).max() # days_after_launch天內最大價格
    #         else:
    #             P2 = close[c].shift(-1*days_after_launch).rolling(days_after_launch).min() # days_after_launch天內最小價格
           
    #         try:
    #             name = cbi[cbi['stock_id'] == c].values[-1][-1]
    #         except:
    #             name = "N/A"
    #         name = name+"("+c+"):"
    #         for i in day_with_signal.index:
    #             day = i.strftime('%Y/%m/%d')
    #             if (abs(P2[i]-P1[i])/P1[i]) > (breaking_ratio/100):
    #                 info.append(day+"["+str(days_after_launch)+"d_"+str(breaking_ratio)+"%]")
    #             else:
    #                 info.append(day)
                    
    #         print(name+",".join(info)) 
#############################################################