import sqlite3
import requests
import os
import trading
import fvg
import fvg_filler

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
        "start": "100",
        "limit": "10",
        "convert": "USD",
    }
    response = requests.get(API_URL, headers=headers, params=params)
    data = response.json()

    
    coins_dict = {coin['symbol']+'USDT': "BINANCE" for coin in data['data']}
    

    return coins_dict
coins_dict = fetch_top_100_coins()

def insert_coins_into_db():    
    #trading.saveToDatabase(coins_dict, '4h')
    fvg.find_fvg_levels_foreach(coins_dict, '4h')
    fvg_filler.control_all(coins_dict, '4h')
    
    


if __name__ == "__main__":
    print(coins_dict)
    insert_coins_into_db()
