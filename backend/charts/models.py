from django.db import models
import json

class Coin(models.Model):
    cmc_rank = models.IntegerField(primary_key=True)
    coin_id = models.IntegerField(db_column="id")  
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=50)
    price = models.FloatField()
    market_cap = models.FloatField()
    market_cap_dominance = models.FloatField()
    volume_24h = models.FloatField()
    max_supply = models.FloatField(null=True, blank=True)
    circulating_supply = models.FloatField()
    total_supply = models.FloatField()
    infinite_supply = models.BooleanField()
    date_added = models.DateTimeField()
    tags = models.TextField()  # JSON olarak saklanan alan
    percent_change_1h = models.FloatField()
    percent_change_24h = models.FloatField()
    percent_change_7d = models.FloatField()
    percent_change_30d = models.FloatField()
    percent_change_90d = models.FloatField()

    class Meta:
        db_table = "CMC_INFO"  
        managed = False  

    def get_tags(self):
        """ JSON olarak saklanan 'tags' alanını listeye çevirir """
        return json.loads(self.tags) if self.tags else []

    def __str__(self):
        return f"{self.name} ({self.symbol})"
    
class Watchlist(models.Model):
    name = models.CharField(max_length=20)
    
class WatchlistCoin(models.Model):
    watchlist = models.ForeignKey(Watchlist, related_name='coins', on_delete=models.CASCADE)  # Hangi watchlist'e ait
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE)
    
