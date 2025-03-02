"""
Views for the accounts app.
"""

from dashboard.models import UserPreference, Watchlist
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView

from .forms import UserProfileForm, UserRegistrationForm


class RegisterView(CreateView):
    """View for user registration."""
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('dashboard:index')
    
    def form_valid(self, form):
        """If the form is valid, save the user and log them in."""
        response = super().form_valid(form)
        
        # Get username and password
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        
        # Log the user in
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(self.request, user)
            
            # Create initial user preference
            UserPreference.objects.create(user=user)
            
            # Create a default watchlist
            default_watchlist = Watchlist.objects.create(
                name='My Watchlist',
                user=user
            )
            
            # Update user preference with default watchlist
            user_pref = UserPreference.objects.get(user=user)
            user_pref.default_watchlist = default_watchlist
            user_pref.save()
            
            messages.success(self.request, f'Account created for {username}!')
        
        return response


@login_required
def profile_view(request):
    """View for user profile page."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    # Get user's watchlists
    watchlists = Watchlist.objects.filter(user=request.user)
    
    # Get user preferences
    try:
        preferences = UserPreference.objects.get(user=request.user)
    except UserPreference.DoesNotExist:
        preferences = UserPreference.objects.create(user=request.user)
    
    context = {
        'form': form,
        'watchlists': watchlists,
        'preferences': preferences
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def update_preferences(request):
    """View to update user preferences."""
    if request.method == 'POST':
        # Get preference fields
        theme = request.POST.get('theme')
        email_notifications = request.POST.get('email_notifications') == 'on'
        notification_frequency = request.POST.get('notification_frequency')
        default_watchlist_id = request.POST.get('default_watchlist')
        
        # Get or create user preferences
        preferences, created = UserPreference.objects.get_or_create(user=request.user)
        
        # Update preferences
        preferences.theme = theme
        preferences.email_notifications = email_notifications
        preferences.notification_frequency = notification_frequency
        
        # Set default watchlist if provided
        if default_watchlist_id:
            try:
                watchlist = Watchlist.objects.get(id=default_watchlist_id, user=request.user)
                preferences.default_watchlist = watchlist
            except Watchlist.DoesNotExist:
                pass
        
        preferences.save()
        
        messages.success(request, 'Your preferences have been updated!')
    
    return redirect('accounts:profile')

class CustomLoginView(auth_views.LoginView):
    """Custom login view using our template."""
    template_name = 'accounts/login.html'