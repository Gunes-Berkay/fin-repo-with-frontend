import ccxt
import pandas as pd

def get_most_gainers_and_losers():
    exchange = ccxt.okx()
    markets = exchange.load_markets()
    swap_markets = [symbol for symbol in markets if markets[symbol]['swap'] and '/USDT:USDT' in symbol]
    swap_tickers = {}

    for symbol in swap_markets: 
        try:
            ticker = exchange.fetch_ticker(symbol)
            swap_tickers[symbol] = ticker
        except Exception as e:
            print(f"Hata {symbol}: {e}")

    if swap_tickers:
        most_gainers = sorted(
            (item for item in swap_tickers.items() if item[1].get('percentage') is not None),
            key=lambda x: x[1].get('percentage', 0),
            reverse=False 
        )
        most_losers = sorted(
            (item for item in swap_tickers.items() if item[1].get('percentage') is not None),
            key=lambda x: x[1].get('percentage', 0),
            reverse=False 
        )
               
        for i in range(0, 5):
            print(f"{most_gainers[i][0]} - Değişim yüzdesi: {most_gainers[i][1].get('percentage', 0)}%")
            
        for i in range(0, 5):
            print(f"{most_losers[i][0]} - Değişim yüzdesi: {most_losers[i][1].get('percentage', 0)}%")
    else:
        print("Hiçbir swap tick verisi alınamadı.")
    
