import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings') 
django.setup()

# Django modellerini buradan sonra import et
from charts.models import CMCInfo


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "databases/userdb.sqlite3")

old_conn = sqlite3.connect(db_path)
old_cursor = old_conn.cursor()

old_cursor.execute("SELECT * FROM CMC_INFO")
rows = old_cursor.fetchall()


for row in rows:
    cmc_info = CMCInfo(
        cmc_rank=row[0],
        id=row[1],
        name=row[2],
        symbol=row[3],
        price=row[4],
        market_cap=row[5],
        market_cap_dominance=row[6],
        volume_24h=row[7],
        max_supply=row[8],
        circulating_supply=row[9],
        total_supply=row[10],
        infinite_supply=row[11],
        date_added=row[12],
        tags=row[13],
        percent_change_1h=row[14],
        percent_change_24h=row[15],
        percent_change_7d=row[16],
        percent_change_30d=row[17],
        percent_change_90d=row[18]
    )
    cmc_info.save(using='default')

print(f"{len(rows)} satır başarıyla aktarıldı.")
