"""
API views for the insights_api app.
"""

from dashboard.models import (CompanyRating, DataCollectionTask, MarketInsight,
                              ModelTrainingTask, NewsArticle, Symbol)
from dashboard.tasks import (collect_market_data_task, collect_news_data_task,
                             evaluate_companies_task, process_data_task,
                             train_model_task)
from django.db.models import Avg, Count, Max, Min
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .serializers import (CompanyRatingSerializer,
                          DataCollectionTaskSerializer,
                          MarketInsightSerializer, ModelTrainingTaskSerializer,
                          NewsArticleSerializer, SymbolSerializer)


class SymbolViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for symbols."""
    queryset = Symbol.objects.all()
    serializer_class = SymbolSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['sector', 'industry', 'country']
    search_fields = ['ticker', 'name']
    ordering_fields = ['ticker', 'name', 'sector', 'market_cap']
    ordering = ['ticker']


class CompanyRatingViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for company ratings."""
    queryset = CompanyRating.objects.all().select_related('symbol')
    serializer_class = CompanyRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['symbol__ticker', 'symbol__sector']
    search_fields = ['symbol__ticker', 'symbol__name']
    ordering_fields = ['rating', 'rating_date', 'news_relevance']
    ordering = ['-rating_date', '-rating']


class MarketInsightViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for market insights."""
    queryset = MarketInsight.objects.all()
    serializer_class = MarketInsightSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for news articles."""
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['source', 'related_symbols__ticker']
    search_fields = ['title', 'description']
    ordering_fields = ['published_at', 'sentiment']
    ordering = ['-published_at']


class DataCollectionTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for data collection tasks."""
    queryset = DataCollectionTask.objects.all()
    serializer_class = DataCollectionTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['task_type', 'status']
    ordering_fields = ['started_at', 'completed_at']
    ordering = ['-started_at']


class ModelTrainingTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for model training tasks."""
    queryset = ModelTrainingTask.objects.all()
    serializer_class = ModelTrainingTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']
    ordering_fields = ['started_at', 'completed_at']
    ordering = ['-started_at']


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_data_collection(request):
    """API endpoint to start a data collection task."""
    task_type = request.data.get('task_type')
    symbols = request.data.get('symbols')
    use_cached = request.data.get('use_cached', True)
    
    if task_type not in ['news', 'market', 'process']:
        return Response(
            {'error': 'Invalid task type. Must be one of: news, market, process'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create task
    task = DataCollectionTask.objects.create(
        task_type=task_type,
        status='pending',
        parameters={
            'symbols': symbols,
            'use_cached': use_cached
        }
    )
    
    # Start the celery task
    if task_type == 'news':
        celery_task = collect_news_data_task.delay(task.id)
    elif task_type == 'market':
        celery_task = collect_market_data_task.delay(task.id)
    elif task_type == 'process':
        celery_task = process_data_task.delay(task.id)
    
    # Update task with celery task ID
    task.celery_task_id = celery_task.id
    task.save()
    
    return Response(
        {'task_id': task.id, 'status': 'pending'},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_model_training(request):
    """API endpoint to start a model training task."""
    symbols = request.data.get('symbols')
    episodes = request.data.get('episodes', 1000)
    use_cached = request.data.get('use_cached', True)
    
    # Create task
    task = ModelTrainingTask.objects.create(
        status='pending',
        parameters={
            'symbols': symbols,
            'episodes': episodes,
            'use_cached': use_cached
        },
        total_epochs=episodes
    )
    
    # Start the celery task
    celery_task = train_model_task.delay(task.id)
    
    # Update task with celery task ID
    task.celery_task_id = celery_task.id
    task.save()
    
    return Response(
        {'task_id': task.id, 'status': 'pending'},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def evaluate_companies(request):
    """API endpoint to evaluate companies."""
    model_id = request.data.get('model_id')
    
    if model_id:
        # Get model path from training task
        model_task = get_object_or_404(ModelTrainingTask, id=model_id)
        model_path = model_task.model_path
    else:
        model_path = None
    
    # Start the evaluation task
    result = evaluate_companies_task.delay(model_path)
    
    return Response(
        {'task_id': result.id, 'status': 'pending'},
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """API endpoint to get dashboard statistics."""
    # Get company stats
    total_companies = Symbol.objects.count()
    rated_companies = CompanyRating.objects.values('symbol').distinct().count()
    avg_rating = CompanyRating.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    # Get company counts by sector
    sector_counts = list(Symbol.objects.values('sector').annotate(
        count=Count('id'),
        avg_rating=Avg('ratings__rating')
    ).order_by('-count'))
    
    # Get news stats
    total_news = NewsArticle.objects.count()
    news_sources = list(NewsArticle.objects.values('source').annotate(count=Count('id')).order_by('-count')[:5])
    
    # Get top companies
    top_companies = list(CompanyRating.objects.select_related('symbol').order_by('-rating')[:10].values(
        'symbol__ticker', 'symbol__name', 'symbol__sector', 'rating', 'news_relevance'
    ))
    
    # Get latest insights
    latest_insight = MarketInsight.objects.first()
    latest_insight_id = latest_insight.id if latest_insight else None
    
    # Get task stats
    pending_tasks = DataCollectionTask.objects.filter(status='pending').count() + ModelTrainingTask.objects.filter(status='pending').count()
    running_tasks = DataCollectionTask.objects.filter(status='running').count() + ModelTrainingTask.objects.filter(status='running').count()
    
    stats = {
        'company_stats': {
            'total_companies': total_companies,
            'rated_companies': rated_companies,
            'avg_rating': round(avg_rating, 2)
        },
        'sector_stats': sector_counts,
        'news_stats': {
            'total_news': total_news,
            'sources': news_sources
        },
        'top_companies': top_companies,
        'latest_insight_id': latest_insight_id,
        'task_stats': {
            'pending_tasks': pending_tasks,
            'running_tasks': running_tasks
        }
    }
    
    return Response(stats)