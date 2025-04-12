import time
import threading
from django.db import models
from views import get_most_gainers_and_losers  

def fetch_top_markets_periodically():
    while True:
        get_most_gainers_and_losers()
        time.sleep(3600)

def start_fetch_thread():
    fetch_thread = threading.Thread(target=fetch_top_markets_periodically)
    fetch_thread.daemon = True
    fetch_thread.start()

from django.apps import AppConfig

class TradingAppConfig(AppConfig):
    name = 'trading'

    def ready(self):
        start_fetch_thread()  
