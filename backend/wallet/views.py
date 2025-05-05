from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound
from django.db import transaction, connections
import json
import requests
from charts.models import FollowingPaper
from .models import Portfolio, PortfolioPaper, Transactions
from charts.models import CMCInfo

@csrf_exempt
@require_http_methods(["POST"])
def add_paper_to_portfolio(request):
    data = json.loads(request.body)
    portfolio_id = data.get('portfolio_id')
    paper_name = data.get('paper_name')

    try:
        portfolio = Portfolio.objects.get(portfolio_id=portfolio_id)
        paper = CMCInfo.objects.get(name=paper_name)
    except (Portfolio.DoesNotExist, CMCInfo.DoesNotExist):
        return JsonResponse({"error": "Portfolio or Paper not found."}, status=404)

    portfolio_paper = PortfolioPaper.objects.create(
        portfolio=portfolio,
        paper=paper
    )
    portfolio.papers_list.add(paper)

    return JsonResponse({
        "portfolio_paper_id": portfolio_paper.portfolio_paper_id,
        "portfolio_name": portfolio.name,
        "paper_name": paper.name
    }, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def create_portfolio(request):
    data = json.loads(request.body)
    portfolio_name = data.get('name')
    papers_data = data.get('papers', [])

    try:
        with transaction.atomic():
            portfolio = Portfolio.objects.create(name=portfolio_name)

            for paper_id in papers_data:
                paper = CMCInfo.objects.get(id=paper_id)
                portfolio.papers_list.add(paper)

            return JsonResponse({
                "portfolio_id": portfolio.portfolio_id,
                "name": portfolio.name,
                "papers": [paper.name for paper in portfolio.papers_list.all()]
            }, status=201)

    except CMCInfo.DoesNotExist:
        return JsonResponse({"error": f"Paper with ID {paper_id} not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def portfolio_list(request):
    portfolios = Portfolio.objects.all()
    data = []
    for portfolio in portfolios:
        data.append({
            "portfolio_id": portfolio.portfolio_id,
            "name": portfolio.name,
            "papers": [paper.name for paper in portfolio.papers_list.all()]
        })
    return JsonResponse(data, safe=False, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def paper_list(request):
    papers = CMCInfo.objects.all()
    data = []
    for paper in papers:
        data.append({
            "id": paper.id,
            "name": paper.name,
            "symbol": paper.symbol
        })
    return JsonResponse(data, safe=False, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def create_transaction(request):
    data = json.loads(request.body)

    paper_name = data.get('name')
    portfolio_name = data.get('portfolio')
    entry_price = data.get('entry_price')
    quantity = data.get('quantity')
    buy = data.get('buy')

    try:
        paper = CMCInfo.objects.get(name=paper_name)
    except CMCInfo.DoesNotExist:
        return JsonResponse({"error": "Paper exactly not found"}, status=404)

    try:
        portfolio = Portfolio.objects.get(name=portfolio_name)
    except Portfolio.DoesNotExist:
        return JsonResponse({"error": "Portfolio not found"}, status=404)

    portfolio_paper, created = PortfolioPaper.objects.get_or_create(
        portfolio=portfolio,
        paper=paper
    )

    transaction_obj = Transactions.objects.create(
        portfolio_paper=portfolio_paper,
        entry_price=entry_price,
        quantity=quantity,
        buy=buy
    )
    
    calculate_transaction_for_portfolio_paper(portfolio_paper.portfolio_paper_id)

    return JsonResponse({
        "transaction_id": transaction_obj.transaction_id,
        "paper_name": paper.name,
        "portfolio_name": portfolio.name,
        "entry_price": entry_price,
        "quantity": quantity,
        "buy": buy,
        "entry_date": transaction_obj.entry_date
    }, status=201)


@csrf_exempt
@require_http_methods(["GET"])
def transaction_list(request):
    paper_name = request.GET.get('paper_name')
    portfolio_name = request.GET.get('portfolio_name')

    paper = get_object_or_404(CMCInfo, name=paper_name)
    portfolio = get_object_or_404(Portfolio, name=portfolio_name)
    portfolio_paper = get_object_or_404(PortfolioPaper, portfolio=portfolio, paper=paper)

    transactions = Transactions.objects.filter(portfolio_paper=portfolio_paper).order_by('-entry_date')

    data = []
    for transaction_obj in transactions:
        data.append({
            "transaction_id": transaction_obj.transaction_id,
            "entry_price": transaction_obj.entry_price,
            "quantity": transaction_obj.quantity,
            "buy": transaction_obj.buy,
            "entry_date": transaction_obj.entry_date
        })

    return JsonResponse(data, safe=False, status=200)



@csrf_exempt
@require_http_methods(["PUT"])
def update_portfolio_paper(request, portfolio_paper_id):
    try:
        portfolio_paper = PortfolioPaper.objects.get(portfolio_paper_id=portfolio_paper_id)
    except PortfolioPaper.DoesNotExist:
        return JsonResponse({"error": "PortfolioPaper not found"}, status=404)

    data = json.loads(request.body)

    total_quantity = data.get('total_quantity')
    current_price = data.get('current_price')
    average_buy_price = data.get('average_buy_price')

    if total_quantity is not None:
        portfolio_paper.total_quantity = total_quantity
    if current_price is not None:
        portfolio_paper.current_price = current_price
    if average_buy_price is not None:
        portfolio_paper.average_buy_price = average_buy_price

    portfolio_paper.save()

    return JsonResponse({
        "portfolio_paper_id": portfolio_paper.portfolio_paper_id,
        "portfolio_name": portfolio_paper.portfolio.name,
        "paper_name": portfolio_paper.paper.name,
        "total_quantity": portfolio_paper.total_quantity,
        "current_price": portfolio_paper.current_price,
        "average_buy_price": portfolio_paper.average_buy_price
    }, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def update_paper_prices(request):
    response = requests.get('https://api.example.com/get_paper_prices')
    paper_prices = response.json()

    for paper in paper_prices:
        try:
            paper_obj = CMCInfo.objects.get(symbol=paper['symbol'])
            paper_obj.max_supply = paper.get('max_supply')
            paper_obj.circulating_supply = paper.get('circulating_supply')
            paper_obj.total_supply = paper.get('total_supply')
            paper_obj.inifinite_supply = paper.get('inifinite_supply')
            paper_obj.cmc_rank = paper.get('cmc_rank')
            paper_obj.save()
        except CMCInfo.DoesNotExist:
            continue

    return JsonResponse({"message": "Prices updated successfully"}, status=200)


@csrf_exempt
@require_http_methods(["GET"])
def portfolio_paper_list(request):
    
    portfolio_papers = PortfolioPaper.objects.all()

    data = []
    for portfolio_paper in portfolio_papers:
        paper = portfolio_paper.paper
        portfolio = portfolio_paper.portfolio
        data.append({
            "portfolio_id": portfolio.portfolio_id,
            "id": paper.id,
            "name": paper.name,
            "symbol": paper.symbol,
            "total_quantity": portfolio_paper.total_quantity,
            "current_price": portfolio_paper.current_price,
            "average_buy_price": portfolio_paper.average_buy_price,
            "paper_id": paper.id,
        })

    return JsonResponse(data, safe=False, status=200)



@csrf_exempt
@require_http_methods(["GET"])
def get_papers(request):
    papers = CMCInfo.objects.all()
    data = []
    for paper in papers:
        data.append({
            "id": paper.id,
            "symbol": paper.symbol,
            "name": paper.name
        })
    return JsonResponse(data, safe=False, status=200)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_portfolio(request, portfolio_id):
    if request.method == 'DELETE':
        try:
            portfolio = Portfolio.objects.get(portfolio_id=portfolio_id)
            portfolio.delete()
            return JsonResponse({'message': 'Portfolio deleted successfully.'})
        except Portfolio.DoesNotExist:
            return HttpResponseNotFound('Portfolio not found.')
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_portfolio_paper(request, portfolio_id, paper_id):
    if request.method == 'DELETE':
        try:
            portfolioPaper = PortfolioPaper.objects.get(paper=paper_id, portfolio=portfolio_id)
            portfolioPaper.delete()
            return JsonResponse({'message': 'PortfolioPaper deleted successfully.'})
        except Portfolio.DoesNotExist:
            return HttpResponseNotFound('PortfolioPaper not found.')
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_transaction(request, transaction_id):
    if request.method == 'DELETE':
        try:
            transaction = Transactions.objects.get(transaction_id=transaction_id)
            transaction.delete()
            return JsonResponse({'message': 'transaction deleted successfully.'})
        except Portfolio.DoesNotExist:
            return HttpResponseNotFound('transaction not found.')
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

def calculate_transaction_for_portfolio_paper(portfolio_paper_id):
    try:
        portfolio_paper = PortfolioPaper.objects.get(portfolio_paper_id=portfolio_paper_id)
    except PortfolioPaper.DoesNotExist:
        return JsonResponse({"error": "PortfolioPaper not found"}, status=404)

    transactions = Transactions.objects.filter(portfolio_paper=portfolio_paper)
    total_buy = 0
    avg_buy_price = 0
    total_sell = 0
    avg_sell_price = 0
    for transaction in transactions.filter(buy=True):
        total_buy += transaction.quantity
        avg_buy_price += transaction.entry_price * transaction.quantity
        avg_buy_price /= total_buy if total_buy != 0 else 1
    for transaction in transactions.filter(buy=False):
        total_sell += transaction.quantity
        avg_sell_price += transaction.entry_price * transaction.quantity   
        avg_sell_price /= total_sell if total_sell != 0 else 1
        
    portfolio_paper.average_buy_price = avg_buy_price
    portfolio_paper.average_sell_price = avg_sell_price
    portfolio_paper.buy_count = total_buy
    portfolio_paper.sell_count = total_sell
    
    realized_pl = (avg_sell_price - avg_buy_price) * total_sell

    unrealized_pl = (portfolio_paper.current_price - avg_buy_price) * (total_buy - total_sell)

    total_profit_loss = realized_pl + unrealized_pl
    portfolio_paper.total_profit_loss = total_profit_loss
    
        
    portfolio_paper.total_quantity = total_buy - total_sell
    portfolio_paper.save()
 
def update_portfolio_paper_price(request):
    try:
        portfolio_papers = PortfolioPaper.objects.all()
    except PortfolioPaper.DoesNotExist:
        return JsonResponse({"error": "PortfolioPapers not found"}, status=404)
    
    for portfolio_paper in portfolio_papers:
        paper = portfolio_paper.paper
        followingPaper = FollowingPaper.objects.filter(paper=paper).first()
        if followingPaper:
            portfolio_paper.current_price = followingPaper.price
        portfolio_paper.save()
        
    return JsonResponse({"message": "PortfolioPaper prices updated successfully"}, status=200)