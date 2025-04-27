from django.urls import path
from . import views

urlpatterns = [
    path('wallet/add-paper/', views.add_paper_to_portfolio, name='add_paper_to_portfolio'),
    path('wallet/create-portfolio/', views.create_portfolio, name='create_portfolio'),
    path('wallet/portfolios/', views.portfolio_list, name='portfolio_list'),
    path('wallet/papers/', views.paper_list, name='paper_list'),
    path('wallet/create-transaction/', views.create_transaction, name='create_transaction'),
    path('wallet/transactions/', views.transaction_list, name='transaction_list'),
    path('wallet/update-portfolio-paper/<int:portfolio_paper_id>/', views.update_portfolio_paper, name='update_portfolio_paper'),
    path('wallet/update-paper-prices/', views.update_paper_prices, name='update_paper_prices'), #tv kodu yazılacak
    path('wallet/portfolio-papers/', views.portfolio_paper_list, name='portfolio_paper_list'),
    path('wallet/get-papers/', views.get_papers, name='get_papers'),
    path('wallet/delete-portfolio/<int:portfolio_id>/', views.delete_portfolio, name='delete-portfolio'),
    path('wallet/delete-portfolio-paper/<int:portfolio_paper_id>/', views.delete_portfolio_paper, name='delete-portfolio-paper'),
    path('wallet/delete-transaction/<int:transaction_id>/', views.delete_transaction, name='delete-transaction'),
    

]
