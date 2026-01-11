# C:\Users\ASUS\MyanmarTravelPlanner\users\views.py

from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.backends import ModelBackend
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser

from django.http import JsonResponse
import traceback

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py (ADD THESE VIEWS)
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
import json
from planner.models import Destination, Hotel, Flight, BusService, CarRental, TripPlan

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# Add these imports at the top:
from django.conf import settings
import json


# Add this class to your views.py (add it after the SelectHotelView class):

class SelectHotelWithMapView(LoginRequiredMixin, View):
    """Hotel selection page with interactive Google Map"""
    template_name = 'planner/select_hotel_map.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        # Calculate number of nights
        nights = (trip.end_date - trip.start_date).days
        if nights <= 0:
            nights = 1
        
        # Get hotels for the destination
        hotels = Hotel.objects.filter(
            destination=trip.destination,
            is_active=True
        ).order_by('price_per_night')
        
        # Filter by budget if specified
        if trip.budget_range == 'low':
            hotels = hotels.filter(category='budget')
        elif trip.budget_range == 'medium':
            hotels = hotels.filter(category__in=['budget', 'medium'])
        elif trip.budget_range == 'high':
            hotels = hotels.filter(category__in=['medium', 'luxury'])
        
        # Get destination coordinates for map center
        center_lat = 21.9588  # Default to Myanmar center
        center_lng = 96.0891
        
        if trip.destination.latitude and trip.destination.longitude:
            center_lat = float(trip.destination.latitude)
            center_lng = float(trip.destination.longitude)
        else:
            # Try to get coordinates from Google Maps
            if maps_service and trip.destination.name:
                geocode_result = maps_service.geocode_address(f"{trip.destination.name}, Myanmar")
                if geocode_result:
                    center_lat = geocode_result['latitude']
                    center_lng = geocode_result['longitude']
        
        # Prepare hotel data for map
        hotel_markers = []
        for hotel in hotels:
            if hotel.has_coordinates():
                hotel_markers.append(hotel.get_map_marker())
        
        context = {
            'trip': trip,
            'hotels': hotels,
            'nights': nights,
            'hotel_markers': json.dumps(hotel_markers),
            'center_lat': center_lat,
            'center_lng': center_lng,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        }
        return render(request, self.template_name, context)

# Also add the SearchRealHotelsView:
class SearchRealHotelsView(LoginRequiredMixin, View):
    """Search for real hotels using Google Places API"""
    def get(self, request, destination_id):
        destination = get_object_or_404(Destination, id=destination_id)
        
        # Get destination coordinates
        if destination.latitude and destination.longitude:
            # Search for nearby hotels
            real_hotels = maps_service.search_nearby_hotels(
                float(destination.latitude),
                float(destination.longitude)
            )
            
            # Filter out hotels that already exist in our database
            existing_hotel_names = set(
                Hotel.objects.filter(destination=destination)
                .values_list('name', flat=True)
            )
            
            # Filter to show only hotels not in our database
            available_real_hotels = [
                hotel for hotel in real_hotels 
                if hotel['name'] not in existing_hotel_names
            ]
            
            return JsonResponse({
                'success': True,
                'hotels': available_real_hotels,
                'count': len(available_real_hotels)
            })
        
        return JsonResponse({
            'success': False,
            'error': 'Destination coordinates not available'
        })
# Add this new view
class SelectHotelWithMapView(LoginRequiredMixin, View):
    """Hotel selection page with interactive Google Map"""
    template_name = 'planner/select_hotel_map.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        # Calculate number of nights
        nights = (trip.end_date - trip.start_date).days
        if nights <= 0:
            nights = 1
        
        # Get hotels for the destination
        hotels = Hotel.objects.filter(
            destination=trip.destination,
            is_active=True
        ).order_by('price_per_night')
        
        # Filter by budget if specified
        if trip.budget_range == 'low':
            hotels = hotels.filter(category='budget')
        elif trip.budget_range == 'medium':
            hotels = hotels.filter(category__in=['budget', 'medium'])
        elif trip.budget_range == 'high':
            hotels = hotels.filter(category__in=['medium', 'luxury'])
        
        # Get destination coordinates for map center
        center_lat = 21.9588  # Default to Yangon
        center_lng = 96.0891
        
        if trip.destination.latitude and trip.destination.longitude:
            center_lat = float(trip.destination.latitude)
            center_lng = float(trip.destination.longitude)
        
        # Prepare hotel data for map
        hotel_markers = []
        for hotel in hotels:
            if hotel.has_coordinates():
                hotel_markers.append(hotel.get_map_marker())
        
        context = {
            'trip': trip,
            'hotels': hotels,
            'nights': nights,
            'hotel_markers': json.dumps(hotel_markers),
            'center_lat': center_lat,
            'center_lng': center_lng,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        }
        return render(request, self.template_name, context)

# Update this class in planner/views.py
class SelectHotelView(LoginRequiredMixin, View):
    """Redirect to hotel selection with map"""
    def get(self, request, trip_id):
        return redirect('planner:select_hotel_map', trip_id=trip_id)

# Add a view to search for real hotels on Google Maps
class SearchRealHotelsView(LoginRequiredMixin, View):
    """Search for real hotels using Google Places API"""
    def get(self, request, destination_id):
        destination = get_object_or_404(Destination, id=destination_id)
        
        # Get destination coordinates
        if destination.latitude and destination.longitude:
            # Search for nearby hotels
            real_hotels = maps_service.search_nearby_hotels(
                float(destination.latitude),
                float(destination.longitude)
            )
            
            # Filter out hotels that already exist in our database
            existing_hotel_names = set(
                Hotel.objects.filter(destination=destination)
                .values_list('name', flat=True)
            )
            
            # Filter to show only hotels not in our database
            available_real_hotels = [
                hotel for hotel in real_hotels 
                if hotel['name'] not in existing_hotel_names
            ]
            
            return JsonResponse({
                'success': True,
                'hotels': available_real_hotels,
                'count': len(available_real_hotels)
            })
        
        return JsonResponse({
            'success': False,
            'error': 'Destination coordinates not available'
        })

# Add this to your existing urls.py

def check_email_availability(request):
    """Check if email is available"""
    email = request.GET.get('email', '').lower()
    if email:
        exists = CustomUser.objects.filter(email=email).exists()
        return JsonResponse({'available': not exists})
    return JsonResponse({'available': False})

def force_logout_view(request):
    """Force logout endpoint for debugging"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        """Add custom messages after successful login"""
        # Get the user from the form
        user = form.get_user()
        
        # Specify which backend to use for this user
        # Use the first backend from AUTHENTICATION_BACKENDS
        from django.conf import settings
        backend_path = settings.AUTHENTICATION_BACKENDS[0]
        
        # Manually log in the user with the specified backend
        login(self.request, user, backend=backend_path)
        
        # Add custom messages
        if user.is_admin_user():
            messages.success(self.request, f'Welcome back, Admin {user.username}!')
        else:
            messages.success(self.request, f'Welcome back, {user.username}!')
        
        # Redirect to appropriate page
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        user = self.request.user
        
        if user.is_admin_user():
            return reverse_lazy('users:admin_dashboard')
        else:
            return reverse_lazy('planner:dashboard')

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('planner:dashboard')
    
    def form_valid(self, form):
        try:
            # Save the user
            user = form.save()
            
            # Get the authentication backend path
            from django.conf import settings
            backend_path = settings.AUTHENTICATION_BACKENDS[0]
            
            # Auto-login the user with backend specified
            login(self.request, user, backend=backend_path)
            
            messages.success(self.request, f'Account created successfully! Welcome, {user.username}!')
            return redirect(self.success_url)
            
        except Exception as e:
            messages.error(self.request, f'Error creating account: {str(e)}')
            # For debugging
            print(f"Error details: {traceback.format_exc()}")
            return self.form_invalid(form)

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
    # Add these function-based views at the end of views.py

def login_view(request):
    """Function-based login view"""
    if request.user.is_authenticated:
        # Redirect authenticated users to appropriate dashboard
        if request.user.is_admin_user():
            return redirect('users:admin_dashboard')
        else:
            return redirect('planner:dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Specify backend
            from django.conf import settings
            backend_path = settings.AUTHENTICATION_BACKENDS[0]
            
            login(request, user, backend=backend_path)
            
            if user.is_admin_user():
                messages.success(request, f'Welcome back, Admin {user.username}!')
                return redirect('users:admin_dashboard')
            else:
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('planner:dashboard')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})

def signup_view(request):
    """Function-based signup view"""
    if request.user.is_authenticated:
        return redirect('planner:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                
                # Specify backend
                from django.conf import settings
                backend_path = settings.AUTHENTICATION_BACKENDS[0]
                
                login(request, user, backend=backend_path)
                
                messages.success(request, f'Account created successfully! Welcome, {user.username}!')
                return redirect('planner:dashboard')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
                print(f"Error details: {traceback.format_exc()}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/signup.html', {'form': form})

def logout_view(request):
    """Function-based logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')