# dashboard/management/commands/generate_sample_data.py
import random
from datetime import datetime, timedelta

from accounts.models import UserPreference, Watchlist
from dashboard.models import CompanyRating, MarketInsight, NewsArticle, Symbol
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Generates sample data for the application'

    def handle(self, *args, **options):
        self.stdout.write('Generating sample data...')
        
        # Create symbols with realistic data
        symbols_data = [
            {'ticker': 'NVDA', 'name': 'NVIDIA Corporation', 'sector': 'Technology', 'industry': 'Semiconductors'},
            {'ticker': 'AMD', 'name': 'Advanced Micro Devices, Inc.', 'sector': 'Technology', 'industry': 'Semiconductors'},
            {'ticker': 'INTC', 'name': 'Intel Corporation', 'sector': 'Technology', 'industry': 'Semiconductors'},
            {'ticker': 'MSFT', 'name': 'Microsoft Corporation', 'sector': 'Technology', 'industry': 'Software'},
            {'ticker': 'AAPL', 'name': 'Apple Inc.', 'sector': 'Technology', 'industry': 'Consumer Electronics'},
            {'ticker': 'GOOGL', 'name': 'Alphabet Inc.', 'sector': 'Technology', 'industry': 'Internet Content & Information'},
            {'ticker': 'AMZN', 'name': 'Amazon.com, Inc.', 'sector': 'Consumer Cyclical', 'industry': 'Internet Retail'},
            {'ticker': 'META', 'name': 'Meta Platforms, Inc.', 'sector': 'Technology', 'industry': 'Internet Content & Information'},
            {'ticker': 'TSLA', 'name': 'Tesla, Inc.', 'sector': 'Consumer Cyclical', 'industry': 'Auto Manufacturers'},
            {'ticker': 'XOM', 'name': 'Exxon Mobil Corporation', 'sector': 'Energy', 'industry': 'Oil & Gas'},
            {'ticker': 'CVX', 'name': 'Chevron Corporation', 'sector': 'Energy', 'industry': 'Oil & Gas'},
            {'ticker': 'JPM', 'name': 'JPMorgan Chase & Co.', 'sector': 'Financial Services', 'industry': 'Banks'},
            {'ticker': 'BAC', 'name': 'Bank of America Corporation', 'sector': 'Financial Services', 'industry': 'Banks'},
            {'ticker': 'PFE', 'name': 'Pfizer Inc.', 'sector': 'Healthcare', 'industry': 'Drug Manufacturers'},
            {'ticker': 'JNJ', 'name': 'Johnson & Johnson', 'sector': 'Healthcare', 'industry': 'Drug Manufacturers'},
        ]
        
        for sym_data in symbols_data:
            Symbol.objects.get_or_create(
                ticker=sym_data['ticker'],
                defaults={
                    'name': sym_data['name'],
                    'sector': sym_data['sector'],
                    'industry': sym_data['industry'],
                    'market_cap': random.randint(50000000000, 3000000000000)
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(symbols_data)} symbols'))
        
        # Create sample news
        topics = ['AI', 'Chip Shortage', 'Earnings', 'Tech Layoffs', 'Renewable Energy', 
                 'Interest Rates', 'Inflation', 'Supply Chain', 'Consumer Spending', 'Market Volatility']
        
        sources = ['Bloomberg', 'CNBC', 'Reuters', 'Yahoo Finance', 'Wall Street Journal']
        
        news_items = [
            {
                'title': 'NVIDIA Announces New AI Chip',
                'description': 'NVIDIA unveiled its next-generation AI chip, promising significant performance improvements.',
                'tickers': ['NVDA', 'AMD', 'INTC'],
                'sentiment': 0.8,
                'source': 'Bloomberg'
            },
            {
                'title': 'Tech Layoffs Continue as Microsoft Reduces Workforce',
                'description': 'Microsoft announced plans to lay off 5% of its global workforce amid economic uncertainty.',
                'tickers': ['MSFT', 'GOOGL', 'META'],
                'sentiment': -0.6,
                'source': 'CNBC'
            },
            {
                'title': 'Oil Prices Surge Amid Supply Concerns',
                'description': 'Crude oil prices rose sharply today due to concerns about global supply constraints.',
                'tickers': ['XOM', 'CVX'],
                'sentiment': 0.5,
                'source': 'Reuters'
            },
        ]
        
        # Generate more random news
        for i in range(30):
            random_title = f"{random.choice(['Rising', 'Falling', 'Stable', 'Volatile'])} {random.choice(['Prices', 'Demand', 'Supply', 'Growth'])} in {random.choice(['Tech', 'Energy', 'Finance', 'Healthcare'])} Sector"
            random_tickers = random.sample([s['ticker'] for s in symbols_data], k=random.randint(1, 3))
            random_sentiment = random.uniform(-0.9, 0.9)
            
            news_items.append({
                'title': random_title,
                'description': f"Market analysis of recent trends affecting {', '.join(random_tickers)}.",
                'tickers': random_tickers,
                'sentiment': random_sentiment,
                'source': random.choice(sources)
            })
        
        for item in news_items:
            article = NewsArticle.objects.create(
                title=item['title'],
                description=item['description'],
                source=item['source'],
                url=f"https://example.com/news/{item['title'].lower().replace(' ', '-')}",
                published_at=timezone.now() - timedelta(days=random.randint(1, 30), hours=random.randint(1, 23)),
                sentiment=item['sentiment'],
                topics={
                    random.choice(topics): random.uniform(0.5, 0.9),
                    random.choice(topics): random.uniform(0.3, 0.7)
                }
            )
            
            # Add related symbols
            for ticker in item['tickers']:
                try:
                    symbol = Symbol.objects.get(ticker=ticker)
                    article.related_symbols.add(symbol)
                except Symbol.DoesNotExist:
                    pass
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(news_items)} news articles'))
        
        # Generate company ratings
        model_service = ModelService()
        result = model_service.evaluate_companies()
        
        self.stdout.write(self.style.SUCCESS(f"Generated ratings for {result['companies_evaluated']} companies"))
        
        # Generate market insight
        insights_service = InsightsService()
        insight = insights_service.generate_market_insights()
        
        self.stdout.write(self.style.SUCCESS(f'Created market insight: {insight.title}'))
        
        self.stdout.write(self.style.SUCCESS('Sample data generation complete!'))