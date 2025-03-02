"""
Models for the dashboard app.
"""

from accounts.models import UserPreference, Watchlist
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Symbol(models.Model):
    """Model representing a stock symbol."""
    ticker = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    sector = models.CharField(max_length=100)
    industry = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    market_cap = models.BigIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ticker} - {self.name}"

class CompanyRating(models.Model):
    """Model representing a company rating."""
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE, related_name='ratings')
    rating = models.FloatField()
    confidence = models.FloatField()
    weight = models.FloatField()
    news_relevance = models.FloatField(default=0)
    news_sentiment = models.FloatField(default=0)
    news_mentions = models.IntegerField(default=0)
    rating_date = models.DateTimeField(default=timezone.now)
    
    # Store rating components as JSON
    rating_components = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-rating_date', '-rating']
        
    def __str__(self):
        return f"{self.symbol.ticker} Rating: {self.rating:.1f}/100"

class MarketInsight(models.Model):
    """Model representing market insights."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    sectors = models.JSONField(default=dict)
    trending_topics = models.JSONField(default=list)
    top_companies = models.JSONField(default=list)
    news_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Market Insight: {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class NewsArticle(models.Model):
    """Model representing a news article."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    url = models.URLField()
    source = models.CharField(max_length=100)
    published_at = models.DateTimeField()
    sentiment = models.FloatField(default=0)  # -1 to 1 scale
    topics = models.JSONField(default=dict)
    related_symbols = models.ManyToManyField(Symbol, related_name='news')
    
    class Meta:
        ordering = ['-published_at']
        
    def __str__(self):
        return self.title

class DataCollectionTask(models.Model):
    """Model representing a data collection task."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    TYPE_CHOICES = [
        ('news', 'News Collection'),
        ('market', 'Market Data Collection'),
        ('process', 'Data Processing'),
    ]
    
    task_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    parameters = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        
    def __str__(self):
        return f"{self.task_type} Task - {self.status}"

class ModelTrainingTask(models.Model):
    """Model representing a model training task."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    parameters = models.JSONField(default=dict)
    metrics = models.JSONField(default=dict)
    epochs_completed = models.IntegerField(default=0)
    total_epochs = models.IntegerField(default=1000)
    model_path = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        
    def __str__(self):
        return f"Model Training Task - {self.status} ({self.epochs_completed}/{self.total_epochs})"