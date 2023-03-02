from finlab.dataframe import FinlabDataFrame
from finlab import data
from finlab.backtest import sim
from talib import MA_Type
from peterlib import *
import finlab,json
import pandas as pd
import pandas_ta as ta
import numpy as np
    
if __name__=="__main__":
    init()
#############################################################
    #BBand帶寬%, 5%以下=>窄
    W=5
    #帶寬小於W之連續天數
    N=5
    #突破斜率%
    G=0.8
    # break_nextday_stat(data,W,N,G)
    # rotation_break_result = rotation_break(data,W,N,G)
    # print(rotation_break_today(data,W,N,G))
    print(rotation_break_week(data,W,N,G))
    # print(rotation_break_month(data,W,N,G))

    # entries = rotation_break(data,W,N,G)
    # exits = price_below_bband_upper(data) 
    # pb = data.get('price_earning_ratio:股價淨值比') 

    # position = entries.hold_until(exits, nstocks_limit=10, rank=-pb)
    # backtest_report = sim(position, upload=False)
    # backtest_report.benchmark = data.get('benchmark_return:發行量加權股價報酬指數').squeeze()
    # backtest_report.display()

