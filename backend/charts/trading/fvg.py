import sqlite3
import pandas as pd
import os 


interval_percantage_dict = {}

def find_fvg_levels(db_path, symbol, interval):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # query için bir de class sınıfının numarasına göre yüzdelik etkileşim değişecek, intervala göre de eklenecek
    
    query = f"""
    SELECT datetime, open, high, low, close 
    FROM {symbol}on{interval} 
    ORDER BY datetime ASC
    """
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"[!] Tablo bulunamadı veya sorgu hatalı: {symbol}on{interval} — {e}")
        conn.close()
        return
    
    bullish_fvg = []
    bearish_fvg = []
    percantage = 1
    

    for i in range(1, len(df) - 1):
        prev_high = df.iloc[i - 1]['high']
        prev_low = df.iloc[i - 1]['low']
        next_high = df.iloc[i + 1]['high']
        next_low = df.iloc[i + 1]['low']
        
        if (prev_high*(100+percantage)/100) < next_low:
            direction = "up"          
            bullish_fvg.append((df.iloc[i]['datetime'], prev_high, next_low, direction, 0,0,0))
        
        elif (prev_low > (next_high*(percantage+100)/100)):
            direction = "bottom"            
            bearish_fvg.append((df.iloc[i]['datetime'], next_high, prev_low, direction, 0,0,0))
    
    fvg_table = f"{symbol}on{interval}_fvg"
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {fvg_table} (
        datetime TEXT,
        start_price REAL,
        end_price REAL,
        direction TEXT,
        touch_start BOOLEAN,
        touch_half BOOLEAN,
        touch_end BOOLEAN
    )""")
    
    cursor.executemany(f"INSERT INTO {fvg_table} (datetime, start_price, end_price, direction, touch_start, touch_half, touch_end) VALUES (?, ?, ?, ?, ?, ?, ?)", bullish_fvg)
    cursor.executemany(f"INSERT INTO {fvg_table} (datetime, start_price, end_price, direction, touch_start, touch_half, touch_end) VALUES (?, ?, ?, ?, ?, ?, ?)", bearish_fvg)

    conn.commit()
    conn.close()
    print(f" FVG seviyeleri {fvg_table} tablosuna kaydedildi.")


def find_fvg_levels_foreach(coins_dict, interval):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "papers.sqlite3")
    for symbol in coins_dict.keys():
        find_fvg_levels(db_path, symbol, interval)
        print(f"{symbol} için FVG seviyeleri bulundu.")
