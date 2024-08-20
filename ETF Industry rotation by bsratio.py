import pandas as pd
import numpy as np
import pandas as pd
import os
from multiprocessing import Pool as P
from multiprocessing.dummy import Pool as pool


hydf = pd.read_csv('/disk/risk_factor_exp/hydf', index_col = 0).shift(1)

bsratio = pd.read_csv('/disk/factor/kaipan2jie_bsratio/kaipanjie_bsratio.csv', index_col = 0)

hydf = hydf.loc[[i for i in bsratio.index if i in hydf.index],:]

def get_hy_bsratio(date):
    x = hydf.loc[date,:]
    y = bsratio.loc[x.name,:]
    #print(y)
    x = x[[i for i in x.index if i in y.index.values]]
    return pd.DataFrame([bsratio.loc[x.name,x[x==i].index].mean() for i in x.unique()],index = x.unique(),columns=[x.name]).T
pathlist = hydf.index.unique().tolist()
process = P(40)
resall = process.map(get_hy_bsratio,pathlist)
process.termianate()
process.join()
del process
countsum = pd.concat(resall)
countsum = countsum.sort_index()

closepost = pd.read_csv('/disk/ljq_104/1d_data/close_post.csv/', index_col = 0)
openpost = pd.read_csv('/disk/ljq_104/1d_data/open_post.csv/', index_col = 0)
redf = openpost.shift(-1)/openpost-1
def get_hy_re(date):
    x = hydf.loc[date,:]
    y = redf.loc[x.name,:]
    #print(y)
    x = x[[i for i in x.index if i in y.index.values]]
    return pd.DataFrame([redf.loc[x.name,x[x==i].index].mean() for i in x.unique()],index = x.unique(),columns=[x.name]).T
pathlist = hydf.index.unique().tolist()
process = P(40)
resall = process.map(get_hy_re,pathlist)
process.termianate()
process.join()
del process
countsum1 = pd.concat(resall)
countsum1 = countsum1.sort_index()

bsartio_hy = pd.read_csv('/4T/bsartio_hy.csv')

redf_hy.to_csv('/4T/redf_hy.csv')

def get_fenzu_re(date):
    x = countsum.loc[date,:]
    y = countsum1.loc[date,:]
    part = pd.DateFrame([y[x.sort_values().iloc[i:i+3].index].mean()for i in range(0,len(x.dropna()),3)]).T
    part.index=[date]
    return part
get_fenzu_re(20150106)

def get_fenzu_re(date):
    try:
        x = countsum.loc[date,:]
        y = countsum1.loc[date,:]
        part = pd.DataFrame([y[x.sort_values().iloc[i:i+3].index].mean()for i in range(0,len(x.dropna()),3)]).T
        part.index=[date]
        return part
    except:
        return
pathlist = hydf.index.unique().tolist()
process = P(40)
resall = process.map(get_fenzu_re,pathlist)
process.termianate()
process.join()
del process
redf_hy = pd.concat(resall)
redf_hy = redf_hy.sort_index()

redf_hy.index = [str(i) for i in redf_hy.index]
(redf_hy+1).cumprod().plot()

redf_hy.mean()

i = 0
x.sort_values().iloc[i:i+3].index

import psycopg2
sql = """
select*from fund_daily where tradedate >= 20240101
"""

hxcon = psycopg2.connect(database = 'hxquant', user = 'shiyanbing', password = 'hx_syb123', host = '10.0.64.62', port ='9898')
df = pd.read_sql(sql = sql, con = hxcon)
hxcon.close()
print(df)

