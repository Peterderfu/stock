from finlab.dataframe import FinlabDataFrame
# from finlab import data, backtest
import pandas as pd
import finlab,json
from talib import MA_Type
from peterlib import rotation_break,My_BBANDS
from peterlib import *
import pandas_ta as ta
import numpy as np
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

    
if __name__=="__main__":
    with open("finlab_token.txt",mode='r') as f:
        finlab.login(f.readline())
    data.set_storage(data.FileStorage())
    
    price = get_price_twyahoo(stock_id=2330)
    if price:
        print(price)

    # # data.set_storage(data.CacheStorage())
    # broker_mapping = data.get('broker_mapping',save_to_storage=True)
    # bt = data.get('broker_transactions',save_to_storage=True)

    # stocks = ['9904','6669','3533','3443','3661','2376','3653','3017','1795','6285','9939','2206','6533','2707','1536','2607','1442','1760','1308','4551','1519','3454','5607','2530','4119','2497','8033','3138','6205','4763','2402','2228','4572','1529','3027','1342','2483','3004','2413','5284','1618','4566','3046','6152','3535','2613','8222','3025','3021','5225']
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
#############################################################
    #BBand帶寬%, 5%以下=>窄
    W=5
    #帶寬小於W之連續天數
    N=10
    #突破斜率%
    G=0.7
    # rotation_break_result = rotation_break(data,W,N,G)
    print(rotation_break_today(data,W,N,G))
    # print(rotation_break_week(data,W,N,G))
    pass
#     #開始觀察日
#     observe_date = '2023-2-1'
#     #觀察日數(開始觀察日往前的日數)
#     N=365
#     #發動後觀察天數
#     days_after_launch = 10
#     #觀察時突破比例(%)
#     breaking_ratio = 5
    
#     period_result = rotation_break_result[(pd.to_datetime(observe_date)-pd.Timedelta(days=N)):pd.to_datetime(observe_date)]
#     for c in period_result.columns:
#         match = period_result[c][period_result[c]==True]
#         if not match.empty:
#            print(match.name + ":" + match.index[0].strftime('%Y/%m/%d'))
#     exit
#     cbi = data.get('company_basic_info')
#     close = data.get('price:收盤價')
#     #列出股票代號：發動日期
#     for c in period_result.columns:
#         stock_series = period_result[c]
#         day_with_signal = stock_series[stock_series==True]
#         info = []
#         if len(day_with_signal) > 0:
#             P1 = close[c].reset_index()
           
#             try:
#                 name = cbi[cbi['stock_id'] == c].values[-1][-1]
#             except:
#                 name = "N/A"
#             name = name+"("+c+"):"
#             for i in day_with_signal.index:
#                 idx = P1[P1['date']==i].index
#                 period = P1.iloc[idx[0]:idx[0]+days_after_launch]
#                 desired_column = period.columns.values[-1]
#                 p = period[desired_column]
#                 pmax=np.nanmax(p.values)
#                 pfirst = p.values[0]
#                 day = i.strftime('%Y/%m/%d')
#                 if (abs(pmax-pfirst)/pfirst) > (breaking_ratio/100):
#                     info.append(day+"["+str(days_after_launch)+"d_"+str(breaking_ratio)+"%]")
#                 else:
#                     pass
#             if len(info)>0:        
#                 print(name+",".join(info)) 
# #############################################################