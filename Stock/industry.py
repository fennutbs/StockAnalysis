import numpy as np
import pandas as pd
import calendar
import csv
import data_reload
from pandas.core.frame import DataFrame

# 环境参数设置
pd.options.display.max_columns = 100  # 显示所有列
# 数据准备
df_ind = []
df_mv = []


def get_mvConc01(gp):
    '''
    计算行业集中度指标
    params:
        gp->Series: 分组对象
    return
        ->float:返回包含计算好的行业集中度指标的df对象
    '''
    gp = gp.sort_values(ascending=False)  # 排序，从大到小
    return gp[:3].sum() / gp.sum()  # 计算前3位之和与总和的比值


def get_mvConc02(gp):
    '''
    计算行业集中度指标
    params:
        gp->Series: 分组对象
    return
        ->float:返回包含计算好的行业集中度指标的df对象
    '''
    return gp.max() / gp.median()  # 计算最大值与中位数的比值


def get_data(df_ind, df_mv):
    df_ind = data_reload.data_reload('df_ind.csv', df_ind)
    df_mv  = data_reload.data_reload('df_mv.csv', df_mv)


def All_industry(df_ind, df_mv):
    df = pd.merge(df_ind[['secID', 'industryID2']], df_mv[['secID', 'marketValue']],how='inner', left_on='secID', right_on='secID')  # 合并分类和市值数据
    df[['marketValue']] = df[['marketValue']].astype('float64')
    gp = df.groupby('industryID2')  # 按行业代码分类
    func = [('size', 'size'), ('mvConc01', get_mvConc01), ('mvConc02', get_mvConc02)]  # 对分组进行计算的函数列表
    df_conc = gp['marketValue'].agg(func)  # 运用函数列表计算
    df_conc = pd.merge(df_ind[['industryID2', 'industryName2']].drop_duplicates(), df_conc,
       how='inner', left_on='industryID2', right_index=True)  # 添加分类名称
    df_conc=df_conc.sort_values('industryID2').reset_index(drop=True)
    df_conc = df_conc.sort_values('mvConc02', ascending=False).reset_index(drop=True)      #结果展示
    print(df_conc)


def Single_industry(str):
    global df_ind, df_mv
    df_0101 = df_ind[df_ind['industryID2'] == str]
    df = pd.merge(df_0101[['secID', 'industryID2']], df_mv[['secID', 'secShortName', 'marketValue']], how='inner',left_on='secID',right_on='secID')
    df=df.sort_values('marketValue', ascending=False)
    mv_sum=df['marketValue'].sum()
    mv_head3=df['marketValue'][:3].sum()
    mv_median=df['marketValue'].median()
    mv_max= df['marketValue'].max()
    mv_conc01 = mv_head3/mv_sum
    mv_conc02 = mv_max/mv_median
    print("industryID:{} ; industryName:{}".format(df_0101.iloc[0]['industryID2'], df_0101.iloc[0]['industryName2']))
    print('')
    print('该行业的市场总值：{}'.format(df['marketValue'].sum()))
    print('该行业下共有上市公司家数：{}'.format(len(df_0101)))
    print('头部企业(前3）市值占比：{:.2%}'.format(mv_conc01))
    print('最大市值与中值比例：{:.2f}'.format(mv_conc02))
    df.reset_index(drop=True)


tradeDate = '20220225'  # 取当天日期或指定日期
print("数据采样日期：{}".format(tradeDate))
Stock_code = '0103032403'      # 取公司股票代码
get_data(df_ind, df_mv)
df_mv = pd.DataFrame(df_mv[1:], columns=df_mv[0])
df_ind = pd.DataFrame(df_ind[1:], columns=df_ind[0])
df_mv[['marketValue']] = df_mv[['marketValue']].astype('float64')

All_industry(df_ind, df_mv)
Single_industry(Stock_code)
