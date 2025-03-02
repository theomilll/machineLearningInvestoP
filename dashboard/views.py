"""
Views for the dashboard app.
"""

from accounts.models import UserPreference, Watchlist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import DataCollectionForm, ModelTrainingForm, WatchlistForm
from .models import (CompanyRating, DataCollectionTask, MarketInsight,
                     ModelTrainingTask, NewsArticle, Symbol)
from .tasks import (collect_market_data_task, collect_news_data_task,
                    process_data_task, train_model_task)


@login_required
def index(request):
    """Dashboard home view - shows overview of market insights and top companies."""
    # Get the latest market insight
    latest_insight = MarketInsight.objects.first()
    
    # Get top rated companies
    top_companies = CompanyRating.objects.select_related('symbol').order_by('-rating_date', '-rating')[:10]
    
    # Get latest data collection tasks
    recent_tasks = DataCollectionTask.objects.all()[:5]
    
    # Get latest news
    latest_news = NewsArticle.objects.all()[:5]
    
    # Get user's watchlists
    watchlists = Watchlist.objects.filter(user=request.user)
    
    # Get sector performance
    sector_performance = []
    if latest_insight:
        for sector, data in latest_insight.sectors.items():
            sector_performance.append({
                'name': sector,
                'rating': data.get('average_rating', 0),
                'company_count': data.get('company_count', 0)
            })
    
    # Sort sectors by rating
    sector_performance.sort(key=lambda x: x['rating'], reverse=True)
    
    context = {
        'insight': latest_insight,
        'top_companies': top_companies,
        'recent_tasks': recent_tasks,
        'latest_news': latest_news,
        'watchlists': watchlists,
        'sector_performance': sector_performance,
    }
    
    return render(request, 'dashboard/index.html', context)


@login_required
def company_list(request):
    """View to display a list of all companies with their ratings."""
    # Get filter parameters
    sector = request.GET.get('sector', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-rating')
    
    # Get latest ratings for all companies
    latest_ratings = CompanyRating.objects.select_related('symbol')
    
    # Apply filters
    if sector:
        latest_ratings = latest_ratings.filter(symbol__sector=sector)
    
    if search:
        latest_ratings = latest_ratings.filter(
            symbol__ticker__icontains=search
        ) | latest_ratings.filter(
            symbol__name__icontains=search
        )
    
    # Determine sort field
    if sort.startswith('-'):
        sort_field = sort[1:]
        sort_dir = '-'
    else:
        sort_field = sort
        sort_dir = ''
    
    # Apply sorting
    if sort_field == 'ticker':
        latest_ratings = latest_ratings.order_by(f'{sort_dir}symbol__ticker')
    elif sort_field == 'name':
        latest_ratings = latest_ratings.order_by(f'{sort_dir}symbol__name')
    elif sort_field == 'sector':
        latest_ratings = latest_ratings.order_by(f'{sort_dir}symbol__sector')
    else:
        latest_ratings = latest_ratings.order_by(sort)
    
    # Get all unique sectors for filter dropdown
    sectors = Symbol.objects.values_list('sector', flat=True).distinct()
    
    # Paginate results
    paginator = Paginator(latest_ratings, 20)
    page_number = request.GET.get('page')
    companies = paginator.get_page(page_number)
    
    context = {
        'companies': companies,
        'sectors': sectors,
        'current_sector': sector,
        'search': search,
        'sort': sort,
    }
    
    return render(request, 'dashboard/company_list.html', context)


@login_required
def company_detail(request, ticker):
    """Detailed view for a specific company."""
    # Get company information
    symbol = get_object_or_404(Symbol, ticker=ticker)
    
    # Get ratings history
    ratings = CompanyRating.objects.filter(symbol=symbol).order_by('-rating_date')
    
    # Get related news
    news = NewsArticle.objects.filter(related_symbols=symbol).order_by('-published_at')[:10]
    
    # Get user's watchlists
    watchlists = Watchlist.objects.filter(user=request.user)
    
    # Check if company is in any of the user's watchlists
    in_watchlists = []
    for watchlist in watchlists:
        if symbol in watchlist.symbols.all():
            in_watchlists.append(watchlist.id)
    
    context = {
        'symbol': symbol,
        'ratings': ratings,
        'news': news,
        'watchlists': watchlists,
        'in_watchlists': in_watchlists,
    }
    
    return render(request, 'dashboard/company_detail.html', context)


@login_required
def sector_analysis(request):
    """View for sector analysis."""
    # Get the latest market insight
    latest_insight = MarketInsight.objects.first()
    
    # Get all sectors and their performance
    sector_performance = []
    if latest_insight and 'sectors' in latest_insight.sectors:
        for sector, data in latest_insight.sectors.items():
            sector_performance.append({
                'name': sector,
                'rating': data.get('average_rating', 0),
                'company_count': data.get('company_count', 0),
                'top_company_symbol': data.get('top_company')
            })
    
    # Get top company details for each sector
    for sector in sector_performance:
        if sector.get('top_company_symbol'):
            try:
                symbol = Symbol.objects.get(ticker=sector['top_company_symbol'])
                top_rating = CompanyRating.objects.filter(symbol=symbol).order_by('-rating_date').first()
                if top_rating:
                    sector['top_company'] = {
                        'ticker': symbol.ticker,
                        'name': symbol.name,
                        'rating': top_rating.rating
                    }
            except Symbol.DoesNotExist:
                pass
    
    # Sort sectors by rating
    sector_performance.sort(key=lambda x: x['rating'], reverse=True)
    
    context = {
        'insight': latest_insight,
        'sector_performance': sector_performance,
    }
    
    return render(request, 'dashboard/sector_analysis.html', context)


@login_required
def watchlist_view(request, watchlist_id=None):
    """View for displaying and managing watchlists."""
    if watchlist_id:
        watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    else:
        # Get default or first watchlist
        try:
            watchlist = request.user.preferences.default_watchlist
            if not watchlist:
                watchlist = Watchlist.objects.filter(user=request.user).first()
        except:
            watchlist = Watchlist.objects.filter(user=request.user).first()
    
    # Get all user's watchlists for the dropdown
    all_watchlists = Watchlist.objects.filter(user=request.user)
    
    # Get form for creating new watchlist
    form = WatchlistForm()
    
    if request.method == 'POST':
        form = WatchlistForm(request.POST)
        if form.is_valid():
            new_watchlist = form.save(commit=False)
            new_watchlist.user = request.user
            new_watchlist.save()
            messages.success(request, f"Watchlist '{new_watchlist.name}' created.")
            return redirect('dashboard:watchlist', watchlist_id=new_watchlist.id)
    
    context = {
        'watchlist': watchlist,
        'all_watchlists': all_watchlists,
        'form': form,
    }
    
    return render(request, 'dashboard/watchlist.html', context)


@login_required
@require_POST
def watchlist_add_symbol(request, watchlist_id, ticker):
    """Add a symbol to a watchlist."""
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    symbol = get_object_or_404(Symbol, ticker=ticker)
    
    watchlist.symbols.add(symbol)
    messages.success(request, f"{ticker} added to {watchlist.name} watchlist.")
    
    # Return to the referring page
    next_url = request.POST.get('next', 'dashboard:index')
    return HttpResponseRedirect(next_url)


@login_required
@require_POST
def watchlist_remove_symbol(request, watchlist_id, ticker):
    """Remove a symbol from a watchlist."""
    watchlist = get_object_or_404(Watchlist, id=watchlist_id, user=request.user)
    symbol = get_object_or_404(Symbol, ticker=ticker)
    
    watchlist.symbols.remove(symbol)
    messages.success(request, f"{ticker} removed from {watchlist.name} watchlist.")
    
    # Return to the referring page
    next_url = request.POST.get('next', 'dashboard:watchlist')
    return HttpResponseRedirect(next_url)


@login_required
def news_list(request):
    """View to display a list of news articles."""
    # Get filter parameters
    search = request.GET.get('search', '')
    source = request.GET.get('source', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Query all news
    news = NewsArticle.objects.all()
    
    # Apply filters
    if search:
        news = news.filter(title__icontains=search) | news.filter(description__icontains=search)
    
    if source:
        news = news.filter(source=source)
    
    if start_date:
        news = news.filter(published_at__gte=start_date)
    
    if end_date:
        news = news.filter(published_at__lte=end_date)
    
    # Get all sources for filter dropdown
    sources = NewsArticle.objects.values_list('source', flat=True).distinct()
    
    # Paginate results
    paginator = Paginator(news, 20)
    page_number = request.GET.get('page')
    articles = paginator.get_page(page_number)
    
    context = {
        'articles': articles,
        'sources': sources,
        'search': search,
        'source': source,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'dashboard/news_list.html', context)


@login_required
def data_management(request):
    """View for managing data collection and processing tasks."""
    # Get recent data collection tasks
    tasks = DataCollectionTask.objects.all()[:20]
    
    # Create form for new data collection task
    form = DataCollectionForm()
    
    if request.method == 'POST':
        form = DataCollectionForm(request.POST)
        if form.is_valid():
            task_type = form.cleaned_data['task_type']
            parameters = {
                'symbols': form.cleaned_data['symbols'].split(',') if form.cleaned_data['symbols'] else None,
                'use_cached': form.cleaned_data['use_cached'],
            }
            
            task = DataCollectionTask.objects.create(
                task_type=task_type,
                status='pending',
                parameters=parameters
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
            
            messages.success(request, f"{task_type.capitalize()} task started.")
            return redirect('dashboard:data_management')
    
    context = {
        'tasks': tasks,
        'form': form,
    }
    
    return render(request, 'dashboard/data_management.html', context)


@login_required
def model_training(request):
    """View for managing model training tasks."""
    # Get recent training tasks
    tasks = ModelTrainingTask.objects.all()[:10]
    
    # Create form for new training task
    form = ModelTrainingForm()
    
    if request.method == 'POST':
        form = ModelTrainingForm(request.POST)
        if form.is_valid():
            parameters = {
                'symbols': form.cleaned_data['symbols'].split(',') if form.cleaned_data['symbols'] else None,
                'episodes': form.cleaned_data['episodes'],
                'use_cached': form.cleaned_data['use_cached'],
            }
            
            task = ModelTrainingTask.objects.create(
                status='pending',
                parameters=parameters,
                total_epochs=form.cleaned_data['episodes']
            )
            
            # Start the celery task
            celery_task = train_model_task.delay(task.id)
            
            # Update task with celery task ID
            task.celery_task_id = celery_task.id
            task.save()
            
            messages.success(request, "Model training task started.")
            return redirect('dashboard:model_training')
    
    context = {
        'tasks': tasks,
        'form': form,
    }
    
    return render(request, 'dashboard/model_training.html', context)


@login_required
def task_status(request, task_id):
    """AJAX view to get the status of a task."""
    try:
        if 'data_task' in request.GET:
            task = DataCollectionTask.objects.get(id=task_id)
            data = {
                'status': task.status,
                'started_at': task.started_at.isoformat(),
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'error_message': task.error_message,
            }
        else:
            task = ModelTrainingTask.objects.get(id=task_id)
            data = {
                'status': task.status,
                'started_at': task.started_at.isoformat(),
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'epochs_completed': task.epochs_completed,
                'total_epochs': task.total_epochs,
                'progress': int((task.epochs_completed / task.total_epochs) * 100) if task.total_epochs else 0,
                'metrics': task.metrics,
                'error_message': task.error_message,
            }
        
        return JsonResponse({'success': True, 'data': data})
    except (DataCollectionTask.DoesNotExist, ModelTrainingTask.DoesNotExist):
        return JsonResponse({'success': False, 'error': 'Task not found'})


@login_required
def insight_detail(request, insight_id):
    """Detailed view for a specific market insight."""
    insight = get_object_or_404(MarketInsight, id=insight_id)
    
    # Extract top companies
    top_companies = []
    for company_data in insight.top_companies:
        try:
            symbol = Symbol.objects.get(ticker=company_data.get('symbol'))
            company = {
                'ticker': symbol.ticker,
                'name': symbol.name,
                'rating': company_data.get('rating', 0),
                'sector': symbol.sector
            }
            top_companies.append(company)
        except Symbol.DoesNotExist:
            pass
    
    # Extract sector information
    sector_data = []
    for sector, data in insight.sectors.items():
        sector_info = {
            'name': sector,
            'rating': data.get('average_rating', 0),
            'company_count': data.get('company_count', 0)
        }
        
        # Try to get top company for the sector
        if data.get('top_company'):
            try:
                symbol = Symbol.objects.get(ticker=data.get('top_company'))
                sector_info['top_company'] = {
                    'ticker': symbol.ticker,
                    'name': symbol.name
                }
            except Symbol.DoesNotExist:
                pass
        
        sector_data.append(sector_info)
    
    # Sort sectors by rating
    sector_data.sort(key=lambda x: x['rating'], reverse=True)
    
    context = {
        'insight': insight,
        'top_companies': top_companies,
        'sector_data': sector_data,
    }
    
    return render(request, 'dashboard/insight_detail.html', context)