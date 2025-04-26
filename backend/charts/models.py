from django.db import models
import json


class FollowList(models.Model):
    list_name = models.CharField(max_length=30, primary_key=True)

    def __str__(self):
        return self.list_name
    
    class Meta:
        db_table = "follow_list_charts"
        app_label = 'charts'


class CMCInfo(models.Model):
    cmc_rank = models.IntegerField(default=0)
    id = models.IntegerField(primary_key=True)  # CoinMarketCap ID
    name = models.TextField(default="")
    symbol = models.TextField(default="")
    price = models.FloatField(default=0.0)
    market_cap = models.FloatField(default=0.0)
    market_cap_dominance = models.FloatField(default=0.0)
    volume_24h = models.FloatField(default=0.0)
    max_supply = models.FloatField(null=True, blank=True, default=0.0)
    circulating_supply = models.FloatField(default=0.0)
    total_supply = models.FloatField(default=0.0)
    infinite_supply = models.BooleanField(default=False)
    date_added = models.TextField(default="")
    tags = models.TextField(default="")
    percent_change_1h = models.FloatField(default=0.0)
    percent_change_24h = models.FloatField(default=0.0)
    percent_change_7d = models.FloatField(default=0.0)
    percent_change_30d = models.FloatField(default=0.0)
    percent_change_90d = models.FloatField(default=0.0)
    platforms = models.TextField(default="", blank=True)  

    
    class Meta:
        db_table = "CMC_INFO_charts"
        app_label = 'charts'

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class FollowingPaper(models.Model):
    list_name = models.ForeignKey(FollowList, on_delete=models.CASCADE)
    paper = models.ForeignKey(CMCInfo, on_delete=models.CASCADE)
    price = models.FloatField(default=0.0)
    percent_change_24h = models.FloatField(default=0.0)

    class Meta:
        db_table = "following_paper_charts"
        app_label = 'charts'


class Portfolio(models.Model):
    portfolio_id = models.AutoField(primary_key=True)
    portfolio_name = models.CharField(max_length=20)
    portfolio_tags = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.portfolio_name
    
    class Meta:
        db_table = "portfolio_charts"
        app_label = 'charts'


class PortfolioPaper(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    paper = models.ForeignKey(CMCInfo, on_delete=models.CASCADE)
    count_of_paper = models.FloatField()
    average_buy_price = models.FloatField()
    average_sell_price = models.FloatField()
    buy_count = models.FloatField()
    sell_count = models.FloatField()
    
    class Meta:
        db_table = "portfolio_paper_charts"
        app_label = 'charts'


class Transactions(models.Model):
    paper = models.ForeignKey(CMCInfo, on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    date_added = models.DateField()
    count_of_transaction = models.FloatField()
    transaction_type_buy = models.BooleanField()
    
    class Meta:
        db_table = "transactions_charts"
        app_label = 'charts'
