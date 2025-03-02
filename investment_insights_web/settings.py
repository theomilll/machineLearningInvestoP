"""
Django settings for investment_insights_web project.
"""

import os
from pathlib import Path

import environ
from celery.schedules import crontab

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, 'default-secret-key-for-dev'),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    DATABASE_URL=(str, 'sqlite:///db.sqlite3')
)

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_celery_results',
    'django_celery_beat',
    'django_filters',
    'channels',
    
    # Project apps - accounts must come before dashboard since dashboard now depends on accounts models
    'accounts.apps.AccountsConfig',
    'dashboard.apps.DashboardConfig',
    'insights_api.apps.InsightsApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'investment_insights_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'investment_insights_web.wsgi.application'
ASGI_APPLICATION = 'investment_insights_web.asgi.application'

# Database
DATABASES = {
    'default': env.db(),
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Authentication
LOGIN_REDIRECT_URL = 'dashboard:index'  # This should redirect to dashboard after login
LOGOUT_REDIRECT_URL = 'accounts:login'
LOGIN_URL = 'accounts:login'

CELERY_BEAT_SCHEDULE = {
    'daily-data-update': {
        'task': 'dashboard.tasks.scheduled_data_update',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight
    },
    'weekly-model-evaluation': {
        'task': 'dashboard.tasks.evaluate_companies_task',
        'schedule': crontab(day_of_week=0, hour=1, minute=0),  # Run at 1 AM on Sundays
    },
}

# Celery Configuration
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Investment Insights Configuration
INVESTMENT_INSIGHTS = {
    'DATA_DIR': os.path.join(BASE_DIR, 'insights_data'),
    'MODEL_DIR': os.path.join(BASE_DIR, 'insights_models'),
    'DEFAULT_SYMBOLS': {
        'tech': ['NVDA', 'AMD', 'INTC', 'TSM', 'AVGO', 'MSFT', 'GOOGL', 'AAPL', 'AMZN', 'META'],
        'energy': ['XOM', 'CVX', 'BP', 'SHEL', 'COP'],
    }
}

# Path to ML system directory - adjust this to your actual path
ML_SYSTEM_PATH = os.path.join(BASE_DIR, '..', 'investment_insights')

# Create data and model directories if they don't exist
os.makedirs(INVESTMENT_INSIGHTS['DATA_DIR'], exist_ok=True)
os.makedirs(INVESTMENT_INSIGHTS['MODEL_DIR'], exist_ok=True)