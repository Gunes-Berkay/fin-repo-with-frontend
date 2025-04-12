import json 
import sqlite3
import os 
import pandas as pd
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "papers.sqlite3") 
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

with open('veri.json', 'r', encoding="utf-8") as json_file:
    data = json.load(json_file)

def create_table():
   
    query = f"""
        CREATE TABLE IF NOT EXISTS CMC_INFO (
            id NUMBER,
            symbol TEXT,
            name TEXT,
            max_supply NUMBER,
            circulating_supply NUMBER,
            total_supply NUMBER,
            infinite_supply BOOLEAN,
            cmc_rank NUMBER
        )
    """
    cursor.execute(query)

    df = pd.DataFrame({
    'id': [coin['id'] for coin in data['data']],
    'name': [coin['name'] for coin in data['data']],
    'symbol': [coin['symbol'] for coin in data['data']],
    'max_supply': [coin['max_supply'] for coin in data['data']],
    'circulating_supply': [coin['circulating_supply'] for coin in data['data']],
    'total_supply': [coin['total_supply'] for coin in data['data']],
    'infinite_supply': [coin['infinite_supply'] for coin in data['data']],
    'cmc_rank': [coin['cmc_rank'] for coin in data['data']]
    })

    for _, row in df.iterrows():
        row_data = tuple(row[col] for col in df.columns)
        try:
            cursor.execute(f"""
                INSERT INTO CMC_INFO ({", ".join(df.columns)})
                VALUES ({", ".join(["?"] * len(df.columns))})
            """, row_data)
            conn.commit() 
        except Exception as e:
            print(f"Veri eklenirken hata oluştu: {e}")

create_table()




