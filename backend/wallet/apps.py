from django.apps import AppConfig

class WalletConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wallet'

    def ready(self):
        import wallet.signals

    # def ready(self):
    #     from wallet.models import Paper, Portfolio

    #     papers = Paper.objects.all()
    #     portfolios = Portfolio.objects.all()
        


    #     if papers.exists():
    #         print(f"{papers.count()} adet Paper veritabanında yüklendi.")
    #     else:
    #         print("Hiç Paper kaydı bulunamadı.") 
