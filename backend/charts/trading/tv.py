import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval
import sqlite3, os
import numpy as np



tv = TvDatafeed()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "papers.sqlite3")
conn = sqlite3.connect(db_path)

interval_dict = {
    '1m' : Interval.in_1_minute,
    '5m' : Interval.in_5_minute,
    '15m': Interval.in_15_minute,
    '30m': Interval.in_30_minute,
    '1h' : Interval.in_1_hour,
    '4h' : Interval.in_4_hour,
    '1d' : Interval.in_daily,
    '1w' : Interval.in_weekly,
    '1mo': Interval.in_monthly
}
interval_mapping = {
    "1h": 60,
    "4h": 240,
    "1d": 1440
}

data = tv.get_hist(symbol='BTCUSDT', exchange='BINANCE', interval=Interval.in_4_hour, n_bars=500)
print(data)
