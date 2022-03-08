# 本篇给出了宏观因子择时的一种实现方式：采用宏观因子滞后期数据（避免预测时使用未来数据）与历史股指回报拟合模型，
# 在训练样本外期间使用得到参数预测股指回报，并进行相应操作。样本外回测表现不错，回撤小，回报高。
# 这里只提供一种思路，宏观因子选取、拟合模型等都还有不同的选择。

# libs
from __future__ import division
import seaborn as sns
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import math
import string
from sklearn import linear_model
import calendar

# settings
sns.set_style('whitegrid')
fsize = (12, 12*0.618)
today = dt.datetime.today().strftime('%Y%m%d')

def monthBefore(year = 2022, month = 1, delta = 2):
    # 获取delta个月之前的年月
    rtnMonth = (month + 12 - (delta%12)) % 12
    rtnMonth = 12 if rtnMonth == 0 else rtnMonth
    yearDelta = int((delta - month) / 12) + 1
    rtnYear = year - yearDelta if delta >= month else year
    return dt.datetime(rtnYear, rtnMonth, 1).strftime('%Y-%m')

print(monthBefore())


