import sys
import os
import django

# settings.py'nin bulunduğu dizini path'e ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # ../backend için

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()



import ccxt
import json
from charts.models import CMCInfo

selected_exchanges = [
    'binance', 'coinbase', 'kraken', 'kucoin', 'bitfinex',
    'bybit', 'okx', 'gateio', 'bitstamp'
]

def find_active_exchanges_for_symbol(symbol):
    active_exchanges = []

    for exchange_id in selected_exchanges:
        try:
            exchange_class = getattr(ccxt, exchange_id)
            exchange = exchange_class()
            markets = exchange.load_markets()

            # Sembolü farklı formatlarda kontrol et
            possible_symbols = [
                symbol,
                symbol.replace('/', ''),
                symbol.replace('/', '-')
            ]

            if any(sym in markets for sym in possible_symbols):
                active_exchanges.append(exchange_id)

        except Exception as e:
            print(f"{exchange_id} hatası: {e}")
            continue

    return active_exchanges

def update_platforms_for_all_papers():
    all_papers = CMCInfo.objects.all()

    for paper in all_papers:
        symbol = paper.symbol + "/USDT"
        platforms = find_active_exchanges_for_symbol(symbol)

        paper.platforms = json.dumps(platforms)  # JSON formatında saklıyoruz
        paper.save()

        print(f"{paper.name} ({symbol}) → {platforms}")

update_platforms_for_all_papers()