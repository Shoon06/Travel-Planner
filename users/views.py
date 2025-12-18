from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser
from django.utils import timezone


def force_logout_view(request):
    """Force logout endpoint for debugging"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# views.py - Update CustomLoginView
class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = CustomAuthenticationForm
    
    def form_valid(self, form):
        # Since usernames can be duplicate, we rely on email for login
        # The form already handles authentication by email
        user = form.get_user()
        
        if user is not None:
            login(self.request, user)
            
            if user.is_admin_user():
                messages.success(self.request, f'Welcome back, Admin {user.username}!')
                return redirect('users:admin_dashboard')
            else:
                messages.success(self.request, f'Welcome back, {user.username}!')
                return redirect('planner:dashboard')
        else:
            messages.error(self.request, 'Invalid email or password. Please try again.')
            return self.form_invalid(form)

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        # Check if email already exists
        email = form.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            messages.error(self.request, 'This email is already registered. Please use a different email or login.')
            return self.form_invalid(form)
        
        user = form.save(commit=False)
        user.user_type = 'user'
        user.save()
        
        if not user.email:
            user.email = form.cleaned_data.get('email', '')
            user.save()
            
        messages.success(self.request, 'Account created successfully! Please login.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if 'email' in form.errors:
            messages.error(self.request, 'This email is already registered. Please use a different email.')
        return super().form_invalid(form)

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin_user()

class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'users/admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Real statistics
        from django.contrib.auth import get_user_model
        from planner.models import Destination, Hotel, Flight, BusService, CarRental, TripPlan
        
        User = get_user_model()
        
        # User statistics
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['new_users_today'] = User.objects.filter(
            date_joined__date=timezone.now().date()
        ).count()
        
        # Trip statistics
        context['total_trips'] = TripPlan.objects.count()
        context['active_trips'] = TripPlan.objects.filter(status__in=['planning', 'booked']).count()
        context['completed_trips'] = TripPlan.objects.filter(status='completed').count()
        
        # Destination statistics
        context['total_destinations'] = Destination.objects.count()
        context['popular_destinations'] = Destination.objects.all()[:5]
        
        # Hotel statistics
        context['total_hotels'] = Hotel.objects.count()
        context['active_hotels'] = Hotel.objects.filter(is_active=True).count()
        
        # Transport statistics
        context['total_flights'] = Flight.objects.count()
        context['total_buses'] = BusService.objects.count()
        context['total_cars'] = CarRental.objects.count()
        
        # Recent activity
        context['recent_users'] = User.objects.order_by('-date_joined')[:5]
        context['recent_trips'] = TripPlan.objects.select_related('user', 'destination').order_by('-created_at')[:5]
        
        # Revenue calculation (simplified)
        total_revenue = 0
        for trip in TripPlan.objects.filter(status__in=['booked', 'completed']):
            total_revenue += trip.get_total_cost() or 0
        
        context['total_revenue'] = total_revenue
        
        return context