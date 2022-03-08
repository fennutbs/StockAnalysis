# 导入包

import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import talib as ta
import time

import matplotlib.colors as colors
import matplotlib.cm as cmx
import random as rd
import seaborn as sns




def get_trends(series):
    series = series.dropna()
    wu = len(series[series == 1])
    wd = len(series[series == 0])
    return 1.0 * (wu - wd) / (wu + wd)


def mypolyfit(close):
    # 收盘数据窗口拟合

    x = np.linspace(0, 1, len(close))
    cof = np.polyfit(x, close, 1)
    p = np.poly1d(cof)
    close_middle = p(x)[-1]

    return close_middle


def tech_ana(name):
    mylist = []
    index_close = DataAPI.MktIdxdGet(indexID=u"", ticker=name, tradeDate=u"", beginDate=u"", endDate=u"",
                                     exchangeCD=u"", field=u"", pandas="1")
    # print(index_close.tail(10).to_html())
    mylist.append(index_close.closeIndex.values[-1])
    mylist.append(ta.EMA(index_close.closeIndex.values, 5)[-1])
    mylist.append(ta.EMA(index_close.closeIndex.values, 10)[-1])
    mylist.append(ta.EMA(index_close.closeIndex.values, 20)[-1])
    mylist.append(ta.EMA(index_close.closeIndex.values, 60)[-1])
    mylist.append(ta.EMA(index_close.closeIndex.values, 120)[-1])
    mylist.append(ta.EMA(index_close.closeIndex.values, 240)[-1])
    mylist.append(ta.MA(index_close.closeIndex.values, 5)[-1])
    mylist.append(ta.MA(index_close.closeIndex.values, 10)[-1])
    mylist.append(ta.MA(index_close.closeIndex.values, 20)[-1])
    mylist.append(ta.MA(index_close.closeIndex.values, 60)[-1])
    mylist.append(ta.MA(index_close.closeIndex.values, 120)[-1])
    mylist.append(ta.MA(index_close.closeIndex.values, 240)[-1])
    mylist.sort()
    p = mylist.index(index_close.closeIndex.values[-1])
    return (float(p)) / (len(mylist) - 1)


def delextremum(array):
    '''
    去极值
    '''
    array = np.array(array)
    for i in range(1, 5):
        sigma = array.std()
        mu = array.mean()
        array[array > mu + 3 * sigma] = mu + 3 * sigma
        array[array < mu - 3 * sigma] = mu - 3 * sigma
    return array


def momentum(array, title=u"指数动量"):
    '''
    动量图
    '''
    day_begin = (datetime.now() - timedelta(days=380)).strftime('%Y-%m-%d')
    df_daily_industry_symbol = DataAPI.MktIdxdGet(tradeDate=u"", indexID=u"", ticker=array, beginDate=day_begin,
                                                  endDate=u"", field=u"secShortName,tradeDate,closeIndex", pandas="1")
    df_daily_industry_unstack = df_daily_industry_symbol.set_index(['tradeDate', 'secShortName']).unstack()[
        'closeIndex']
    increase_20 = 100 * (df_daily_industry_unstack.iloc[-1] / df_daily_industry_unstack.iloc[-21] - 1)
    increase_60 = 100 * (df_daily_industry_unstack.iloc[-1] / df_daily_industry_unstack.iloc[-61] - 1)
    increase_120 = 100 * (df_daily_industry_unstack.iloc[-1] / df_daily_industry_unstack.iloc[-121] - 1)
    increase_250 = 100 * (df_daily_industry_unstack.iloc[-1] / df_daily_industry_unstack.iloc[-251] - 1)
    df_daily_industry_increase = pd.DataFrame([increase_20, increase_60, increase_120, increase_250],
                                              columns=df_daily_industry_unstack.columns,
                                              index=[u"20日涨跌幅", u"60日涨跌幅", u"120日涨跌幅", u"250日涨跌幅"])
    df_daily_industry_increase = df_daily_industry_increase.round(1)
    df_daily_industry_increase = df_daily_industry_increase.T
    df_daily_industry_increase = df_daily_industry_increase.reset_index(drop=False)
    df_daily_industry_increase.index = df_daily_industry_increase["secShortName"].apply(lambda x: x.decode("utf-8"))
    df_daily_industry_increase = df_daily_industry_increase.drop(['secShortName'], axis=1)
    df_daily_industry_increase = df_daily_industry_increase.sort_values(u"20日涨跌幅", ascending=False)
    f, ax = plt.subplots(figsize=(30, 10))
    sns.heatmap(df_daily_industry_increase, annot=True, ax=ax)
    ax.set_xticklabels(df_daily_industry_increase.columns, fontproperties=font, fontsize=16)
    # index顺序互换
    ax.set_yticklabels(df_daily_industry_increase.index[::-1], fontproperties=font, rotation=0, fontsize=16)
    plt.title(title, fontproperties=font, fontsize=16)
    return


def value(index_index):
    # 获取指数的估值数据

    # 处理文件相关
    # 文件名
    path_name = "%s.csv" % index_index
    old_data = None
    # 读缓存文件
    try:
        old_data = pd.read_csv(path_name, index_col=0)
    except Exception as e:
        print(e)
        print('第一次运行时间较长')
        pass

        # 建立空的数据结构
    mypb = []
    mype = []
    mypepb = []
    totalmypb = []
    totalmype = []
    totalmypepb = []
    myclose = []
    # 获取指数开始日期
    if index_index == "zzzz":
        indexatart = DataAPI.IdxGet(secID=u"", ticker='000902', field=u"baseDate", pandas="1")
    else:
        indexatart = DataAPI.IdxGet(secID=u"", ticker=index_index, field=u"baseDate", pandas="1")
    start_date = indexatart.iloc[0, 0]
    start_date = '20080630'
    # HK_start_date=u"20060630"
    # HK_start_date='20080630'

    if old_data is not None:
        # 缓存数据回滚两个也就是两天时间，好统一处理
        old_data = old_data[:-2]
        old_end_date = old_data.index.values[-1].replace('-', '')
        print('数据缓存日期:' + old_end_date)
        # 文件记录最后日期的下一个日期
        start_date = (datetime.strptime(old_end_date, '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d')

    # 获取日期
    if index_index == "HSI":
        HK_data = DataAPI.TradeCalGet(exchangeCD=u"XHKG", beginDate=start_date,
                                      endDate=datetime.today().strftime('%Y%m%d'), isOpen=u"1", field=u"calendarDate",
                                      pandas="1")
        HK_Dates = map(lambda x: x, HK_data['calendarDate'].values.tolist())
    else:
        data = DataAPI.TradeCalGet(exchangeCD=u"XSHG", beginDate=start_date,
                                   endDate=datetime.today().strftime('%Y%m%d'), isOpen=u"1",
                                   field=u"calendarDate,isWeekEnd", pandas="1")
        Dates = map(lambda x: x, data['calendarDate'].values.tolist())

    mylen = []
    progress = []

    zzzz = pd.DataFrame()
    if index_index == 'zzzz':
        print(u"转债" + u'进度:'),
        for date in Dates:
            # 取指数收盘数据
            close = DataAPI.MktIdxdGet(indexID=u"", ticker="000902", tradeDate=date, beginDate=u"", endDate=u"",
                                       exchangeCD=u"", field=u"closeIndex", pandas="1")
            # 有时优矿数据更新不及时，容错处理
            if close.empty:
                if date > '2007-01-04':
                    print(' close error')
                continue
            zzzz.loc[date, 'close'] = close.iloc[0, 0]
            aaa1 = DataAPI.MktConsBondPremiumGet(SecID=u"", tickerBond=u"", beginDate=date, endDate=date, field=u"",
                                                 pandas="1")
            aaa1 = aaa1[aaa1['secShortNameBond'].str.contains('转')]
            aaa1 = aaa1.reset_index(drop=True)
            aaa1 = DataAPI.MktConsBondPerfGet(beginDate=date, endDate=date, secID=u"", tickerBond=aaa1["tickerBond"],
                                              tickerEqu=u"", field=u"", pandas="1")
            bbb1 = aaa1.median()
            zzzz.loc[date, 'closePriceBond'] = bbb1["closePriceBond"]
            zzzz.loc[date, 'bondPremRatio'] = bbb1["bondPremRatio"]
            zzzz.loc[date, 'puredebtPremRatio'] = bbb1["puredebtPremRatio"]
            # 进度条处理
            if (len(Dates) > 10):
                if progress != Dates.index(date) / int(len(Dates) / 10):
                    print
                    10 * Dates.index(date) / int(len(Dates) / 10),
                    progress = Dates.index(date) / int(len(Dates) / 10)

        print
        ''
        zzzz['close'] = [math.log1p(x) for x in zzzz['close']]
        # 把新的数据和老数据合并处理
        if old_data is not None:
            zzzz = pd.concat([old_data, zzzz])
        zzzz.to_csv(path_name)

        return (zzzz, u"转债")

    if index_index == 'HSI':
        # 此处日期根据缓存情况分别处理，如果是全部市场指数情况
        pepbdata = pd.DataFrame()
        print(u"恒生指数" + u'进度:'),
        for date in HK_Dates:

            # print(date)

            # 取指数收盘数据
            close = DataAPI.MktIdxdGet(indexID=u"", ticker=u"HSI", tradeDate=date, beginDate=u"", endDate=u"",
                                       exchangeCD=u"", field=u"closeIndex,CHGPct", pandas="1")
            # 有时优矿数据更新不及时，容错处理
            if close.empty:
                print(date),
                print(' 恒生指数收盘数据空缺')
                continue
            pepbdata.loc[date, 'close'] = close.iloc[0, 0]
            pepbdata.loc[date, 'CHGPct'] = close.iloc[0, 1]
            # 取每天的指数成分股的u"ticker,LCAP,PE,PB,TVMA20,LFLO"

            myindex_index = DataAPI.IdxConsGet(secID=u"", ticker=u"HSI", isNew=u"", intoDate=date, field=u"",
                                               pandas="1")

            data_temp = DataAPI.MktHKEqudGet(secID=list(myindex_index["consID"]), ticker=u"", tradeDate=date,
                                             beginDate=u"", endDate=u"", field=u"", pandas="1")

            if data_temp.empty:
                print(date),
                print(' 恒生股票数据空缺')
                continue

            aaa1 = len(data_temp)
            data_temp = data_temp.dropna(subset=["PE1"])
            data_temp = data_temp.dropna(subset=["PB"])
            data_temp = data_temp.dropna(subset=["marketValue"])
            data_temp = data_temp.dropna(subset=["turnoverValue"])
            data_temp = data_temp.dropna(subset=["negMarketValue"])

            data_temp["E"] = data_temp["marketValue"] / data_temp["PE1"]
            data_temp["B"] = data_temp["marketValue"] / data_temp["PB"]

            # 中位数市净率，市盈率
            pepbdata.loc[date, 'pb'] = data_temp.PB.median()
            pepbdata.loc[date, 'pe'] = data_temp.PE1.median()
            # 整体法市净率，市盈率
            pepbdata.loc[date, 'totalpb'] = data_temp["marketValue"].sum() / data_temp["B"].sum()
            pepbdata.loc[date, 'totalpe'] = data_temp["marketValue"].sum() / data_temp["E"].sum()
            pepbdata.loc[date, 'marketValue'] = data_temp["marketValue"].sum()
            pepbdata.loc[date, 'negMarketValue'] = data_temp["negMarketValue"].sum()
            pepbdata.loc[date, 'turnoverValue'] = data_temp["turnoverValue"].sum()

            # 进度条处理
            if (len(HK_Dates) > 10):
                if progress != HK_Dates.index(date) / int(len(HK_Dates) / 10):
                    print
                    10 * HK_Dates.index(date) / int(len(HK_Dates) / 10),
                    progress = HK_Dates.index(date) / int(len(HK_Dates) / 10)

        print
        ''
        pepbdata["pe"].replace(0, np.nan, inplace=True)
        pepbdata["pb"].replace(0, np.nan, inplace=True)
        pepbdata["totalpe"].replace(0, np.nan, inplace=True)
        pepbdata["totalpb"].replace(0, np.nan, inplace=True)

        pepbdata["close"].fillna(method='ffill', inplace=True)
        pepbdata["CHGPct"].fillna(method='ffill', inplace=True)
        pepbdata["pe"].fillna(method='ffill', inplace=True)
        pepbdata["pb"].fillna(method='ffill', inplace=True)
        pepbdata["totalpe"].fillna(method='ffill', inplace=True)
        pepbdata["totalpb"].fillna(method='ffill', inplace=True)
        pepbdata["marketValue"].fillna(method='ffill', inplace=True)
        pepbdata["negMarketValue"].fillna(method='ffill', inplace=True)
        pepbdata["turnoverValue"].fillna(method='ffill', inplace=True)

        pepbdata['close'] = [math.log1p(x) for x in pepbdata['close']]
        pepbdata['close'] = delextremum(pepbdata.loc[:, 'close'].values)
        pepbdata['pe'] = delextremum(pepbdata.loc[:, 'pe'].values)
        pepbdata['pb'] = delextremum(pepbdata.loc[:, 'pb'].values)
        pepbdata['totalpe'] = delextremum(pepbdata.loc[:, 'totalpe'].values)
        pepbdata['totalpb'] = delextremum(pepbdata.loc[:, 'totalpb'].values)

        # 把新的数据和老数据合并处理
        if old_data is not None:
            data = pd.concat([old_data, pepbdata])
        else:
            data = pepbdata
        data.to_csv(path_name)
        return (data, u"恒生指数")

    # 获取指数名字
    myname_index = DataAPI.IdxGet(secID=u"", ticker=index_index, indexGroup=u"", consType=u"", consMkt=u"",
                                  returnType=u"", indexTypeCD=u"", porgFullName=u"", secShortName=u"", wMethodCD="",
                                  pubName=u"", industryID=u"", sortID=u"", field=u"secShortName", pandas="1")
    # 建立数据结构
    pepbdata = pd.DataFrame()
    print(myname_index.iloc[0, 0].decode("utf-8") + u'进度:'),

    # 每天计算数据
    for date in Dates:
        # 取指数收盘数据
        close = DataAPI.MktIdxdGet(indexID=u"", ticker=index_index, tradeDate=date, beginDate=u"", endDate=u"",
                                   exchangeCD=u"", field=u"closeIndex,CHGPct", pandas="1")
        # 有时优矿数据更新不及时，容错处理
        if close.empty:
            if date > '2007-01-04':
                print(' close error')
            continue
        pepbdata.loc[date, 'close'] = close.iloc[0, 0]
        pepbdata.loc[date, 'CHGPct'] = close.iloc[0, 1]
        # 取每天的指数成分股的u"ticker,LCAP,PE,PB,TVMA20,LFLO"
        myindex_index = list(
            DataAPI.IdxConsGet(secID=u"", ticker=index_index, isNew=u"", intoDate=date, field=u"", pandas="1")[
                'consID'])
        data_temp = DataAPI.MktStockFactorsOneDayGet(tradeDate=date, secID=myindex_index,
                                                     field=u"ticker,LCAP,PE,PB,VOL20,VOL240", pandas="1").dropna(axis=0,
                                                                                                                 how='any')

        # 有时优矿数据更新不及时，容错处理
        if data_temp.empty:
            if date > '2007-01-04':
                print(date)
                print(' data error')
            continue

        # 按照市值从大到小排序，并重建索引
        data_temp = data_temp.sort_values('LCAP', ascending=False)
        data_temp = data_temp.reset_index(drop=True)
        # '000852.ZICN'中证1000指数，优矿的数据不全。程序重建指数，取市值800到1800的成分股数据。
        if index_index == '000852.ZICN':
            if len(data_temp) > 1000:
                data_temp = data_temp.iloc[800:(min(1800, len(data_temp)) - 1), :]

        data_temp = data_temp.reset_index(drop=True)
        mylen.append(len(data_temp))

        # 指数的每个成分股数据处理
        data_temp["LCAP"] = map(lambda x: np.e ** x, data_temp["LCAP"])
        data_temp["B"] = map(lambda x, y: x / y, data_temp["LCAP"], data_temp['PB'])
        data_temp["E"] = map(lambda x, y: x / y, data_temp["LCAP"], data_temp['PE'])

        # 中位数市净率，市盈率
        pepbdata.loc[date, 'pb'] = data_temp.PB.median()
        pepbdata.loc[date, 'pe'] = data_temp.PE.median()
        # 整体法市净率，市盈率
        pepbdata.loc[date, 'totalpb'] = data_temp["LCAP"].sum() / data_temp["B"].sum()
        pepbdata.loc[date, 'totalpe'] = data_temp["LCAP"].sum() / data_temp["E"].sum()
        # 20,240日平均换手率中位数
        pepbdata.loc[date, 'exchange'] = data_temp.VOL20.median()
        pepbdata.loc[date, 'VOL240'] = data_temp.VOL240.median()

        if (len(Dates) > 10):
            if progress != Dates.index(date) / int(len(Dates) / 10):
                print
                10 * Dates.index(date) / int(len(Dates) / 10),
                progress = Dates.index(date) / int(len(Dates) / 10)

    print
    ''

    # 指数收盘点位数据处理，去掉空数据，收盘数据取对数，去极值
    pepbdata = pepbdata.dropna(subset=['close'])
    pepbdata['close'] = [math.log1p(x) for x in pepbdata['close']]
    pepbdata['close'] = delextremum(pepbdata.loc[:, 'close'].values)

    pepbdata['pe'] = delextremum(pepbdata.loc[:, 'pe'].values)
    pepbdata['pb'] = delextremum(pepbdata.loc[:, 'pb'].values)
    pepbdata['totalpe'] = delextremum(pepbdata.loc[:, 'totalpe'].values)
    pepbdata['totalpb'] = delextremum(pepbdata.loc[:, 'totalpb'].values)

    if index_index == '000902':
        index_symbol = \
        DataAPI.IndustryGet(industryVersion=u"SW", industryVersionCD=u"", industryLevel=u"1", isNew=u"1", field=u"",
                            pandas="1")['indexSymbol'].tolist()
        index_symbol = [str(item) for item in index_symbol]
        df_daily_industry_symbol = DataAPI.MktIdxdGet(tradeDate=u"", indexID=u"", ticker=index_symbol, beginDate=u"",
                                                      endDate=u"", field=u"ticker,tradeDate,closeIndex", pandas="1")
        df_daily_industry_unstack = df_daily_industry_symbol.set_index(['tradeDate', 'ticker']).unstack()['closeIndex']
        # 日线级别MACD
        df_weekly_DEA = df_daily_industry_unstack.apply(lambda x: ta.MACD(x.values)[1], axis=0)
        df_weekly_flag = df_weekly_DEA[:]
        df_weekly_flag[df_weekly_flag > 0] = 1
        df_weekly_flag[df_weekly_flag < 0] = 0
        df_weekly_flag = df_weekly_flag.dropna(axis=0, how='all')

        trends_series = df_weekly_flag.apply(lambda x: get_trends(x), axis=1)
        trends_series = pd.DataFrame(trends_series).rename(columns={0: 'trends'})
        trends_series['tradeDate'] = trends_series.index
        trends_series['tradeDate'] = trends_series['tradeDate'].map(lambda x: datetime.strptime(x, '%Y-%m-%d'))
        trends_series = trends_series.drop('tradeDate', 1)
        trends_series["trends"] = trends_series["trends"] * 1.5 + 7
        trends_series = trends_series.ix[Dates]
        # 如果是全部市场情况，获取申万28个行业趋势度，巴菲特指标数据
        pepbdata = pepbdata.merge(trends_series, how='left', left_index=True, right_index=True)

    # 把新的数据和老数据合并处理
    if old_data is not None:
        data = pd.concat([old_data, pepbdata])
    else:
        data = pepbdata
    # 存储数据到缓存，并返回
    data.to_csv(path_name)

    return (data, myname_index.iloc[0, 0].decode("utf-8"))


# 计时开始
starttime = datetime.now()
result = []

# 数据列表['估值指数的数据代码',u'估值指数名称',"指数收盘数据代码",u'指数收盘数据名称','on：显示图表，off：不显示图表'],
myset = [
    ['000902', u'中证流通'],
    ['HSI', u'恒生指数'],
    ['zzzz', u'中证转债'],
    ['000016', u'上证50'],
    ['000300', u'沪深300'],
    ['000905', u'中证500'],
    ['000852', u'中证1000'],
    ['399371', u'国证价值'],
    ['399370', u'国证成长'],
    # ['000932',u'中证消费'],
    ['399608', u'科技100'],
    ['801150', u'申万医药生物'],
    ['801120', u'申万食品饮料'],
    # ['399550',u'央视50'],
    # ['399324',u'深证红利'],
    ['000922', u'中证红利'],
]
myset = np.array(myset)

mytotal = pd.DataFrame()

for i in range(0, len(myset)):
    (result, index_name) = value(myset[i, 0])
    # 两年一个时间戳
    interval = 500
    mylocs = range(0, len(result), interval)
    mylocs.append(len(result) - 1)
    mylabels = result.index.tolist()[0:len(result):interval]
    mylabels.append(result.index[len(result) - 1])

    print('最新日期:' + result.index.tolist()[-1])

    if myset[i, 0] == 'zzzz':
        result['close'] = [math.log1p(x) for x in result['close']]
        plt.figure(figsize=(30, 10))
        plt.subplot(121)
        result['close'].plot(color='b')
        result['closePriceBond'].plot(secondary_y=True, color='r', linestyle='-.')
        result["twolow"] = result['bondPremRatio'] + result['puredebtPremRatio']
        result["twolow"].plot(secondary_y=True, color='c', linewidth=4)
        plt.title(u'左轴蓝颜色中证流通，右轴红颜色转债价格中位数', fontproperties=font, fontsize=16)
        # result['puredebtPremRatio'].plot(secondary_y=True,color='y',linestyle= '-.')
        plt.xticks(mylocs, mylabels)
        plt.grid(True, axis='y')
        plt.subplot(122)
        result['close'].plot(color='b')
        result['bondPremRatio'].plot(secondary_y=True, color='r', linestyle='-.')
        result['puredebtPremRatio'].plot(secondary_y=True, color='y', linestyle='-.')
        plt.xticks(mylocs, mylabels)
        plt.title(u'左轴蓝颜色中证流通，右轴红颜色转股溢价率中位数，右轴黄颜色纯债溢价率中位数', fontproperties=font, fontsize=16)
        plt.grid(True, axis='y')
        continue

    if myset[i, 0] == 'HSI':
        mn = 500 * 5
        close_middle = result['close'].rolling(window=mn, center=False).apply(mypolyfit)
        close_var = result['close'].rolling(window=mn, center=False).std()
        result['close_middle'] = close_middle
        result['close_up'] = close_middle + close_var
        result['close_down'] = close_middle - close_var
        # 计算5年均线，7.5年均线，10年均线
        result['EMA1200'] = ta.EMA(result.close.values, 250 * 5)
        result['EMA1800'] = ta.EMA(result.close.values, 375 * 5)
        result['EMA2400'] = ta.EMA(result.close.values, 500 * 5)
        result['auto_invest'] = (result['EMA1800'] + result['close_down']) / 2
        # 收盘点位处于拟合的上下沿顶底的位置，作为时间域百分位
        value_close = (result['close'][-1] - result['close_down'][-1]) / (
                    result['close_up'][-1] - result['close_down'][-1])
        mn = 350 * 5
        # 中位数市净率百分位
        value_totalPE = len(
            [x for x in result[len(result) - mn:len(result)]['totalpe'] if x < result['totalpe'][-1]]) / float(mn)
        # 整体法最近七年市净率百分位
        value_totalPB = len(
            [x for x in result[len(result) - mn:len(result)]['totalpb'] if x < result['totalpb'][-1]]) / float(mn)
        value_total = (value_close + value_totalPE + value_totalPB) / 3
        p = 1 - value_total
        invest_holding = max((2 * p - 1) / 2, 0)

        mytotal1 = pd.DataFrame(
            {u'总估值': value_total, u'K线拟合估值': value_close, u'中位数PB估值': value_totalPE, u'整体法PB估值': value_totalPB,
             u'仓位': invest_holding, u'中位数PB': result['totalpe'][-1] / 100, u'整体法PB': result['totalpb'][-1] / 100,
             u'市场强度': tech_ana(myset[i, 0])}, index=[index_name])
        mytotal = mytotal.append(mytotal1)

        result['totalpe_10'] = result['totalpe'].rolling(window=mn, center=False).quantile(0.1)
        result['totalpe_20'] = result['totalpe'].rolling(window=mn, center=False).quantile(0.2)
        result['totalpe_50'] = result['totalpe'].rolling(window=mn, center=False).quantile(0.5)
        result['totalpe_80'] = result['totalpe'].rolling(window=mn, center=False).quantile(0.8)
        result['totalpe_90'] = result['totalpe'].rolling(window=mn, center=False).quantile(0.9)

        result['totalpb_10'] = result['totalpb'].rolling(window=mn, center=False).quantile(0.1)
        result['totalpb_20'] = result['totalpb'].rolling(window=mn, center=False).quantile(0.2)
        result['totalpb_50'] = result['totalpb'].rolling(window=mn, center=False).quantile(0.5)
        result['totalpb_80'] = result['totalpb'].rolling(window=mn, center=False).quantile(0.8)
        result['totalpb_90'] = result['totalpb'].rolling(window=mn, center=False).quantile(0.9)

        result['exchange_20'] = result['turnoverValue'].rolling(window=20, center=False).sum() / result[
            'negMarketValue'].rolling(window=20, center=False).sum()
        result['exchange_240'] = result['turnoverValue'].rolling(window=240, center=False).sum() / result[
            'negMarketValue'].rolling(window=240, center=False).sum()
        result['CHGPct_rolling_30'] = result['CHGPct'].rolling(window=30, center=False).std()
        result['CHGPct_rolling_250'] = result['CHGPct'].rolling(window=250, center=False).std()

        result['myzeshi_30'] = result['CHGPct_rolling_30'] / result['exchange_20']
        result['myzeshi_250'] = result['CHGPct_rolling_250'] / result['exchange_240']

        price_data1_close = result['close'].dropna()
        price_data1_myzeshi_250 = result['myzeshi_250'].dropna()
        price_data1_myzeshi_30 = result['myzeshi_30'].dropna()
        close_scale = max(price_data1_close) - min(price_data1_close)
        myzeshi_scale_250 = max(price_data1_myzeshi_250) - min(price_data1_myzeshi_250)
        myzeshi_scale_30 = max(price_data1_myzeshi_30) - min(price_data1_myzeshi_30)
        myscale_250 = close_scale / myzeshi_scale_250
        myscale_30 = close_scale / myzeshi_scale_30
        result['myzeshi_250'] = myscale_250 * result['myzeshi_250'] + min(price_data1_close) + 0.2
        result['myzeshi_30'] = myscale_30 * result['myzeshi_30'] + min(price_data1_close) + 0.2

        plt.figure(figsize=(30, 10))
        plt.subplot(121)
        result['totalpb'].plot()
        result['totalpb_10'].plot(color=u'g')
        result['totalpb_20'].plot(color=u'g')
        result['totalpb_50'].plot(color=u'y')
        result['totalpb_80'].plot(color=u'r')
        result['totalpb_90'].plot(color=u'r')
        plt.title(index_name + u" PB:" + str(round(result['totalpb'][-1], 1)) + u"；  百分位：" + str(
            round(100 * value_totalPB, 1)), fontproperties=font, fontsize=16)
        plt.xticks(mylocs, mylabels)
        plt.subplot(122)
        result['totalpe'].plot()
        result['totalpe_10'].plot(color=u'g')
        result['totalpe_20'].plot(color=u'g')
        result['totalpe_50'].plot(color=u'y')
        result['totalpe_80'].plot(color=u'r')
        result['totalpe_90'].plot(color=u'r')
        plt.title(index_name + u" PE:" + str(round(result['totalpe'][-1], 1)) + u"；  百分位：" + str(
            round(100 * value_totalPE, 1)), fontproperties=font, fontsize=16)
        plt.xticks(mylocs, mylabels)

        plt.figure(figsize=(30, 10))
        result['close'].plot(linewidth=4)
        result['EMA1200'].plot(linestyle='-.')
        result['EMA1800'].plot(linestyle='-.')
        result['EMA2400'].plot(linestyle='-.')

        result['close_up'].plot()
        result['close_middle'].plot()
        result['close_down'].plot()
        plt.xticks(mylocs, mylabels)
        result['auto_invest'].plot(color='red', linewidth=4)
        result['exchange_20'].plot(secondary_y=True, color='#808080', linestyle='-.')
        result['myzeshi_250'].plot(color='c', linestyle='-.')
        result['myzeshi_30'].plot(color='green', linestyle='-.')
        plt.title(index_name + u" 时间域百分位:" + str(round(100 * value_close, 1)) + u"；   综合百分位:" + str(
            round(100 * value_total, 1)) + u"；   点状灰线是人气指标，也就是换手率, 点状绿线是抄底指标", fontproperties=font, fontsize=16)
        continue

    # ------------------------------------------------------------------------------------------------------------------

    mn = 500 * 5
    close_middle = result['close'].rolling(window=mn, center=False).apply(mypolyfit)
    close_var = result['close'].rolling(window=mn, center=False).std()
    result['middle'] = close_middle
    result['up'] = close_middle + close_var
    result['down'] = close_middle - close_var
    # 计算5年均线，7.5年均线，10年均线
    result['EMA1200'] = ta.EMA(result.close.values, 250 * 5)
    result['EMA1800'] = ta.EMA(result.close.values, 375 * 5)
    result['EMA2400'] = ta.EMA(result.close.values, 500 * 5)
    result['auto_invest'] = (result['EMA1800'] + result['down']) / 2

    # 收盘点位处于拟合的上下沿顶底的位置，作为时间域百分位
    value_close = (result['close'][-1] - result['down'][-1]) / (result['up'][-1] - result['down'][-1])
    # 七年时间
    mn = 350 * 5
    # 中位数市净率百分位
    # 最近七年百分位
    value_PB = len([x for x in result[len(result) - mn:len(result)]['pb'] if x < result['pb'][-1]]) / float(mn)
    # 整体法最近七年市净率百分位
    value_totalPB = len(
        [x for x in result[len(result) - mn:len(result)]['totalpb'] if x < result['totalpb'][-1]]) / float(mn)
    # 两份中位数市净率百分位，一份整体法市净率百分位，一份时间域百分位作为权重分配，来产生综合百分位
    value_total = (value_close + value_PB + value_totalPB) / 3
    # mytotal.loc[myset[i,0]] ==value_total
    # 根据市盈率和市净率产生预期年化收益率。预期年化收益率=分红率/PE+(1-分红率)*PB/PE，分红率统一设定为25%
    # p=(1-综合百分位)做为投资赢得概率，百分位越小，赢得概率越大
    # 2p-1作为激进仓位，（2p-1）/2作为保守仓位。次投资仓位原理来自齐东平的大数投资。当估值百分位是0的时候，激进仓位是100%，保守仓位是50%
    p = 1 - value_total
    invest_holding = max((2 * p - 1) / 2, 0)

    mytotal1 = pd.DataFrame(
        {u'总估值': value_total, u'K线拟合估值': value_close, u'中位数PB估值': value_PB, u'整体法PB估值': value_totalPB,
         u'仓位': invest_holding, u'中位数PB': result['pb'][-1] / 100, u'整体法PB': result['totalpb'][-1] / 100,
         u'市场强度': tech_ana(myset[i, 0])}, index=[index_name])
    mytotal = mytotal.append(mytotal1)

    # 从数据作图
    plt.figure(figsize=(30, 10))
    plt.subplot(121)
    result['pb'].plot()

    # 最近7年数据求百分位：10%，20%，50%，80%，90%
    result['pb_10'] = result['pb'].rolling(window=mn, center=False).quantile(0.1)
    result['pb_20'] = result['pb'].rolling(window=mn, center=False).quantile(0.2)
    result['pb_50'] = result['pb'].rolling(window=mn, center=False).quantile(0.5)
    result['pb_80'] = result['pb'].rolling(window=mn, center=False).quantile(0.8)
    result['pb_90'] = result['pb'].rolling(window=mn, center=False).quantile(0.9)

    result['totalpb_10'] = result['totalpb'].rolling(window=mn, center=False).quantile(0.1)
    result['totalpb_20'] = result['totalpb'].rolling(window=mn, center=False).quantile(0.2)
    result['totalpb_50'] = result['totalpb'].rolling(window=mn, center=False).quantile(0.5)
    result['totalpb_80'] = result['totalpb'].rolling(window=mn, center=False).quantile(0.8)
    result['totalpb_90'] = result['totalpb'].rolling(window=mn, center=False).quantile(0.9)
    plt.title(index_name + u" PB(中位数):" + str(round(result['pb'][-1], 1)) + u"；  百分位：" + str(round(100 * value_PB, 1)),
              fontproperties=font, fontsize=16)
    xmin, xmax = plt.xlim()

    result['pb_10'].plot(color=u'g')
    result['pb_20'].plot(color=u'g')
    result['pb_50'].plot(color=u'y')
    result['pb_80'].plot(color=u'r')
    result['pb_90'].plot(color=u'r')

    plt.xticks(mylocs, mylabels)
    plt.hlines(result['pb'][-1], xmin, xmax, color='#808080', linestyle='-.')
    plt.legend(['PB', '10-20%', 'Current', '50%', '80-90%'], fontsize='small', loc='best')
    plt.subplot(122)
    result['totalpb'].plot()
    plt.title(index_name + u" PB(整体法):" + str(round(result['totalpb'][-1], 1)) + u"；  百分位：" + str(
        round(100 * value_totalPB, 1)), fontproperties=font, fontsize=16)
    xmin, xmax = plt.xlim()
    result['totalpb_10'].plot(color=u'g')
    result['totalpb_20'].plot(color=u'g')
    result['totalpb_50'].plot(color=u'y')
    result['totalpb_80'].plot(color=u'r')
    result['totalpb_90'].plot(color=u'r')
    plt.xticks(mylocs, mylabels)
    plt.hlines(result['totalpb'][-1], xmin, xmax, color='#808080', linestyle='-.')
    plt.legend(['PB', '10-20%', 'Current', '50%', '80-90%'], fontsize='small', loc='best')
    plt.figure(figsize=(30, 10))
    result['close'].plot(linewidth=4)
    result['EMA1200'].plot(linestyle='-.')
    result['EMA1800'].plot(linestyle='-.')
    result['EMA2400'].plot(linestyle='-.')
    result['up'].plot()
    result['middle'].plot()
    result['down'].plot()
    result['auto_invest'].plot(color='red', linewidth=4)
    if myset[i, 0] == '000902':
        result['trends'].plot(color='red', linestyle='-.')
        plt.axhline(result['trends'][-1], color='red', linestyle='-.')
    plt.axhline(result['close'][-1], color='#808080', linestyle='-.')
    plt.legend(['close', 'EMA1200', 'EMA1800', 'EMA2400'], fontsize='small', loc='best')
    result['exchange'].plot(secondary_y=True, color='#808080', linestyle='-.')
    plt.axhline(result['exchange'][-1], color='#808080', linestyle='-.')
    plt.xticks(mylocs, mylabels)

    result['CHGPct_rolling_30'] = result['CHGPct'].rolling(window=30, center=False).std()
    result['CHGPct_rolling_250'] = result['CHGPct'].rolling(window=250, center=False).std()

    result['myzeshi_30'] = result['CHGPct_rolling_30'] / result['exchange']
    result['myzeshi_250'] = result['CHGPct_rolling_250'] / result['VOL240']

    price_data1_close = result['close'].dropna()
    price_data1_myzeshi_250 = result['myzeshi_250'].dropna()
    price_data1_myzeshi_30 = result['myzeshi_30'].dropna()
    close_scale = max(price_data1_close) - min(price_data1_close)
    myzeshi_scale_250 = max(price_data1_myzeshi_250) - min(price_data1_myzeshi_250)
    myzeshi_scale_30 = max(price_data1_myzeshi_30) - min(price_data1_myzeshi_30)
    myscale_250 = close_scale / myzeshi_scale_250
    myscale_30 = close_scale / myzeshi_scale_30
    result['myzeshi_250'] = myscale_250 * result['myzeshi_250'] + min(price_data1_close)
    result['myzeshi_30'] = myscale_30 * result['myzeshi_30'] + min(price_data1_close)
    result['myzeshi_250'].plot(color='c', linestyle='-.')
    result['myzeshi_30'].plot(color='green', linestyle='-.')

    if myset[i, 0] == '000902':
        plt.title(index_name + u" 时间域百分位:" + str(round(100 * value_close, 1)) + u"；   综合百分位:" + str(
            round(100 * value_total, 1)) + u" 点状红线是基于28个申万行业的趋势度，点状灰线是换手率, 点状绿线是抄底指标", fontproperties=font, fontsize=16)
    else:
        plt.title(index_name + u" 时间域百分位:" + str(round(100 * value_close, 1)) + u"；   综合百分位:" + str(
            round(100 * value_total, 1)) + u"；   点状灰线是人气指标，也就是换手率, 点状绿线是抄底指标", fontproperties=font, fontsize=16)
    plt.grid(True)

    if myset[i, 0] == '000902':
        # 读取国债历史数据
        try:
            old_data = pd.read_csv("10Ybond.csv", index_col=0)
        except Exception as e:
            print(e)
            print('缺少历史国债收益率文件')
            pass
        else:
            # 从优矿获取最新国债收益率数据
            end_date = datetime.today().strftime('%Y%m%d')
            new_data = DataAPI.BondCmYieldCurveGet(beginDate=u"20191202", endDate=end_date.replace('-', ''),
                                                   curveCD=u"01", curveTypeCD=u"1", maturity="10.0", field=u"",
                                                   pandas="1")
            # 数据处理
            del new_data['curveName']
            del new_data['maturity']
            del new_data['curveType']
            # 数据首尾对调
            new_data = new_data.sort_index(ascending=0)
            new_data = new_data.reset_index(drop=True)
            # 最新数据日期改为当天日期。此处理属于无奈之举，因为优矿国债数据更新不及时。不过这样处理不影响模糊的正确
            new_data.iloc[-1, 0] = end_date
            # 历史数据和最新数据合并
            tenY_bond = pd.concat([old_data, new_data])
            tenY_bond = tenY_bond.reset_index(drop=True)
            tenY_bond = tenY_bond.set_index(['tradeDate'])

            # 国债数据以天为周期，估值数据以周为周期。所以国债数据和估值数据采取并“AND”操作，改变国债数据周期为周
            result1 = pd.concat([result, tenY_bond], axis=1, join='inner')
            # 1/PE为中位数市盈率收益率
            result1['pe'] = 100 / result1['pe']
            result1['totalpe'] = 100 / result1['totalpe']
            # 作图
            result1['close'] = 1.5 * (result1['close'] - 5.5)
            result1['close'] = result1['close'] - 2.5
            result1['value'] = result1['yield'] / result1['pe']
            result1['totalvalue'] = result1['yield'] / result1['totalpe']
            result1['value'] = delextremum(result1['value'].values)
            result1['totalvalue'] = delextremum(result1['totalvalue'].values)

            result1['value_up'] = None
            result1['value_mean'] = None
            result1['value_down'] = None
            result1['totalvalue_up'] = None
            result1['totalvalue_mean'] = None
            result1['totalvalue_down'] = None
            # print(result1.tail(10).to_html())
            # print(result1.head(10).to_html())
            myweek = 350 * 5
            for k in range(myweek, len(result1)):
                # 方差法
                value_var1 = np.std(result1['value'][k - myweek:k])
                value_median1 = np.mean(result1['value'][k - myweek:k])
                result1.iloc[k, -6] = value_median1 + value_var1
                result1.iloc[k, -5] = value_median1
                result1.iloc[k, -4] = value_median1 - value_var1
                totalvalue_var1 = np.std(result1['totalvalue'][k - myweek:k])
                totalvalue_median1 = np.mean(result1['totalvalue'][k - myweek:k])
                result1.iloc[k, -3] = totalvalue_median1 + totalvalue_var1
                result1.iloc[k, -2] = totalvalue_median1
                result1.iloc[k, -1] = totalvalue_median1 - totalvalue_var1

            plt.figure(figsize=(30, 10))
            plt.subplot(121)
            result1['close'] = result1['close'] * 1.3
            result1['close'].plot(color='#808080', linestyle='-.')
            result1['value'].plot(color='b')
            plt.axhline(result1['value'][-1], color='b', linestyle='-.')
            result1['value_up'].plot(color=u'r')
            result1['value_mean'].plot(color=u'y')
            result1['value_down'].plot(color=u'g')
            plt.twinx()
            result1['yield'].plot(color='red', linewidth=1, linestyle='-.')
            plt.xticks(mylocs, mylabels)
            plt.title(u'蓝色10年国债收益率/中位数PE收益率（1/PE），灰颜色中证流通，红颜色10年国债收益率（右轴）', fontproperties=font, fontsize=16)

            plt.subplot(122)
            result1['close'] = result1['close'] / 1.5 / 1.5
            result1['close'].plot(color='#808080', linestyle='-.')
            result1['totalvalue'].plot(color='b')
            plt.axhline(result1['totalvalue'][-1], color='b', linestyle='-.')
            result1['totalvalue_up'].plot(color=u'r')
            result1['totalvalue_mean'].plot(color=u'y')
            result1['totalvalue_down'].plot(color=u'g')
            plt.twinx()
            result1['yield'].plot(color='red', linewidth=1, linestyle='-.')
            plt.xticks(mylocs, mylabels)
            plt.title(u'蓝色10年国债收益率/整体法PE收益率（1/PE），灰颜色中证流通，红颜色10年国债收益率（右轴）', fontproperties=font, fontsize=16)

mytotal = mytotal.multiply(100)
mytotal = mytotal.round(1)
cols = [u"总估值", u"市场强度", u"K线拟合估值", u"中位数PB", u"中位数PB估值", u"整体法PB", u"整体法PB估值", u"仓位"]
mytotal = mytotal.loc[:, cols]
print(mytotal.to_html())

for i in range(len(myset)):
    if myset[i, 0] == 'zzzz':
        continue
    if myset[i, 0] == 'HSI':
        continue

plt.figure(figsize=(30, 10))
plt.subplot(121)
plt.scatter(x=mytotal[u"中位数PB估值"], y=mytotal[u"整体法PB估值"], s=100, c='#929591')
xmin, xmax = plt.xlim()
ymin, ymax = plt.ylim()
xymax = max(xmax, ymax)
plt.xlim(xmax=xymax)
plt.ylim(ymax=xymax)
plt.xlim(xmax=105)
plt.ylim(ymax=105)
plt.xlim(xmin=-5)
plt.ylim(ymin=-5)
plt.title(u'PB百分位', fontproperties=font, fontsize=16)
plt.xlabel(u'中位数PB百分位', fontproperties=font)
plt.ylabel(u'整体法PB百分位', fontproperties=font)
plt.axhline(y=50, color='#15b01a', alpha=1)
plt.axvline(x=50, color='#15b01a', alpha=1)
for i in mytotal.index.values:
    plt.annotate(i, (mytotal[u"中位数PB估值"][i], mytotal[u"整体法PB估值"][i]), fontproperties=font, fontsize=9)

plt.subplot(122)
plt.scatter(x=mytotal[u"总估值"], y=mytotal[u"市场强度"], s=100, c='#929591')
xmin, xmax = plt.xlim()
ymin, ymax = plt.ylim()
xymax = max(xmax, ymax)
plt.xlim(xmax=xymax)
plt.ylim(ymax=xymax)
plt.xlim(xmax=105)
plt.ylim(ymax=105)
plt.xlim(xmin=-5)
plt.ylim(ymin=-5)
plt.title(u'横轴总估值，纵轴市场强度', fontproperties=font, fontsize=16)
plt.xlabel(u'总估值', fontproperties=font)
plt.ylabel(u'市场强度', fontproperties=font)
plt.axhline(y=50, color='#15b01a', alpha=1)
plt.axvline(x=50, color='#15b01a', alpha=1)
for i in mytotal.index.values:
    plt.annotate(i, (mytotal[u"总估值"][i], mytotal[u"市场强度"][i]), fontproperties=font, fontsize=9)

# 大盘小盘，价值成长
myclose_value = DataAPI.MktIdxFactorDateRangeGet(secID=u"399371.ZICN", ticker=u"", beginDate=u"20100104", endDate=u"",
                                                 field=u"tradeDate,Close", pandas="1")
myclose_value = myclose_value.rename(columns={'Close': 'value'})
myclose_grouth = DataAPI.MktIdxFactorDateRangeGet(secID=u"399370.ZICN", ticker=u"", beginDate=u"20100104", endDate=u"",
                                                  field=u"tradeDate,Close", pandas="1")
myclose_grouth = myclose_grouth.rename(columns={'Close': 'grouth'})
myclose_big = DataAPI.MktIdxFactorDateRangeGet(secID=u"000300.ZICN", ticker=u"", beginDate=u"20100104", endDate=u"",
                                               field=u"tradeDate,Close", pandas="1")
myclose_big = myclose_big.rename(columns={'Close': 'big'})
myclose_small = DataAPI.MktIdxFactorDateRangeGet(secID=u"000852.ZICN", ticker=u"", beginDate=u"20100104", endDate=u"",
                                                 field=u"tradeDate,Close", pandas="1")
myclose_small = myclose_small.rename(columns={'Close': 'small'})
myclose = pd.merge(myclose_value, myclose_grouth, on=['tradeDate'], how='outer')
myclose = pd.merge(myclose, myclose_big, on=['tradeDate'], how='outer')
myclose = pd.merge(myclose, myclose_small, on=['tradeDate'], how='outer')
myclose["value/grouth"] = myclose["value"] / myclose["grouth"]
myclose["big/small"] = myclose["big"] / myclose["small"]
myclose.set_index(["tradeDate"], inplace=True)
plt.figure(figsize=(30, 10))
myclose["value/grouth"].plot()
myclose["big/small"].plot()
plt.axhline(myclose["value/grouth"][-1], color='b', linestyle='-.')
plt.axhline(myclose["big/small"][-1], color='g', linestyle='-.')

plt.title('蓝颜色价值/成长，绿颜色大盘/小盘'.decode("utf-8"), fontproperties=font, fontsize=16)
plt.legend(loc='best')

momentum(["881001", "399001", "399006", "000688", "000001", "000300", "000905", "000852"], u"指数精选")
momentum(["399372", "399373", "399374", "399375", "399376", "399377"], u"九宫格基金动量")

# 申万2021
index_symbol = DataAPI.IndustryGet(industryVersion=u"", industryVersionCD=u"010321", industryLevel=u"1", isNew=u"1",
                                   field=u"", pandas="1")
momentum(index_symbol["indexSymbol"], u"申万2021行业动量")

endtime = datetime.now()
print(u'程序运行时间(秒):'),
print(endtime - starttime).seconds