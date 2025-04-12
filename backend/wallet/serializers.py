from rest_framework import serializers
from .models import Paper, Portfolio, Transactions, PortfolioPaper

# Paper Serializer
class PaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = ['id', 'name', 'symbol', 'max_supply', 'circulating_supply', 'total_supply', 'inifinite_supply', 'cmc_rank']

# Portfolio Serializer
class PortfolioSerializer(serializers.ModelSerializer):
    papers_list = PaperSerializer(many=True, read_only=True)  # ManyToMany ilişkisi için iç içe serializer

    class Meta:
        model = Portfolio
        fields = ['portfolio_id', 'name', 'papers_list']

# Transactions Serializer
class TransactionsSerializer(serializers.ModelSerializer):
    portfolio = PortfolioSerializer(read_only=True)  # ForeignKey ilişkisini doğru şekilde serileştirmek için
    paper = PaperSerializer(read_only=True)  # ForeignKey ilişkisini doğru şekilde serileştirmek için

    class Meta:
        model = Transactions
        fields = ['portfolio', 'paper', 'entry_price', 'quantity', 'entry_date', 'buy']

# PortfolioPaper Serializer
class PortfolioPaperSerializer(serializers.ModelSerializer):
    portfolio = PortfolioSerializer(read_only=True)
    paper = PaperSerializer(read_only=True)

    class Meta:
        model = PortfolioPaper
        fields = ['portfolio_paper_id', 'portfolio', 'paper', 'total_quantity', 'current_price']
