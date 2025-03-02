"""
URL patterns for the insights_api app.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'symbols', views.SymbolViewSet)
router.register(r'ratings', views.CompanyRatingViewSet)
router.register(r'insights', views.MarketInsightViewSet)
router.register(r'news', views.NewsArticleViewSet)
router.register(r'data-tasks', views.DataCollectionTaskViewSet)
router.register(r'training-tasks', views.ModelTrainingTaskViewSet)

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Action APIs
    path('collect-data/', views.start_data_collection, name='collect_data'),
    path('train-model/', views.start_model_training, name='train_model'),
    path('evaluate-companies/', views.evaluate_companies, name='evaluate_companies'),
    
    # Dashboard stats
    path('dashboard-stats/', views.dashboard_stats, name='dashboard_stats'),
    
    # Authentication
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]