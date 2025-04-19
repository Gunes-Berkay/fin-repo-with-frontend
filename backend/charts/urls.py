from django.urls import path
from .views import (
    fetch_table_data,
    fetch_coins_names,
    send_follow_list_on_start,
    create_follow_list,
    delete_follow_list,
    get_follow_lists,
    add_paper_to_follow_list,
    remove_paper_from_follow_list,
    return_follow_list,
    update_following_papers,
    get_paper_names
)

urlpatterns = [
    path('charts/table/<str:table_name>on<str:INTERVAL>lmt<int:limit>/', fetch_table_data, name='fetch_table_data'),
     path('charts/coin-names/', fetch_coins_names, name='fetch_coins_names'),
    path('charts/', send_follow_list_on_start, name='send_follow_list_on_start'),

    path('follow-lists/create/', create_follow_list, name='create_follow_list'),
    path('follow-lists/delete/', delete_follow_list, name='delete_follow_list'),
    path('follow-lists/all/', get_follow_lists, name='get_follow_lists'),

    path('follow-lists/add-paper/', add_paper_to_follow_list, name='add_paper_to_follow_list'),
    path('follow-lists/remove-paper/', remove_paper_from_follow_list, name='remove_paper_from_follow_list'),

    path('follow-lists/data/', return_follow_list, name='return_follow_list'),
    path('update-following-paper/', update_following_papers ,name='update_following_paper'),
    path('get-paper-names/', get_paper_names ,name='get_paper_names'),
    
]
