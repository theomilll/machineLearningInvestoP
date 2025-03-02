# dashboard/tasks.py
from celery import shared_task
from django.utils import timezone
from insights_api.services.data_service import DataCollectionService
from insights_api.services.insights_service import InsightsService
from insights_api.services.model_service import ModelService

from .models import DataCollectionTask, ModelTrainingTask


@shared_task
def collect_news_data_task(task_id):
    """Task to collect news data."""
    task = DataCollectionTask.objects.get(id=task_id)
    service = DataCollectionService()
    
    try:
        result = service.collect_news_data(
            task_id=task_id,
            symbols=task.parameters.get('symbols'),
            use_cached=task.parameters.get('use_cached', True)
        )
        return {"status": "completed", "result": result}
    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.save()
        return {"status": "failed", "error": str(e)}

@shared_task
def collect_market_data_task(task_id):
    """Task to collect market data."""
    task = DataCollectionTask.objects.get(id=task_id)
    service = DataCollectionService()
    
    try:
        result = service.collect_market_data(
            task_id=task_id,
            symbols=task.parameters.get('symbols'),
            use_cached=task.parameters.get('use_cached', True)
        )
        return {"status": "completed", "result": result}
    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.save()
        return {"status": "failed", "error": str(e)}

@shared_task
def process_data_task(task_id):
    """Task to process collected data and generate insights."""
    task = DataCollectionTask.objects.get(id=task_id)
    task.status = 'running'
    task.save()
    
    service = InsightsService()
    
    try:
        # Generate market insight from processed data
        insight = service.generate_market_insights()
        
        # Update task
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.result = {
            "insight_id": insight.id,
            "title": insight.title,
            "processed_symbols": len(insight.top_companies)
        }
        task.save()
        
        return {"status": "completed", "insight_id": insight.id}
    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.save()
        return {"status": "failed", "error": str(e)}

@shared_task
def train_model_task(task_id):
    """Task to train the investment model."""
    task = ModelTrainingTask.objects.get(id=task_id)
    service = ModelService()
    
    try:
        service.train_model(
            task_id=task_id,
            symbols=task.parameters.get('symbols'),
            episodes=task.parameters.get('episodes', 1000),
            use_cached=task.parameters.get('use_cached', True)
        )
        return {"status": "completed", "task_id": task_id}
    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.save()
        return {"status": "failed", "error": str(e)}

@shared_task
def evaluate_companies_task(model_path=None):
    """Task to evaluate companies using the trained model."""
    service = ModelService()
    
    try:
        result = service.evaluate_companies(model_path)
        return {"status": "completed", "result": result}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@shared_task
def scheduled_data_update():
    """Task for scheduled daily data updates."""
    # Create data collection task
    task = DataCollectionTask.objects.create(
        task_type='news',
        status='pending',
        parameters={
            'symbols': None,  # Use all symbols
            'use_cached': False  # Always get fresh data
        }
    )
    
    # Run the task
    collect_news_data_task.delay(task.id)
    
    # Also collect market data
    market_task = DataCollectionTask.objects.create(
        task_type='market',
        status='pending',
        parameters={
            'symbols': None,  # Use all symbols
            'use_cached': False  # Always get fresh data
        }
    )
    
    collect_market_data_task.delay(market_task.id)
    
    # Process data and generate insights
    process_task = DataCollectionTask.objects.create(
        task_type='process',
        status='pending',
        parameters={}
    )
    
    process_data_task.delay(process_task.id)
    
    return {"status": "completed", "tasks_created": 3}