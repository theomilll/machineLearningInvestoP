# insights_api/services/insights_service.py
from datetime import datetime

from dashboard.models import CompanyRating, MarketInsight, NewsArticle, Symbol
from django.db.models import Avg, Count, Max


class InsightsService:
    def generate_market_insights(self):
        """Generate market insights from company ratings and news data"""
        
        # Collect sector performance
        sectors = {}
        for sector in Symbol.objects.values_list('sector', flat=True).distinct():
            if not sector:
                continue
                
            sector_symbols = Symbol.objects.filter(sector=sector)
            sector_ratings = CompanyRating.objects.filter(
                symbol__in=sector_symbols
            ).values('symbol__ticker').annotate(
                avg_rating=Avg('rating')
            ).order_by('-avg_rating')
            
            if not sector_ratings:
                continue
                
            # Calculate sector metrics
            sectors[sector] = {
                'average_rating': sector_ratings.aggregate(Avg('avg_rating'))['avg_rating__avg'] or 0,
                'company_count': sector_ratings.count(),
                'top_company': sector_ratings.first()['symbol__ticker'] if sector_ratings else None
            }
        
        # Get top companies across all sectors
        top_companies = []
        top_ratings = CompanyRating.objects.select_related('symbol').order_by('-rating')[:10]
        for rating in top_ratings:
            top_companies.append({
                'symbol': rating.symbol.ticker,
                'name': rating.symbol.name,
                'sector': rating.symbol.sector,
                'rating': rating.rating
            })
        
        # Extract trending topics from news
        recent_news = NewsArticle.objects.order_by('-published_at')[:100]
        topics_count = {}
        for article in recent_news:
            for topic, weight in article.topics.items():
                if topic in topics_count:
                    topics_count[topic] += weight
                else:
                    topics_count[topic] = weight
        
        trending_topics = [
            {'name': topic, 'weight': weight}
            for topic, weight in sorted(topics_count.items(), key=lambda x: x[1], reverse=True)
        ][:10]
        
        # Create market insight
        insight = MarketInsight.objects.create(
            title=f"Market Insight: {datetime.now().strftime('%B %Y')}",
            description="Generated market insights based on news sentiment and company ratings",
            sectors=sectors,
            trending_topics=trending_topics,
            top_companies=top_companies,
            news_count=recent_news.count()
        )
        
        return insight