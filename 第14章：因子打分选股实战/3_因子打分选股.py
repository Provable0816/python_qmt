# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。

# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
import numpy as np
import pandas as pd
def init(context):
    # 在context中保存全局变量
    # 实时打印日志
    # logger.info("RunInfo: {}".format(context.run_info))
    context.stocks = index_components('沪深300')
    context.lastrank = []
    scheduler.run_monthly(rebalance,1)

def rebalance(context, bar_dict):
    stocks = set(get_stocks(context))
    holdings = set(get_holdings(context))
    to_buy = stocks - holdings
    to_sell = holdings - stocks
    for stock in to_sell:
        order_target_percent(stock,0)
    if len(to_buy) == 0:
        return 
    average_value = context.portfolio.portfolio_value/len(to_buy)
    for stock in to_buy:
        order_target_value(stock,average_value)


def get_holdings(context):
    positions = context.portfolio.positions
    holdings = []
    for  position in positions:
        if positions[position].quantity > 0:
            holdings.append(position)
    return holdings




def get_stocks(context):

    fundamental_df_up = get_fundamentals(query(
        fundamentals.financial_indicator.diluted_earnings_per_share, #每股收益EPS 越高越好
        fundamentals.financial_indicator.return_on_equity,# 净资产收益率 越高越好
        fundamentals.financial_indicator.return_on_invested_capital,#净资产回报率，越高越好
    ).filter(fundamentals.income_statement.stockcode.in_(context.stocks))).T

    fundamental_df_down = get_fundamentals(query(
        fundamentals.financial_indicator.debt_to_asset_ratio, #资产负债率 越低越好
        fundamentals.eod_derivative_indicator.pb_ratio,# pb 越低越好
        fundamentals.eod_derivative_indicator.market_cap,#市值
    ).filter(fundamentals.income_statement.stockcode.in_(context.stocks))).T

    for fator in fundamental_df_up.columns.tolist(): #对越高越好进行打分
        fundamental_df_up.sort_values(by=fator,inplace=True)
        fundamental_df_up[fator] = np.linspace(1,len(fundamental_df_up),len(fundamental_df_up))
    for fator in fundamental_df_down.columns.tolist(): #对越低越好进行打分
        fundamental_df_down.sort_values(by=fator,inplace=True)
        fundamental_df_down[fator] = np.linspace(len(fundamental_df_up),1,len(fundamental_df_up))
    # 拼接
    fundamental_df_rank = fundamental_df_down.join(fundamental_df_up)
    fundamental_df_rank['score'] = np.zeros([len(fundamental_df_rank),1])
    
    #计算总分并排序
    fundamental_df_rank = fundamental_df_rank.cumsum(axis=1).sort_values(by='score',ascending=False)
    rank = fundamental_df_rank.score
    return rank.index.tolist()[:10]
# before_trading此函数会在每天策略交易开始前被调用，当天只会被调用一次
def before_trading(context):
    pass


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    # 开始编写你的主要的算法逻辑

    # bar_dict[order_book_id] 可以拿到某个证券的bar信息
    # context.portfolio 可以拿到现在的投资组合信息

    # 使用order_shares(id_or_ins, amount)方法进行落单

    # TODO: 开始编写你的算法吧！
    #order_shares(context.s1, 1000)
    pass

# after_trading函数会在每天交易结束后被调用，当天只会被调用一次
def after_trading(context):
    pass
