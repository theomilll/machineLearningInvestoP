"""
URL patterns for the dashboard app.
"""

from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard home
    path('', views.index, name='index'),
    
    # Company views
    path('companies/', views.company_list, name='company_list'),
    path('companies/<str:ticker>/', views.company_detail, name='company_detail'),
    
    # Sector analysis
    path('sectors/', views.sector_analysis, name='sector_analysis'),
    
    # Watchlist views
    path('watchlists/', views.watchlist_view, name='watchlist'),
    path('watchlists/<int:watchlist_id>/', views.watchlist_view, name='watchlist'),
    path('watchlists/<int:watchlist_id>/add/<str:ticker>/', views.watchlist_add_symbol, name='watchlist_add_symbol'),
    path('watchlists/<int:watchlist_id>/remove/<str:ticker>/', views.watchlist_remove_symbol, name='watchlist_remove_symbol'),
    
    # News views
    path('news/', views.news_list, name='news_list'),
    
    # Data management
    path('data/', views.data_management, name='data_management'),
    
    # Model training
    path('model/', views.model_training, name='model_training'),
    
    # Task status (AJAX)
    path('task_status/<int:task_id>/', views.task_status, name='task_status'),
    
    # Market insights
    path('insights/<int:insight_id>/', views.insight_detail, name='insight_detail'),
]