import requests
import sqlite3
import json
import os

API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
API_KEY = "e58be2f2-404d-4d5a-893a-cb486e74024d"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "userdb.sqlite3") 

def create_coin_market_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS CMC_INFO (
        cmc_rank INTEGER PRIMARY KEY,
        id INTEGER,
        name TEXT,
        symbol TEXT,
        price REAL,
        market_cap REAL,
        market_cap_dominance REAL,
        volume_24h REAL,
        max_supply REAL,
        circulating_supply REAL,
        total_supply REAL,
        infinite_supply BOOL,
        date_added TEXT,
        tags TEXT,
        percent_change_1h REAL,
        percent_change_24h REAL,
        percent_change_7d REAL,
        percent_change_30d REAL,
        percent_change_90d REAL     
    )
    """)

    conn.commit()
    conn.close()

def insert_data_cmc_info(crypto_list):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for crypto in crypto_list:
        cursor.execute("""
        INSERT INTO CMC_INFO (cmc_rank, id, name, symbol, price, market_cap, market_cap_dominance, volume_24h, max_supply, circulating_supply, total_supply, infinite_supply, date_added, tags, percent_change_1h, percent_change_24h, percent_change_7d , percent_change_30d , percent_change_90d)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            crypto["cmc_rank"],
            crypto["id"],
            crypto["name"],
            crypto["symbol"],
            crypto["quote"]["USD"]["price"],
            crypto["quote"]["USD"]["market_cap"],
            crypto["quote"]["USD"]["market_cap_dominance"],
            crypto["quote"]["USD"]["volume_24h"],
            crypto["max_supply"],
            crypto["circulating_supply"],
            crypto["total_supply"],
            crypto["infinite_supply"],
            crypto["date_added"],
            json.dumps(crypto["tags"]),
            crypto["quote"]["USD"]["percent_change_1h"],
            crypto["quote"]["USD"]["percent_change_24h"],
            crypto["quote"]["USD"]["percent_change_7d"],
            crypto["quote"]["USD"]["percent_change_30d"],
            crypto["quote"]["USD"]["percent_change_90d"]
        ))

    conn.commit()
    conn.close()

def fetch_top_100_coins():
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }
    params = {
        "start": "1",
        "limit": "500",
        "convert": "USD",
    }
    response = requests.get(API_URL, headers=headers, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            crypto_list = data.get("data", [])
            
            if crypto_list:
                insert_data_cmc_info(crypto_list)
                print("Veriler SQLite'e başarıyla eklendi.")
            else:
                print("API'den geçerli bir veri alınamadı.")

        except ValueError:
            print("API yanıtı geçerli bir JSON formatında değil.")
    else:
        print(f"API isteği başarısız oldu. Durum Kodu: {response.status_code}")

create_coin_market_table()

fetch_top_100_coins()
