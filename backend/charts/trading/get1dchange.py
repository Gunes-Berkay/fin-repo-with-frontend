from tvDatafeed import TvDatafeed, Interval

def get_24h_change(symbol, exchange='BINANCE'):
    tv = TvDatafeed()
    data = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=2)

    previous_close = data['close'].iloc[0]
    current_close = data['close'].iloc[1]

    change_24h = ((current_close - previous_close) / previous_close) * 100

    return change_24h

