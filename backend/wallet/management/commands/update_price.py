from django.core.management.base import BaseCommand
from wallet.utils import update_paper_prices

class Command(BaseCommand):
    help = 'Update stock prices from API'

    def handle(self, *args, **kwargs):
        update_paper_prices()
        self.stdout.write(self.style.SUCCESS('Successfully updated stock prices'))
