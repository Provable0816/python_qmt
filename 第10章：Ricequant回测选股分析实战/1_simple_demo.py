# 可以自己import我们平台支持的第三方python模块，比如pandas、numpy等。

# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    # 在context中保存全局变量
    context.hs300 = index_components("沪深300")
    scheduler.run_monthly(filter_data,tradingday=1)
    # 实时打印日志
    # logger.info("RunInfo: {}".format(context.run_info))

# before_trading此函数会在每天策略交易开始前被调用，当天只会被调用一次
def before_trading(context):
    """
    context.fundamentals_df = get_fundamentals(query(
        fundamentals.income_statement.revenue
    ).filter(
        fundamentals.income_statement.stockcode.in_(context.hs300)        
    ).order_by(
        fundamentals.income_statement.revenue.desc()
    ).limit(10)
    )
    #context.fundamentals_df.T
    context.hs300_10 = context.fundamentals_df.T.index 
    # print (context.fundamentals_df.T)
    """
    pass

def filter_data(context, bar_dict):
    context.fundamentals_df = get_fundamentals(query(
        fundamentals.income_statement.revenue
    ).filter(
        fundamentals.income_statement.stockcode.in_(context.hs300)        
    ).order_by(
        fundamentals.income_statement.revenue.desc()
    ).limit(10)
    )
    #context.fundamentals_df.T
    context.hs300_10 = context.fundamentals_df.T.index 


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    # 开始编写你的主要的算法逻辑

    # bar_dict[order_book_id] 可以拿到某个证券的bar信息
    # context.portfolio 可以拿到现在的投资组合信息

    # 使用order_shares(id_or_ins, amount)方法进行落单

    # TODO: 开始编写你的算法吧！
    # order_shares(context.s1, 1000)
    if len(context.portfolio.positions.keys()) !=0 :
        for stock in context.portfolio.positions.keys():
            if stock not in context.hs300_10:
                order_target_percent(stock, 0)
    for stock in context.hs300_10:
        order_target_percent(stock, 1/len(context.hs300_10))




# after_trading函数会在每天交易结束后被调用，当天只会被调用一次
def after_trading(context):
    pass
