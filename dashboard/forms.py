"""
Forms for the dashboard app.
"""

from django import forms
from django.conf import settings

from .models import UserPreference, Watchlist


class WatchlistForm(forms.ModelForm):
    """Form for creating and editing watchlists."""
    
    class Meta:
        model = Watchlist
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Watchlist Name'})
        }


class DataCollectionForm(forms.Form):
    """Form for initiating data collection tasks."""
    
    TASK_CHOICES = [
        ('news', 'Collect News Data'),
        ('market', 'Collect Market Data'),
        ('process', 'Process Data'),
    ]
    
    task_type = forms.ChoiceField(
        choices=TASK_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    symbols = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'NVDA,AAPL,MSFT (leave empty for default symbols)'
        })
    )
    
    use_cached = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_symbols(self):
        """Clean and validate symbols."""
        symbols = self.cleaned_data.get('symbols', '')
        if not symbols:
            return ''
        
        # Split by comma and strip whitespace
        symbols_list = [s.strip().upper() for s in symbols.split(',')]
        
        # Remove duplicates
        symbols_list = list(dict.fromkeys(symbols_list))
        
        # Join back into comma-separated string
        return ','.join(symbols_list)


class ModelTrainingForm(forms.Form):
    """Form for initiating model training tasks."""
    
    symbols = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'NVDA,AAPL,MSFT (leave empty for default symbols)'
        })
    )
    
    episodes = forms.IntegerField(
        min_value=10,
        max_value=10000,
        initial=1000,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    use_cached = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_symbols(self):
        """Clean and validate symbols."""
        symbols = self.cleaned_data.get('symbols', '')
        if not symbols:
            return ''
        
        # Split by comma and strip whitespace
        symbols_list = [s.strip().upper() for s in symbols.split(',')]
        
        # Remove duplicates
        symbols_list = list(dict.fromkeys(symbols_list))
        
        # Join back into comma-separated string
        return ','.join(symbols_list)


class UserPreferenceForm(forms.ModelForm):
    """Form for editing user preferences."""
    
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]
    
    NOTIFICATION_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('never', 'Never'),
    ]
    
    theme = forms.ChoiceField(
        choices=THEME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    notification_frequency = forms.ChoiceField(
        choices=NOTIFICATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = UserPreference
        fields = ['default_watchlist', 'email_notifications', 'notification_frequency', 'theme']
        widgets = {
            'default_watchlist': forms.Select(attrs={'class': 'form-select'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SymbolSearchForm(forms.Form):
    """Form for searching symbols."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by symbol or name'
        })
    )
    
    sector = forms.ChoiceField(
        required=False,
        choices=[('', 'All Sectors')],  # Choices will be populated in the view
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('-rating', 'Rating (High to Low)'),
            ('rating', 'Rating (Low to High)'),
            ('ticker', 'Symbol (A-Z)'),
            ('-ticker', 'Symbol (Z-A)'),
            ('name', 'Name (A-Z)'),
            ('-name', 'Name (Z-A)'),
            ('sector', 'Sector (A-Z)'),
            ('-sector', 'Sector (Z-A)'),
        ],
        initial='-rating',
        widget=forms.Select(attrs={'class': 'form-select'})
    )