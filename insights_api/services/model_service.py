# insights_api/services/model_service.py
import random
from datetime import datetime

from dashboard.models import (CompanyRating, ModelTrainingTask, NewsArticle,
                              Symbol)
from django.db.models import Avg, Count, Max


class ModelService:
    def train_model(self, task_id, symbols=None, episodes=1000, use_cached=True):
        """Train model to predict company ratings"""
        task = ModelTrainingTask.objects.get(id=task_id)
        task.status = 'running'
        task.save()
        
        try:
            # Simulated training process
            for i in range(episodes):
                if i % 10 == 0:  # Update progress every 10 episodes
                    task.epochs_completed = i
                    task.metrics = {
                        'reward': random.uniform(0.5, 0.9) * i/episodes,
                        'return': random.uniform(5, 15),
                        'value_loss': max(0.01, 1.0 - i/episodes),
                        'policy_loss': max(0.005, 0.5 - i/episodes/2),
                        'entropy': max(0.001, 0.1 - i/episodes/10)
                    }
                    task.save()
            
            # Mark as completed
            task.epochs_completed = episodes
            task.status = 'completed'
            task.completed_at = datetime.now()
            task.model_path = f"model_{task.id}_{datetime.now().strftime('%Y%m%d%H%M')}.h5"
            task.save()
            
            return task
        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
            raise
    
    def evaluate_companies(self, model_path=None):
        """Evaluate companies and generate ratings"""
        symbols = Symbol.objects.all()
        
        for symbol in symbols:
            # Get related news
            news = NewsArticle.objects.filter(related_symbols=symbol)
            news_count = news.count()
            
            # Calculate news sentiment
            avg_sentiment = news.aggregate(Avg('sentiment'))['sentiment__avg'] or 0
            
            # Generate simulated rating components based on news and sector
            tech_boost = 1.2 if 'Tech' in symbol.sector else 1.0
            energy_boost = 1.15 if 'Energy' in symbol.sector else 1.0
            
            # Create rating components
            components = {
                'fundamentals': random.uniform(0.3, 0.9),
                'news_sentiment': max(0, (avg_sentiment + 1) / 2),  # Convert -1:1 to 0:1
                'sector_trend': random.uniform(0.4, 0.8) * tech_boost * energy_boost,
                'market_correlation': random.uniform(0.2, 0.7),
                'volatility': random.uniform(0.3, 0.6)
            }
            
            # Calculate overall rating
            rating_value = (
                components['fundamentals'] * 25 +
                components['news_sentiment'] * 20 +
                components['sector_trend'] * 25 +
                components['market_correlation'] * 15 +
                components['volatility'] * 15
            )
            
            # Adjust rating based on news volume
            news_factor = min(1.0, news_count / 10) if news_count > 0 else 0.5
            rating_value = rating_value * (0.8 + 0.2 * news_factor)
            
            # Create or update rating
            CompanyRating.objects.create(
                symbol=symbol,
                rating=rating_value,
                confidence=random.uniform(0.6, 0.95),
                weight=random.uniform(0.7, 1.0),
                news_relevance=news_factor,
                news_sentiment=avg_sentiment,
                news_mentions=news_count,
                rating_components=components
            )
        
        return {'companies_evaluated': symbols.count()}