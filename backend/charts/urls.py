from django.urls import path
from .views import fetch_table_data, fetch_coins_names, send_follow_list_on_start

urlpatterns = [
    path('charts/table/<str:table_name>on<str:INTERVAL>lmt<int:limit>/', fetch_table_data, name='fetch_table_data'),
    path('charts/', send_follow_list_on_start, name='send_follow_list_on_start')
]
