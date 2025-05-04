from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from charts.models import CMCInfo




class Portfolio(models.Model):
    portfolio_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    papers_list = models.ManyToManyField(CMCInfo, through='PortfolioPaper')

    class Meta:
        db_table = 'wallet_portfolio'

    def __str__(self):
        return self.name


class PortfolioPaper(models.Model):
    portfolio_paper_id = models.AutoField(primary_key=True)
    paper = models.ForeignKey(CMCInfo, on_delete=models.CASCADE, related_name='portfolio_papers')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='papers')
    total_quantity = models.IntegerField(default=0)  
    current_price = models.FloatField(default=100.0)  
    average_buy_price = models.FloatField(default=0.0)
    average_sell_price = models.FloatField(default=0.0)
    buy_count = models.IntegerField(default=0)
    sell_count = models.IntegerField(default=0)
    total_profit_loss = models.FloatField(default=0.0)
    realized_profit_loss = models.FloatField(default=0.0)
    unrealized_profit_loss = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.portfolio.name} - {self.paper.name} (Qty: {self.total_quantity})"

class Transactions(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    portfolio_paper = models.ForeignKey(PortfolioPaper, on_delete=models.CASCADE, related_name='transactions')
    entry_price = models.FloatField()
    quantity = models.IntegerField() 
    entry_date = models.DateTimeField(auto_now_add=True)
    buy = models.BooleanField()  

    def __str__(self):
        return f"{self.portfolio_paper.paper.name} - {self.quantity} @ {self.entry_price}"