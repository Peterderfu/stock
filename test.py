from finlab.dataframe import FinlabDataFrame
from finlab import data
import finlab
import pandas as pd
import pandas_ta as ta
with open("finlab_token.txt",mode='r') as f:
    finlab.login(f.readline())
data.set_storage(data.CacheStorage())
broker_mapping = data.get('broker_mapping',save_to_storage=True)
buy = data.get('broker_transactions',save_to_storage=True)
pass