# C:\Users\ASUS\MyanmarTravelPlanner\users\views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, View
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.backends import ModelBackend
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import traceback
from django.utils import timezone
from django.conf import settings
import json


# ========== IMPORT PLANNER MODELS ==========
from django.shortcuts import get_object_or_404
from planner.models import Destination, Hotel, Flight, BusService, CarRental, TripPlan


class SelectHotelWithMapView(LoginRequiredMixin, View):
    """Hotel selection page with interactive Google Map"""
    template_name = 'planner/select_hotel_map.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        nights = (trip.end_date - trip.start_date).days
        if nights <= 0:
            nights = 1
        
        hotels = Hotel.objects.filter(
            destination=trip.destination,
            is_active=True
        ).order_by('price_per_night')
        
        if trip.budget_range == 'low':
            hotels = hotels.filter(category='budget')
        elif trip.budget_range == 'medium':
            hotels = hotels.filter(category__in=['budget', 'medium'])
        elif trip.budget_range == 'high':
            hotels = hotels.filter(category__in=['medium', 'luxury'])
        
        center_lat = 21.9588
        center_lng = 96.0891
        
        if trip.destination.latitude and trip.destination.longitude:
            center_lat = float(trip.destination.latitude)
            center_lng = float(trip.destination.longitude)
        
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
            'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
        }
        return render(request, self.template_name, context)


class SelectHotelView(LoginRequiredMixin, View):
    """Redirect to hotel selection with map"""
    def get(self, request, trip_id):
        return redirect('planner:select_hotel_map', trip_id=trip_id)


class SearchRealHotelsView(LoginRequiredMixin, View):
    """Search for real hotels using Google Places API"""
    def get(self, request, destination_id):
        destination = get_object_or_404(Destination, id=destination_id)
        
        if destination.latitude and destination.longitude:
            existing_hotel_names = set(
                Hotel.objects.filter(destination=destination)
                .values_list('name', flat=True)
            )
            
            available_real_hotels = []
            
            return JsonResponse({
                'success': True,
                'hotels': available_real_hotels,
                'count': len(available_real_hotels)
            })
        
        return JsonResponse({
            'success': False,
            'error': 'Destination coordinates not available'
        })


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
    
    def get_success_url(self):
        user = self.request.user
        
        # CRITICAL: Check for destination in session first
        destination_id = self.request.session.pop('pending_destination_id', None)
        destination_name = self.request.session.pop('pending_destination_name', None)
        
        print(f"🔵 CustomLoginView.get_success_url - Destination from session: {destination_name} (ID: {destination_id})")
        
        if destination_id and destination_name:
            # Redirect to plan trip with destination pre-filled
            url = reverse('planner:plan') + f'?destination_id={destination_id}&destination_name={destination_name}'
            print(f"🔵 Redirecting to: {url}")
            return url
        
        # Check for 'next' parameter
        next_url = self.request.GET.get('next')
        if next_url:
            print(f"🔵 Redirecting to next: {next_url}")
            return next_url
        
        # Default redirect
        if user.is_admin_user():
            return reverse_lazy('users:admin_dashboard')
        else:
            return reverse_lazy('planner:dashboard')
    
    def form_valid(self, form):
        user = form.get_user()
        
        # CRITICAL: Save destination from GET parameters to session BEFORE login
        destination_id = self.request.GET.get('destination_id')
        destination_name = self.request.GET.get('destination_name')
        
        print(f"🔵 CustomLoginView.form_valid - GET params - destination_id: {destination_id}, destination_name: {destination_name}")
        
        if destination_id and destination_name:
            self.request.session['pending_destination_id'] = destination_id
            self.request.session['pending_destination_name'] = destination_name
            print(f"✅ Saved destination to session: {destination_name} (ID: {destination_id})")
        
        from django.conf import settings
        backend_path = settings.AUTHENTICATION_BACKENDS[0]
        
        login(self.request, user, backend=backend_path)
        
        if user.is_admin_user():
            messages.success(self.request, f'Welcome back, Admin {user.username}!')
        else:
            messages.success(self.request, f'Welcome back, {user.username}!')
        
        return redirect(self.get_success_url())


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('planner:dashboard')
    
    def get(self, request, *args, **kwargs):
        # CRITICAL: Save destination to session if present in GET parameters
        destination_id = request.GET.get('destination_id')
        destination_name = request.GET.get('destination_name')
        print(f"🔵 SignUpView.GET - destination_id: {destination_id}, destination_name: {destination_name}")
        
        if destination_id and destination_name:
            request.session['pending_destination_id'] = destination_id
            request.session['pending_destination_name'] = destination_name
            print(f"✅ GET: Saved destination to session: {destination_name} (ID: {destination_id})")
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        try:
            # Save the user
            user = form.save()
            
            # Get the authentication backend path
            from django.conf import settings
            backend_path = settings.AUTHENTICATION_BACKENDS[0]
            
            # Auto-login the user
            login(self.request, user, backend=backend_path)
            
            # CRITICAL: Check for saved destination in session
            destination_id = self.request.session.pop('pending_destination_id', None)
            destination_name = self.request.session.pop('pending_destination_name', None)
            
            print(f"✅ After signup - Destination from session: {destination_name} (ID: {destination_id})")
            
            if destination_id and destination_name:
                # Build redirect URL with destination parameters
                redirect_url = reverse('planner:plan') + f'?destination_id={destination_id}&destination_name={destination_name}'
                messages.success(self.request, f'Account created! Welcome, {user.username}!')
                print(f"✅ Redirecting to: {redirect_url}")
                return redirect(redirect_url)
            
            messages.success(self.request, f'Account created successfully! Welcome, {user.username}!')
            return redirect(self.success_url)
            
        except Exception as e:
            messages.error(self.request, f'Error creating account: {str(e)}')
            print(f"Error details: {traceback.format_exc()}")
            return self.form_invalid(form)


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin_user()


class AdminDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'users/admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from django.contrib.auth import get_user_model
        from planner.models import Destination, Hotel, Flight, BusService, CarRental, TripPlan
        
        User = get_user_model()
        
        context['total_users'] = User.objects.count()
        context['active_users'] = User.objects.filter(is_active=True).count()
        context['new_users_today'] = User.objects.filter(
            date_joined__date=timezone.now().date()
        ).count()
        
        context['total_trips'] = TripPlan.objects.count()
        context['active_trips'] = TripPlan.objects.filter(status__in=['planning', 'booked']).count()
        context['completed_trips'] = TripPlan.objects.filter(status='completed').count()
        
        context['total_destinations'] = Destination.objects.count()
        context['popular_destinations'] = Destination.objects.all()[:5]
        
        context['total_hotels'] = Hotel.objects.count()
        context['active_hotels'] = Hotel.objects.filter(is_active=True).count()
        
        context['total_flights'] = Flight.objects.count()
        context['total_buses'] = BusService.objects.count()
        context['total_cars'] = CarRental.objects.count()
        
        context['recent_users'] = User.objects.order_by('-date_joined')[:5]
        context['recent_trips'] = TripPlan.objects.select_related('user', 'destination').order_by('-created_at')[:5]
        
        total_revenue = 0
        for trip in TripPlan.objects.filter(status__in=['booked', 'completed']):
            total_revenue += trip.get_total_cost() or 0
        
        context['total_revenue'] = total_revenue
        
        return context


def login_view(request):
    """Function-based login view with destination preservation"""
    print(f"🔵 login_view called - GET params: {request.GET}")
    
    if request.user.is_authenticated:
        print(f"🔵 User already authenticated: {request.user.username}")
        if request.user.is_admin_user():
            return redirect('users:admin_dashboard')
        else:
            return redirect('planner:dashboard')
    
    if request.method == 'POST':
        print(f"🔵 Login POST request received")
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            from django.conf import settings
            backend_path = settings.AUTHENTICATION_BACKENDS[0]
            
            login(request, user, backend=backend_path)
            
            # Check for saved destination in session
            destination_id = request.session.pop('pending_destination_id', None)
            destination_name = request.session.pop('pending_destination_name', None)
            
            print(f"🔵 After login - Destination from session: {destination_name} (ID: {destination_id})")
            
            if destination_id and destination_name:
                redirect_url = reverse('planner:plan') + f'?destination_id={destination_id}&destination_name={destination_name}'
                messages.success(request, f'Welcome back, {user.username}!')
                print(f"✅ Redirecting to plan page: {redirect_url}")
                return redirect(redirect_url)
            
            if user.is_admin_user():
                messages.success(request, f'Welcome back, Admin {user.username}!')
                return redirect('users:admin_dashboard')
            else:
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('planner:dashboard')
        else:
            print(f"🔵 Login form invalid: {form.errors}")
    else:
        form = CustomAuthenticationForm()
        
        # Save destination to session if it exists in GET parameters
        destination_id = request.GET.get('destination_id')
        destination_name = request.GET.get('destination_name')
        print(f"🔵 Login GET - destination_id: {destination_id}, destination_name: {destination_name}")
        
        if destination_id and destination_name:
            request.session['pending_destination_id'] = destination_id
            request.session['pending_destination_name'] = destination_name
            print(f"✅ Login GET: Saved destination to session: {destination_name} (ID: {destination_id})")
            print(f"🔵 Session after save: {dict(request.session)}")
    
    return render(request, 'users/login.html', {'form': form})


def signup_view(request):
    """Function-based signup view with destination preservation"""
    print(f"🔵 signup_view called - GET params: {request.GET}")
    
    if request.user.is_authenticated:
        print(f"🔵 User already authenticated: {request.user.username}")
        return redirect('planner:dashboard')
    
    if request.method == 'POST':
        print(f"🔵 Signup POST request received")
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                print(f"✅ User created: {user.username}")
                
                from django.conf import settings
                backend_path = settings.AUTHENTICATION_BACKENDS[0]
                
                login(request, user, backend=backend_path)
                print(f"✅ User logged in: {user.username}")
                
                # CRITICAL: Check for saved destination in session
                destination_id = request.session.pop('pending_destination_id', None)
                destination_name = request.session.pop('pending_destination_name', None)
                
                print(f"✅ After signup - Destination from session: {destination_name} (ID: {destination_id})")
                
                if destination_id and destination_name:
                    # Build redirect URL with destination parameters
                    redirect_url = reverse('planner:plan') + f'?destination_id={destination_id}&destination_name={destination_name}'
                    messages.success(request, f'Account created! Welcome, {user.username}!')
                    print(f"✅ Redirecting to plan page: {redirect_url}")
                    return redirect(redirect_url)
                
                messages.success(request, f'Account created successfully! Welcome, {user.username}!')
                print(f"✅ Redirecting to dashboard")
                return redirect('planner:dashboard')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
                print(f"Error details: {traceback.format_exc()}")
        else:
            print(f"🔵 Signup form invalid: {form.errors}")
    else:
        form = CustomUserCreationForm()
        
        # CRITICAL: Save destination to session if it exists in GET parameters
        destination_id = request.GET.get('destination_id')
        destination_name = request.GET.get('destination_name')
        print(f"🔵 Signup GET - destination_id: {destination_id}, destination_name: {destination_name}")
        
        if destination_id and destination_name:
            request.session['pending_destination_id'] = destination_id
            request.session['pending_destination_name'] = destination_name
            print(f"✅ Signup GET: Saved destination to session: {destination_name} (ID: {destination_id})")
            print(f"🔵 Session after save: {dict(request.session)}")
    
    return render(request, 'users/signup.html', {'form': form})


@csrf_exempt
def logout_view(request):
    """Handle logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def admin_how_it_works(request):
    """Admin-specific How It Works page"""
    if not hasattr(request.user, 'is_admin_user') or not request.user.is_admin_user:
        return redirect('planner:how_it_works')
    
    return render(request, 'users/admin_how_it_works.html')