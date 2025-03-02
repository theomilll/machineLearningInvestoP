from django.contrib.auth.models import User
from django.db import models


# Note: We're adding models here to avoid circular dependencies with dashboard app
class Watchlist(models.Model):
    """Model representing a user's watchlist of symbols."""
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class UserPreference(models.Model):
    """Model representing user preferences."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    default_watchlist = models.ForeignKey(Watchlist, on_delete=models.SET_NULL, null=True, blank=True)
    email_notifications = models.BooleanField(default=True)
    notification_frequency = models.CharField(max_length=10, default='daily')
    theme = models.CharField(max_length=10, default='light')
    
    def __str__(self):
        return f"Preferences for {self.user.username}"