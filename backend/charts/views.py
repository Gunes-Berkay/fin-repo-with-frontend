
from django.http import JsonResponse
from django.db import connections
from .models import Coin, Watchlist, WatchlistCoin
from django.http import JsonResponse

import sqlite3
import requests
import os
import trading
import json
import ccxt
import pandas as pd

INTERVALS = ['15m', '1h', '4h', '1d']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "veri.json") 


def fetch_table_data(request, table_name, INTERVAL):
     data = get_table_data(table_name, INTERVAL, limit=500)
     return JsonResponse({'table_data': data}, json_dumps_params={'ensure_ascii': False})

def get_table_data(table_name, INTERVAL, limit=100):

    if not table_name.isalnum() or not INTERVAL.isalnum():
        return []

    try:
        with connections['papers_db'].cursor() as cursor:
            query = f"SELECT * FROM `{table_name}on{INTERVAL}` LIMIT %s"
            cursor.execute(query, [limit])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        # JSON uyumlu hale getirme
        result = [
            {col: (str(value) if isinstance(value, (bytes, memoryview)) else value) for col, value in zip(columns, row)}
            for row in rows
        ]
        return result

    except Exception as e:
        print(f"Error querying table {table_name}{INTERVAL}: {e}")
        return []

def fetch_coins_names(request):
    with open(db_path, 'r', encoding="utf-8") as json_file:
        data = json.load(json_file)

    data = data['data']
    
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})


def get_analysis(request, symbol):

    for interval in INTERVALS:
        try:
            with connections['papers_db'].cursor() as cursor:
                query = f"SELECT * FROM `{symbol}on{interval}` LIMIT 1"
                cursor.execute(query)
                row = cursor.fetchone()
                column_dict = {desc[0]: index for index, desc in enumerate(cursor.description)}
                rsi = row[column_dict.get('rsi_14')]
                volume = row[column_dict.get('volume')]
                bull_total = row[column_dict.get('bull_total')]

                

            

        except Exception as e:
            print(f"Error querying table {symbol}{interval}: {e}")
            return []
    
def create_watchlist(request):
    """Yeni bir watchlist oluşturur"""
    if request.method == "POST":
        name = request.POST.get("name")  # Watchlist ismi
        if name:
            watchlist = Watchlist.objects.create(name=name)
            return JsonResponse({'message': 'Watchlist oluşturuldu!'}, status=201)
        else:
            return JsonResponse({'message': 'Watchlist ismi boş olamaz!'}, status=400)
    return JsonResponse({'message': 'POST methodu bekleniyor.'}, status=400)


def delete_watchlist(request):
    watchlist_name = request.POST.get('watchlist_name')
    try:
        watchlist = Watchlist.objects.get(name=watchlist_name)
        watchlist.delete()
        return JsonResponse({'message': 'Watchlist başarıyla silindi!'}, status=200)
    except Watchlist.DoesNotExist:
        return JsonResponse({'message': 'Watchlist bulunamadı!'}, status=404)

def add_coin_to_watchlist(request):
    if request.method == 'POST':
        coin_name = request.POST.get('coin_name')
        watchlist_name = request.POST.get('watchlist_name')
        
        try:
            watchlist = Watchlist.objects.get(name=watchlist_name)  # Watchlist'i buluyoruz
            coin = Coin.objects.get(name=coin_name)  # Coin'i buluyoruz

            # Aynı coin'in tekrar eklenmesini engelliyoruz
            if not WatchlistCoin.objects.filter(watchlist=watchlist, coin=coin).exists():
                WatchlistCoin.objects.create(watchlist=watchlist, coin=coin)
                return JsonResponse({'message': 'Coin watchlist\'e eklendi!'}, status=201)
            else:
                return JsonResponse({'message': 'Coin zaten bu watchlist\'te mevcut!'}, status=400)

        except Watchlist.DoesNotExist:
            return JsonResponse({'message': 'Watchlist bulunamadı!'}, status=404)
        except Coin.DoesNotExist:
            return JsonResponse({'message': 'Coin bulunamadı!'}, status=404)

    return JsonResponse({'message': 'POST methodu bekleniyor.'}, status=400)

def remove_coin_from_watchlist(request):
    """Bir watchlist'ten coin çıkarır"""
    if request.method == 'POST':
        coin_id = request.POST.get('coin_id')  
        watchlist_name = request.POST.get('watchlist_name')
        

        try:
            watchlist = Watchlist.objects.get(name=watchlist_name)  
            coin = Coin.objects.get(id=coin_id)  

            watchlist_coin = WatchlistCoin.objects.filter(watchlist=watchlist, coin=coin)
            if watchlist_coin.exists():
                watchlist_coin.delete()
                return JsonResponse({'message': 'Coin watchlist\'ten çıkarıldı!'}, status=200)
            else:
                return JsonResponse({'message': 'Coin bu watchlist\'te bulunmuyor!'}, status=400)

        except Watchlist.DoesNotExist:
            return JsonResponse({'message': 'Watchlist bulunamadı!'}, status=404)
        except Coin.DoesNotExist:
            return JsonResponse({'message': 'Coin bulunamadı!'}, status=404)

    return JsonResponse({'message': 'POST methodu bekleniyor.'}, status=400) 

def get_most_gainers_and_losers(request):
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
            reverse=True  # Artanları almak için sıralama tersine çevrildi
        )
        most_losers = sorted(
            (item for item in swap_tickers.items() if item[1].get('percentage') is not None),
            key=lambda x: x[1].get('percentage', 0),
            reverse=False  # Azalanları almak için sıralama doğru yönde
        )
        
        top_gainers = [{"symbol": most_gainers[i][0], "percentage": most_gainers[i][1].get('percentage', 0)} for i in range(0, 5)]
        top_losers = [{"symbol": most_losers[i][0], "percentage": most_losers[i][1].get('percentage', 0)} for i in range(0, 5)]

        # JSON formatında döndür
        response = {
            "top_gainers": top_gainers,
            "top_losers": top_losers
        }

        return json.dumps(response)
    else:
        return json.dumps({"error": "Hiçbir swap tick verisi alınamadı."})




    