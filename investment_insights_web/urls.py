"""
URL configuration for investment_insights_web project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),  # Changed from '' to 'dashboard/'
    path('api/', include('insights_api.urls')),
    path('accounts/', include('accounts.urls')),
    
    # Include Django's built-in auth URLs as fallback
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Redirect root URL to login page
    path('', RedirectView.as_view(url='accounts/login/'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)