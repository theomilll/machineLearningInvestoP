"""
URL patterns for the accounts app.
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    # Override the default Django auth URL for login
    path('login/', views.CustomLoginView.as_view(), name='login'),
    
    # Other auth URLs using our templates
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/login.html'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    
    # Custom account views
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('preferences/update/', views.update_preferences, name='update_preferences'),
]