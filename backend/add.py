import sqlite3
import requests
import os
import trading
import pandas as pd


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# db_path = os.path.join(BASE_DIR, "db.sqlite3") 
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()


API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
API_KEY = "e58be2f2-404d-4d5a-893a-cb486e74024d"

def fetch_top_100_coins():
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }
    params = {
        "start": "1",
        "limit": "50",
        "convert": "USD",
    }
    response = requests.get(API_URL, headers=headers, params=params)
    data = response.json()

    
    coins_dict = {coin['symbol']+'USDT': "BINANCE" for coin in data['data']}
    symbol_name_dict = {coin['symbol']+'USDT':coin['name'] for coin in data['data']}
    # df = pd.DataFrame(list(coins_dict.items()), columns=["Symbol", "Exchange"])
    # df.to_csv("top_100_coins.csv", index=False)

    return coins_dict, symbol_name_dict


def insert_coins_into_db():
    coins_dict, symbol_name_dict = fetch_top_100_coins()
    trading.saveToDatabase(coins_dict, symbol_name_dict)
    

fetch_top_100_coins()
if __name__ == "__main__":
    print()
    insert_coins_into_db()

# Bağlantıyı kapat
# conn.close()
