# 输入股票代码，点击“全部运行”得到估值
ticker = '000848'

# --企业价值倍数估值--
# 可接受回本年数:7年
N = 7
# ------------------
# ----净现金流估值---
# 增长率：0%
increase = 0
# 折现率:8%
discount = 0.08

# 安全边际：10%
marginOfSafety = 0.1

import pandas as pd
import numpy as np


# 企业价值倍数估值
def getEnterpriceValueByROIC(ticker, N=7, marginOfSafety=0.2):
    # 平均的ROIC
    df_roic = DataAPI.FdmtIndiRtnGet(ticker=ticker, secID="", endDate="", beginDate="", beginYear=u"", endYear=u"",
                                     reportType=u"A", field=u"", pandas="1")

    avg_roic = df_roic['ROIC'].head(5).mean()
    result_roic = df_roic['ROIC'].tolist()[0]

    if result_roic > avg_roic:
        result_roic = avg_roic

    result_roic /= 100

    # IC = 股东权益（TShEquity） + 有息负债
    df_IC = DataAPI.FdmtBSAllLatestGet(ticker=ticker, secID=u"", reportType=u"", endDate=u"", beginDate=u"", year="",
                                       field=u"", pandas="1")
    # 有息负债 = 短期借款(STBorr) + 1年内到期的长期负债（NCLWithin1Y） + 长期借款（LTBorr） + 应付债券（bondPayable） + 长期应付款（LTPayable）
    df_IC_result = df_IC[['TShEquity', 'STBorr', 'NCLWithin1Y', 'LTBorr', 'bondPayable', 'LTPayable']]
    IC = df_IC_result.loc[0].sum()

    # EBIT
    EBIT = result_roic * IC

    # EV
    EV = N * EBIT

    # 有息负债
    df_IC_debt = df_IC[['STBorr', 'NCLWithin1Y', 'LTBorr', 'bondPayable', 'LTPayable']]
    debt = np.nan_to_num(df_IC_debt.loc[0].sum())

    # 现金
    cash = df_IC.loc[0].cashCEquiv

    # 可接受的总市值
    markcap = EV - debt + cash

    #  总股本
    df_totalShares = DataAPI.EquShareGet(secID=u"", ticker=ticker, beginDate=u"", endDate=u"", partyID=u"", field=u"",
                                         pandas="1")
    totalShares = df_totalShares.loc[0].totalShares

    # 可接受收盘价
    price = markcap / totalShares

    # 安全边际打折后的收盘价
    price = round(price * (1 - marginOfSafety), 2)

    return price


# 现金流估值
def getEnterpriceValueByCash(ticker, increase=0.1, discount=0.08, marginOfSafety=0.2):
    df = DataAPI.FdmtCFAllLatestGet(ticker=ticker, secID=u"", reportType=u"A", endDate=u"", beginDate=u"", year="",
                                    field=u"", pandas="1")
    df['cashflow'] = df['NCFOperateA'] - df['NCFFrInvestA']
    df['preCashflow'] = df['cashflow']
    df['preCashflow'][df.index] = df['cashflow'][df.index + 1]
    df['pct_chg'] = df['cashflow'] / df['preCashflow'] - 1

    df_temp = pd.DataFrame(np.zeros(10), columns=['净现金流'])

    index_increase = "净现金流增长率：%.0f%%" % (increase * 100)

    df_temp['净现金流'] = df['cashflow'].tolist()[0]
    df_temp[index_increase] = df_temp.index
    df_temp['净现金流'] = df_temp['净现金流'] * (1 + increase) ** df_temp[index_increase]

    df_temp['折现后价值'] = df_temp['净现金流'] * (1 - discount) ** df_temp[index_increase]

    # 可接受的总市值
    markcap = df_temp['折现后价值'].sum()

    #  总股本
    df_totalShares = DataAPI.EquShareGet(secID=u"", ticker=ticker, beginDate=u"", endDate=u"", partyID=u"", field=u"",
                                         pandas="1")
    totalShares = df_totalShares.loc[0].totalShares

    # 可接受收盘价
    price = markcap / totalShares

    # 安全边际打折后的收盘价
    price = round(price * (1 - marginOfSafety), 2)

    df_temp[index_increase] += 2017
    df_temp[index_increase] = df_temp[index_increase].astype(str) + "年"
    df_temp = df_temp.set_index(index_increase)
    df_temp['净现金流'] = np.round(df_temp['净现金流'] / 100000000, 2).astype(str) + "亿"
    df_temp['折现后价值'] = np.round(df_temp['折现后价值'] / 100000000, 2).astype(str) + "亿"
    df_temp['可接受的总市值'] = ""
    df_temp['可接受的总市值'].ix[-1] = np.round(markcap / 100000000, 2).astype(str) + "亿"
    df_temp['总股本'] = ""
    df_temp['总股本'].ix[-1] = str(round(totalShares / 100000000.0, 2)) + "亿股"
    df_temp['安全边际'] = ""
    df_temp['安全边际'].ix[-1] = "%.0f%%" % (marginOfSafety * 100)
    df_temp['可接受的收盘价'] = ""
    df_temp['可接受的收盘价'].ix[-1] = str(price) + "元"
    return df_temp.T


# 企业价值倍数估值，可接受的年年数7,安全边际20%

price = getEnterpriceValueByROIC(ticker, N, marginOfSafety)
print("可接受的收盘价为%s元" % price)
