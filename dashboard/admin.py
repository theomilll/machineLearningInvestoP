from django.contrib import admin

from .models import (CompanyRating, DataCollectionTask, MarketInsight,
                     ModelTrainingTask, NewsArticle, Symbol)

# Register models
admin.site.register(Symbol)
admin.site.register(CompanyRating)
admin.site.register(MarketInsight)
admin.site.register(NewsArticle)
admin.site.register(DataCollectionTask)
admin.site.register(ModelTrainingTask)