# 导入tushare
import tushare as ts

pro = ts.pro_api('d6d118074a6897b9bf319308e0bcabe1b78dcd3ed39785b60a84bf18')


def GetMacroEcoData(start_q='2018Q1', end_q='2022Q1'):
    # 拉取GDP数据
    df_GDP = pro.cn_gdp(start_q='2018Q1', end_q='2022Q1')

    # 拉取CPI数据
    df_CPI = pro.cn_cpi(start_m='201801', end_m='202203')

    # 拉取PPI数据
    df_PPI = pro.cn_ppi(start_m='201905', end_m='202203')

    # 拉取货币供应量数据
    df_CN_M = pro.cn_m(start_m='201901', end_m='202203')

    return df_GDP, df_CPI, df_PPI, df_CN_M
