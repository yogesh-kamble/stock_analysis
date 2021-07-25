#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 23:14:35 2021

@author: yogesh
"""

from nsepy import get_history
from datetime import date
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--symbol', action="store", help="Stock Symbol", type=str)

args = parser.parse_args()

stock=args.symbol
start=start=date(2021,5,1)
end=date(2021,6,24)
end2=date(2021,7,29)
end3=date(2021,8,26)
data_nearmonth_fut = get_history(symbol=stock,futures=True,start=start, end=end,
expiry_date=end)
data_nextmonth_fut = get_history(symbol=stock,futures=True,start=start, end=end2,
expiry_date=end2)
data_farmonth_fut = get_history(symbol=stock,futures=True,start=start, end=end3,
expiry_date=end3)
stock_data = get_history(symbol=stock,start=start, end=end3)

# Prepare OI Combined data
OI_combined= pd.concat([data_nearmonth_fut['Open Interest'],data_nextmonth_fut['Open Interest'], data_farmonth_fut['Open Interest']],
axis=1)
OI_combined['oi_combined']=OI_combined.sum(axis=1)
OI_combined['close'] = stock_data.Close
OI_combined['price_change'] = (stock_data['Close'].pct_change()) * 100
OI_combined['oi_change'] = OI_combined['oi_combined'].diff()
OI_combined['oi_pct_change'] = (OI_combined['oi_combined'].pct_change()) * 100
OI_combined['delivery'] = stock_data['Deliverable Volume']
OI_combined['%Deliverble'] = stock_data['%Deliverble']
OI_combined['VWAP'] = stock_data['VWAP']
OI_combined['5d_del_avg'] = stock_data.iloc[:,12].rolling(window=5).mean()
OI_combined['chg_delivery'] =  OI_combined['delivery'] / OI_combined['5d_del_avg']

OI_combined['long_build_up'] = np.where((OI_combined['price_change'] > 0) & (OI_combined['oi_change'] > 0) & (OI_combined.index != end), OI_combined['oi_change'], 0)
OI_combined['short_buildup'] = np.where((OI_combined['price_change'] < 0) & (OI_combined['oi_change'] > 0) & (OI_combined.index != end), OI_combined['oi_change'], 0)
OI_combined['long_unwinding'] = np.where((OI_combined['price_change'] < 0) & (OI_combined['oi_change'] < 0) & (OI_combined.index != end), OI_combined['oi_change'], 0)
OI_combined['short_covering'] = np.where((OI_combined['price_change'] > 0) & (OI_combined['oi_change'] < 0) & (OI_combined.index != end), OI_combined['oi_change'], 0)
OI_combined['total_long_buildup_14'] = OI_combined['long_build_up'].rolling(window=14).sum() + OI_combined['long_unwinding'].rolling(window=14).sum()
OI_combined['total_short_buildup_14'] = OI_combined['short_buildup'].rolling(window=14).sum() + OI_combined['short_covering'].rolling(window=14).sum()


# Plot Line graph
fig, axs = plt.subplots(2)
#plt.figure(figsize=[15,10])
# OI_combined.dropna(inplace=True)
plt.grid(True)
#df.index = df.Date
#plt.xticks(df['Date'])
axs[0].plot(OI_combined.index, 'close', data=OI_combined, label='Price')
axs[0].legend(loc=2)

axs[1].plot(OI_combined.index, 'total_long_buildup_14', data=OI_combined, label='SMA 14 days long')
axs[1].plot(OI_combined.index, 'total_short_buildup_14', data=OI_combined, label='SMA 14 days short')
# xs[0].plot(df['delivery_SMA_10'],label='SMA 10 days delivery')
axs[1].legend(loc=2)
plt.legend()
plt.show()
