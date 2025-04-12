import requests
from .models import Paper, PortfolioPaper

def update_paper_prices():
    for paper in Paper.objects.all():
        response = requests.get(f"https://api.example.com/price/{paper.symbol}")  # Örnek API
        if response.status_code == 200:
            data = response.json()
            current_price = data.get("price")
            PortfolioPaper.objects.filter(paper=paper).update(current_price=current_price)
