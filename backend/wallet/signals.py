from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transactions, PortfolioPaper

@receiver(post_save, sender=Transactions)
@receiver(post_delete, sender=Transactions)

def update_average_buy_price(sender, instance, **kwargs):
    portfolio_paper = instance.portfolio_paper

    transactions = Transactions.objects.filter(portfolio_paper=portfolio_paper)

    if transactions.exists():
        total_cost = sum(t.entry_price * t.quantity for t in transactions)
        total_quantity = sum(t.quantity for t in transactions)

        if total_quantity > 0:
            portfolio_paper.average_buy_price = total_cost / total_quantity
        else:
            portfolio_paper.average_buy_price = 0.0  # Eğer hiç işlem yoksa fiyat sıfırlanır
    else:
        portfolio_paper.average_buy_price = 0.0

    portfolio_paper.save()
