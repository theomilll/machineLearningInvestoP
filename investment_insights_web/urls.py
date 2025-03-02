"""
URL configuration for investment_insights_web project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('api/', include('insights_api.urls')),
    path('accounts/', include('accounts.urls')),
    
    # Include Django's built-in auth URLs as fallback, but our custom ones in accounts.urls take precedence
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)