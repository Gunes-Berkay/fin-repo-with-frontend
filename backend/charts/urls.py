from django.urls import path
from .views import fetch_table_data, fetch_coins_names

urlpatterns = [
    path('charts/table/<str:table_name>on<str:INTERVAL>/', fetch_table_data, name='fetch_table_data'),
    path('charts/', fetch_coins_names, name='fetch_coins_names')

]
