"""
Serializers for the insights_api app.
"""

from dashboard.models import (CompanyRating, DataCollectionTask, MarketInsight,
                              ModelTrainingTask, NewsArticle, Symbol,
                              Watchlist)
from rest_framework import serializers


class SymbolSerializer(serializers.ModelSerializer):
    """Serializer for Symbol model."""
    
    class Meta:
        model = Symbol
        fields = '__all__'


class WatchlistSerializer(serializers.ModelSerializer):
    """Serializer for Watchlist model."""
    
    symbols = SymbolSerializer(many=True, read_only=True)
    
    class Meta:
        model = Watchlist
        fields = ['id', 'name', 'user', 'symbols', 'created_at', 'updated_at']


class CompanyRatingSerializer(serializers.ModelSerializer):
    """Serializer for CompanyRating model."""
    
    symbol = SymbolSerializer(read_only=True)
    
    class Meta:
        model = CompanyRating
        fields = '__all__'


class NewsArticleSerializer(serializers.ModelSerializer):
    """Serializer for NewsArticle model."""
    
    related_symbols = SymbolSerializer(many=True, read_only=True)
    
    class Meta:
        model = NewsArticle
        fields = '__all__'


class DataCollectionTaskSerializer(serializers.ModelSerializer):
    """Serializer for DataCollectionTask model."""
    
    class Meta:
        model = DataCollectionTask
        fields = '__all__'


class ModelTrainingTaskSerializer(serializers.ModelSerializer):
    """Serializer for ModelTrainingTask model."""
    
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = ModelTrainingTask
        fields = '__all__'
    
    def get_progress(self, obj):
        """Calculate training progress."""
        if obj.total_epochs > 0:
            return round((obj.epochs_completed / obj.total_epochs) * 100, 1)
        return 0


class MarketInsightSerializer(serializers.ModelSerializer):
    """Serializer for MarketInsight model."""
    
    top_companies_data = serializers.SerializerMethodField()
    sector_performance = serializers.SerializerMethodField()
    
    class Meta:
        model = MarketInsight
        fields = '__all__'
    
    def get_top_companies_data(self, obj):
        """Get detailed data for top companies."""
        top_companies = []
        
        for company_data in obj.top_companies:
            try:
                symbol = Symbol.objects.get(ticker=company_data.get('symbol'))
                company = {
                    'ticker': symbol.ticker,
                    'name': symbol.name,
                    'sector': symbol.sector,
                    'rating': company_data.get('rating', 0),
                }
                top_companies.append(company)
            except Symbol.DoesNotExist:
                # Include just the data we have
                top_companies.append(company_data)
        
        return top_companies
    
    def get_sector_performance(self, obj):
        """Get sector performance data."""
        sectors = []
        
        for sector, data in obj.sectors.items():
            sector_info = {
                'name': sector,
                'average_rating': data.get('average_rating', 0),
                'company_count': data.get('company_count', 0),
                'top_company': data.get('top_company')
            }
            sectors.append(sector_info)
        
        return sorted(sectors, key=lambda x: x.get('average_rating', 0), reverse=True)