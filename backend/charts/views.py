
from django.http import JsonResponse
from django.db import connections
from django.http import JsonResponse

import sqlite3
import requests
import os
import json
import ccxt
import pandas as pd
from .models import FollowList, FollowingPaper
from django.views.decorators.csrf import csrf_exempt
from .models import CMCInfo, FollowingPaper

INTERVALS = ['15m', '1h', '4h', '1d']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "veri.json") 
project_root = os.path.dirname(os.path.dirname(BASE_DIR))
db_path_user_db = os.path.join(project_root, 'databases', 'userdb.sqlite3')

def fetch_table_data(request, table_name, INTERVAL,limit):
     data = get_table_data(table_name, INTERVAL, limit)
     return JsonResponse({'table_data': data}, json_dumps_params={'ensure_ascii': False})

def get_table_data(table_name, INTERVAL, limit=100):

    if not table_name.isalnum() or not INTERVAL.isalnum():
        return []

    try:
        with connections['papers_db'].cursor() as cursor:
            query = f"SELECT * FROM `{table_name}on{INTERVAL}` ORDER BY datetime DESC LIMIT %s"
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

@csrf_exempt
def create_follow_list(request):
    follow_list_name = request.POST.get('follow_list_name')
    if not follow_list_name:
        return JsonResponse({'error': 'Follow list name is required'}, status=400)
    
    FollowList.objects.get_or_create(list_name=follow_list_name)
    return JsonResponse({'message': 'Follow list created successfully'}, status=201)

@csrf_exempt
def delete_follow_list(request):
    follow_list_name = request.POST.get('follow_list_name')
    if not follow_list_name:
        return JsonResponse({'error': 'Follow list name is required'}, status=400)
    
    FollowList.objects.filter(list_name=follow_list_name).delete()
    return JsonResponse({'message': 'Follow list deleted successfully'}, status=200)

def get_follow_lists(request):
    lists = FollowList.objects.all().values('list_name')
    return JsonResponse(list(lists), safe=False, json_dumps_params={'ensure_ascii': False})

@csrf_exempt
def add_paper_to_follow_list(request):
    paper_name = request.POST.get('paper_name')
    follow_list_name = request.POST.get('follow_list_name')

    paper = CMCInfo.objects.filter(name=paper_name).first()
    if not paper or not follow_list_name:
        return JsonResponse({'error': 'paper and follow list name are required'}, status=400)
    
    follow_list, _ = FollowList.objects.get_or_create(list_name=follow_list_name)
    FollowingPaper.objects.get_or_create(list_name=follow_list, paper=paper)

    return JsonResponse({'message': 'Coin added to follow list successfully'}, status=201)

@csrf_exempt
def remove_paper_from_follow_list(request):
    paper_id = request.POST.get('paper_id')
    follow_list_name = request.POST.get('follow_list_name')
    if not paper_id or not follow_list_name:
        return JsonResponse({'error': 'paper_id and follow list name are required'}, status=400)
    
    FollowingPaper.objects.filter(list_name__list_name=follow_list_name, paper_id=paper_id).delete()
    return JsonResponse({'message': 'Coin removed from follow list successfully'}, status=200)

def send_follow_list_on_start(request):
    if not FollowList.objects.exists():
        default_list = FollowList.objects.create(list_name='Default')
        from .models import PortfolioPaper  # Eğer varsa

        for paper in PortfolioPaper.objects.all():
            FollowingPaper.objects.create(list_name=default_list, paper_id=paper.paper_id)

    return return_follow_list(request)

def return_follow_list(request):
    data = {}
    papers = FollowingPaper.objects.select_related('list_name', 'paper').all()
    
    for item in papers:
        list_name = item.list_name.list_name
        coin_data = {
            'symbol': item.paper.symbol,
            'price': item.price,
            'change_24h': item.percent_change_24h
        }
        data.setdefault(list_name, []).append(coin_data)
    
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})
        
def get_paper_names(request):
    data = []
    papers = CMCInfo.objects.all()
    
    for paper in papers:
        data.append({    
            'name': paper.name,
            'symbol': paper.symbol
        })
    
    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})
    


def get_24h_change(symbol, exchange='BINANCE'):
    from tvDatafeed import TvDatafeed, Interval
    tv = TvDatafeed()
    data = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=2)

    previous_close = data['close'].iloc[0]
    current_close = data['close'].iloc[1]

    change_24h = ((current_close - previous_close) / previous_close) * 100

    return current_close, change_24h

@csrf_exempt
def update_following_papers(request):
    import logging
    
    papers = FollowingPaper.objects.select_related('paper')
    
    for fp in papers:
        symbol = fp.paper.symbol.upper() + 'USDT'
        try:
            current_price, change_24h = get_24h_change(symbol)
            fp.price = current_price
            fp.percent_change_24h = change_24h
            fp.save()
            print(f"{symbol} güncellendi → Price: {current_price}, 24h Change: {change_24h:.2f}%")
        except Exception as e:
            logging.warning(f"{symbol} güncellenemedi: {e}")
    
    if request.method == 'POST':
        # Buraya işlemlerini yazabilirsin (örneğin veritabanı güncellemesi)
        return JsonResponse({'message': 'Updated successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
