from django.contrib import admin

from .models import UserPreference, Watchlist

# Register models for admin panel
admin.site.register(UserPreference)
admin.site.register(Watchlist)