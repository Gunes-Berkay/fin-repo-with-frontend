from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Paper(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10, unique=True) 
    max_supply = models.FloatField()
    circulating_supply = models.FloatField()
    total_supply = models.FloatField()
    inifinite_supply = models.BooleanField()
    cmc_rank = models.IntegerField()
    current_price = models.FloatField(default=0.0)


    class Meta:
        db_table = "CMC_INFO"  
        app_label = 'wallet'
        managed = False
    
    def __str__(self):
        return self.name

class Portfolio(models.Model):
    portfolio_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    papers_list = models.ManyToManyField(Paper, through='PortfolioPaper')

    class Meta:
        db_table = 'wallet_portfolio'

    def __str__(self):
        return self.name


class PortfolioPaper(models.Model):
    portfolio_paper_id = models.AutoField(primary_key=True)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='portfolio_papers')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='papers')
    total_quantity = models.IntegerField(default=0)  # Mevcut toplam adet
    current_price = models.FloatField(default=100.0)  # API'den alınacak
    average_buy_price = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.portfolio.name} - {self.paper.name} (Qty: {self.total_quantity})"

class Transactions(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    portfolio_paper = models.ForeignKey(PortfolioPaper, on_delete=models.CASCADE, related_name='transactions')
    entry_price = models.FloatField()
    quantity = models.IntegerField()  # Adet (pozitif: alım, negatif: satım)
    entry_date = models.DateTimeField(auto_now_add=True)
    buy = models.BooleanField()  # True: alım, False: satım

    def __str__(self):
        return f"{self.paper.name} - {self.quantity} @ {self.entry_price}"