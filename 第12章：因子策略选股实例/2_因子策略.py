import numpy as np
import pandas as pd
from statsmodels import regression
import statsmodels.api as sm

def init(context):
    scheduler.run_monthly(rebalance,1)

def rebalance(context, bar_dict):
    # 首先过滤掉不想要的股票
    stocks = filter_paused(all_instruments(type='CS').order_book_id)
    stocks = filter_st(stocks)
    stocks = filter_new(stocks)

    #查询想要的指标
    fundamental_df = get_fundamentals(
        query(
            fundamentals.eod_derivative_indicator.pb_ratio,
            fundamentals.eod_derivative_indicator.market_cap
        ).filter(
            fundamentals.income_statement.stockcode.in_(stocks)
        )
    ).T.dropna()

    #预处理操作：1.3sigma 2.standard 3.neutral
    no_extreme = filter_3sigma(fundamental_df['pb_ratio'])
    pb_ratio_standard = standard(no_extreme)
    pb_ratio_neutral = neutral(pb_ratio_standard,fundamental_df['market_cap'])

    #基于因子对池子做筛选
    q = pb_ratio_neutral.quantile(0.2)
    storck_list = pb_ratio_neutral[pb_ratio_neutral <= q].index
    context.storck_list = storck_list

    #拿到手里有的
    context.last_main_symbol = context.portfolio.positions
    #删掉不在当前因子选中的池子中的股票
    context.detele = set(context.last_main_symbol).difference(context.storck_list)

    if len(context.detele) != 0:
        print ('调仓')
        for stock in context.detele:
            order_target_percent(stock,0)
    for stock in context.storck_list:
        order_target_percent(stock,1/len(context.storck_list))

# 去极值操作
def filter_3sigma(series,n=3):
    mean = series.mean()
    std = series.mean()
    max_range = mean + n*std
    min_range = mean - n*std
    return np.clip(series,min_range,max_range)

# 标准化操作
def standard(series):
    mean = series.mean()
    std = series.mean()
    return (series - mean)/std

# 中性化操作
def neutral(factor,market_cap):
    y = factor
    x = market_cap
    result = sm.OLS(y.astype(float),x.astype(float)).fit()
    return result.resid

# 判断是否停牌    
def filter_paused(stock_list):
    return [stock for stock in stock_list if not is_suspended(stock)]

#判断是否ST股
def filter_st(stock_list):
    return [stock for stock in stock_list if not is_st_stock(stock)]

#判断是否是新股
def filter_new(stock_list):
    return [stock for stock in stock_list if instruments(stock).days_from_listed() >= 180]

# before_trading此函数会在每天交易开始前被调用，当天只会被调用一次
def before_trading(context):
    pass


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    pass


# after_trading函数会在每天交易结束后被调用，当天只会被调用一次
def after_trading(context):
    pass

