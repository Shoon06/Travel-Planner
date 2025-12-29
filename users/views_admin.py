# C:\Users\ASUS\MyanmarTravelPlanner\users\views_admin.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
import json
from datetime import datetime

from .models import CustomUser
from planner.models import TripPlan, Destination, Hotel, Flight, BusService, CarRental
from posts.models import Post
from .forms_admin import CustomUserAdminForm, DestinationForm, HotelForm, FlightForm, BusServiceForm

# ==================== ADMIN CHECK ====================
def is_admin(user):
    """Check if user is admin"""
    return user.is_superuser or user.groups.filter(name='Admin').exists() or getattr(user, 'user_type', None) == 'admin'

# ==================== ADMIN DASHBOARD ====================
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard view"""
    # Statistics
    total_users = CustomUser.objects.count()
    total_hotels = Hotel.objects.count()
    total_trips = TripPlan.objects.count()
    total_destinations = Destination.objects.count()
    total_flights = Flight.objects.count()
    total_buses = BusService.objects.count()
    
    # Recent activities
    recent_hotels = Hotel.objects.order_by('-created_at')[:5]
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    recent_trips = TripPlan.objects.select_related('user', 'destination').order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_hotels': total_hotels,
        'total_trips': total_trips,
        'total_destinations': total_destinations,
        'total_flights': total_flights,
        'total_buses': total_buses,
        'recent_hotels': recent_hotels,
        'recent_users': recent_users,
        'recent_trips': recent_trips,
    }
    
    return render(request, 'users/admin_dashboard.html', context)

# ==================== HOTEL MANAGEMENT (Function-Based) ====================
@user_passes_test(is_admin)
def admin_hotels(request):
    """Admin hotel management view"""
    hotels = Hotel.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        hotels = hotels.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by destination
    destination_id = request.GET.get('destination', '')
    if destination_id:
        hotels = hotels.filter(destination_id=destination_id)
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        hotels = hotels.filter(category=category)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        hotels = hotels.filter(is_active=True)
    elif status == 'inactive':
        hotels = hotels.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(hotels, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_hotels = Hotel.objects.count()
    active_hotels = Hotel.objects.filter(is_active=True).count()
    destinations = Destination.objects.all()
    
    context = {
        'hotels': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'total_hotels': total_hotels,
        'active_hotels': active_hotels,
        'destinations': destinations,
    }
    
    return render(request, 'users/admin_hotels.html', context)

@user_passes_test(is_admin)
def admin_add_hotel(request):
    """Add new hotel view"""
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save()
            messages.success(request, f'Hotel "{hotel.name}" added successfully!')
            return redirect('users:admin_hotels')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HotelForm()
    
    destinations = Destination.objects.all()
    context = {
        'form': form,
        'destinations': destinations,
    }
    return render(request, 'users/admin_add_hotel.html', context)
# C:\Users\ASUS\MyanmarTravelPlanner\users\views_admin.py
# Add this new view function (add it near other hotel management views):

@user_passes_test(is_admin)
def admin_add_hotel_with_map(request):
    """Add new hotel with map location picker"""
    if request.method == 'POST':
        # Parse amenities from comma-separated string
        amenities_text = request.POST.get('amenities', '')
        amenities = [amenity.strip() for amenity in amenities_text.split(',') if amenity.strip()]
        
        # Prepare data for form
        form_data = request.POST.copy()
        form_data['amenities'] = json.dumps(amenities)
        
        form = HotelForm(form_data, request.FILES)
        
        if form.is_valid():
            hotel = form.save(commit=False)
            
            # Set coordinates if provided
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            
            if lat and lng:
                try:
                    hotel.latitude = float(lat)
                    hotel.longitude = float(lng)
                except (ValueError, TypeError):
                    pass
            
            hotel.created_by_admin = True
            hotel.save()
            
            messages.success(request, f'Hotel "{hotel.name}" added successfully with location!')
            return redirect('users:admin_hotels')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HotelForm()
    
    destinations = Destination.objects.all()
    context = {
        'form': form,
        'destinations': destinations,
    }
    return render(request, 'users/admin_add_hotel_maps.html', context)

# Also update your admin_hotels template to add a button for the new map-based form
@user_passes_test(is_admin)
def admin_edit_hotel(request, hotel_id):
    """Edit hotel view"""
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, f'Hotel "{hotel.name}" updated successfully!')
            return redirect('users:admin_hotels')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HotelForm(instance=hotel)
    
    context = {
        'form': form,
        'hotel': hotel,
    }
    return render(request, 'users/admin_edit_hotel.html', context)

@user_passes_test(is_admin)
def admin_delete_hotel(request, hotel_id):
    """Delete hotel view (AJAX)"""
    if request.method == 'POST':
        try:
            hotel = Hotel.objects.get(id=hotel_id)
            hotel_name = hotel.name
            hotel.delete()
            return JsonResponse({'success': True, 'message': f'Hotel "{hotel_name}" deleted successfully!'})
        except Hotel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Hotel not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# ==================== ADMIN MIXIN ====================
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user)

# ==================== USER MANAGEMENT (Class-Based) ====================
class AdminUserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'users/admin_dashboard_users.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = CustomUser.objects.all().order_by('-date_joined')
        
        # Search
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Filter by type
        user_type = self.request.GET.get('type', '')
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate statistics
        context['total_users'] = CustomUser.objects.count()
        context['admin_count'] = CustomUser.objects.filter(user_type='admin').count()
        context['regular_users'] = CustomUser.objects.filter(user_type='user').count()
        context['active_users_count'] = CustomUser.objects.filter(is_active=True).count()
        context['new_users_today'] = CustomUser.objects.filter(
            date_joined__date=timezone.now().date()
        ).count()
        
        return context

class AdminAddUserView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserAdminForm
    template_name = 'users/admin_add_user.html'
    success_url = reverse_lazy('users:admin_dashboard_users')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'User {self.object.username} created successfully!')
        return response

class AdminUserRolesView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'users/admin_user_roles.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = CustomUser.objects.all().order_by('-date_joined')
        context['users'] = users
        context['user_types'] = CustomUser.USER_TYPE_CHOICES
        
        # Calculate counts
        context['admin_count'] = users.filter(user_type='admin').count()
        context['user_count'] = users.filter(user_type='user').count()
        
        return context

# ==================== AJAX FUNCTIONS ====================
def admin_update_user_role(request):
    """Update user role via AJAX"""
    if request.method == 'POST' and is_admin(request.user):
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            new_role = data.get('role')
            
            user = CustomUser.objects.get(id=user_id)
            old_role = user.user_type
            
            if user == request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot modify your own role'
                })
            
            user.user_type = new_role
            
            # Update staff status based on role
            if new_role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            else:
                user.is_staff = False
                user.is_superuser = False
            
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': f'User {user.username} role changed from {old_role} to {new_role}'
            })
            
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request'
    })

def admin_toggle_user_active(request, user_id):
    """Toggle user active status"""
    if request.method == 'POST' and is_admin(request.user):
        try:
            user = CustomUser.objects.get(id=user_id)
            if user != request.user:  # Prevent deactivating yourself
                user.is_active = not user.is_active
                user.save()
                return JsonResponse({
                    'success': True,
                    'is_active': user.is_active,
                    'message': f'User {user.username} {"activated" if user.is_active else "deactivated"}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot modify your own account'
                })
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'User not found'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request'
    })

# ==================== TRIP MANAGEMENT ====================
class AdminTripListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = TripPlan
    template_name = 'users/admin_trip_list.html'
    context_object_name = 'trips'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = TripPlan.objects.select_related('user', 'destination').order_by('-created_at')
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(destination__name__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_users'] = CustomUser.objects.all()
        context['destinations'] = Destination.objects.all()
        
        # Get status choices from TripPlan model
        context['status_choices'] = [
            ('draft', 'Draft'),
            ('planning', 'Planning'),
            ('booked', 'Booked'),
            ('completed', 'Completed'),
        ]
        
        return context

class AdminTripAnalyticsView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'users/admin_trip_analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic statistics
        context['total_trips'] = TripPlan.objects.count()
        context['active_trips'] = TripPlan.objects.filter(status__in=['planning', 'booked']).count()
        context['completed_trips'] = TripPlan.objects.filter(status='completed').count()
        
        # Revenue calculation
        revenue_trips = TripPlan.objects.filter(status__in=['booked', 'completed'])
        total_revenue = 0
        for trip in revenue_trips:
            # Calculate cost based on hotel and transport
            cost = 0
            if trip.selected_hotel:
                nights = (trip.end_date - trip.start_date).days
                if nights <= 0:
                    nights = 1
                cost += float(trip.selected_hotel.price_per_night * nights * 2100)
            
            if trip.selected_transport and isinstance(trip.selected_transport, dict):
                if 'price' in trip.selected_transport:
                    cost += float(trip.selected_transport.get('price', 0))
            
            total_revenue += cost
        
        context['total_revenue'] = total_revenue
        
        # Popular destinations (count trips per destination)
        from django.db.models import Count
        popular_destinations = []
        for dest in Destination.objects.all():
            trip_count = TripPlan.objects.filter(destination=dest).count()
            if trip_count > 0:
                popular_destinations.append({
                    'name': dest.name,
                    'trip_count': trip_count,
                    'destination': dest
                })
        
        # Sort by trip count and get top 5
        popular_destinations.sort(key=lambda x: x['trip_count'], reverse=True)
        context['popular_destinations'] = popular_destinations[:5]
        
        # Active users (users with most trips)
        active_users = []
        for user in CustomUser.objects.all():
            trip_count = TripPlan.objects.filter(user=user).count()
            if trip_count > 0:
                active_users.append({
                    'user': user,
                    'trip_count': trip_count,
                    'last_trip': TripPlan.objects.filter(user=user).order_by('-created_at').first()
                })
        
        # Sort by trip count and get top 10
        active_users.sort(key=lambda x: x['trip_count'], reverse=True)
        context['active_users'] = active_users[:10]
        
        return context

# ==================== CONTENT MANAGEMENT ====================
class AdminContentView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'users/admin_content.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get counts for each content type
        context['destinations_count'] = Destination.objects.count()
        context['hotels_count'] = Hotel.objects.count()
        context['flights_count'] = Flight.objects.count()
        context['buses_count'] = BusService.objects.count()
        context['cars_count'] = CarRental.objects.count()
        context['posts_count'] = Post.objects.count()
        
        # Recent content
        context['recent_destinations'] = Destination.objects.order_by('-created_at')[:5]
        context['recent_hotels'] = Hotel.objects.order_by('-created_at')[:5]
        context['recent_posts'] = Post.objects.order_by('-created_at')[:5]
        
        return context

class AdminDestinationsView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Destination
    template_name = 'users/admin_destinations.html'
    context_object_name = 'destinations'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Destination.objects.all().order_by('-created_at')
        
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(region__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_destinations'] = Destination.objects.count()
        
        # Calculate popular destinations based on trips
        popular_destinations = []
        for dest in Destination.objects.all():
            trip_count = TripPlan.objects.filter(destination=dest).count()
            if trip_count > 0:
                popular_destinations.append({
                    'destination': dest,
                    'trip_count': trip_count
                })
        
        popular_destinations.sort(key=lambda x: x['trip_count'], reverse=True)
        context['popular_destinations'] = popular_destinations[:5]
        
        return context

class AdminAddDestinationView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Destination
    form_class = DestinationForm
    template_name = 'users/admin_add_destination.html'
    success_url = reverse_lazy('users:admin_destinations')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Destination {self.object.name} added successfully!')
        return response

class AdminFlightsView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Flight
    template_name = 'users/admin_flights.html'
    context_object_name = 'flights'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Flight.objects.select_related('departure', 'arrival').order_by('-created_at')
        
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(airline__icontains=search) |
                Q(flight_number__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_flights'] = Flight.objects.count()
        context['active_flights'] = Flight.objects.filter(is_active=True).count()
        return context

class AdminAddFlightView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Flight
    form_class = FlightForm
    template_name = 'users/admin_add_flight.html'
    success_url = reverse_lazy('users:admin_flights')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Flight {self.object.flight_number} added successfully!')
        return response

class AdminBusesView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = BusService
    template_name = 'users/admin_buses.html'
    context_object_name = 'buses'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = BusService.objects.select_related('departure', 'arrival').order_by('-created_at')
        
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(company__icontains=search) |
                Q(bus_type__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_buses'] = BusService.objects.count()
        context['active_buses'] = BusService.objects.filter(is_active=True).count()
        return context

class AdminAddBusView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = BusService
    form_class = BusServiceForm
    template_name = 'users/admin_add_bus.html'
    success_url = reverse_lazy('users:admin_buses')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Bus service {self.object.company} added successfully!')
        return response

# ==================== SYSTEM SETTINGS ====================
class AdminSystemSettingsView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'users/admin_system_settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # System statistics
        context['total_users'] = CustomUser.objects.count()
        context['total_trips'] = TripPlan.objects.count()
        context['total_destinations'] = Destination.objects.count()
        context['total_hotels'] = Hotel.objects.count()
        context['total_flights'] = Flight.objects.count()
        context['total_buses'] = BusService.objects.count()
        
        # Database info
        import sqlite3
        import os
        from django.conf import settings
        
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
            context['db_size'] = f"{db_size:.2f} MB"
            
            # Get table counts
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            context['table_count'] = len(tables)
            conn.close()
        
        return context

class AdminDatabaseBackupView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'users/admin_database_backup.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # List existing backups
        import os
        import glob
        from django.conf import settings
        
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        backups = []
        backup_files = glob.glob(os.path.join(backup_dir, '*.sqlite3'))
        for file in backup_files:
            size = os.path.getsize(file) / (1024 * 1024)
            backups.append({
                'name': os.path.basename(file),
                'size': f"{size:.2f} MB",
                'date': datetime.fromtimestamp(os.path.getmtime(file))
            })
        
        context['backups'] = sorted(backups, key=lambda x: x['date'], reverse=True)
        return context

# ==================== SIMPLIFIED VIEWS ====================
def admin_trip_content_view(request):
    messages.info(request, 'Redirecting to Django admin for trip content management')
    return redirect('/admin/planner/tripplan/')
# C:\Users\ASUS\MyanmarTravelPlanner\users\views_admin.py
# Add this new view
@user_passes_test(is_admin)
def admin_add_hotel_with_map(request):
    """Add new hotel with Google Maps location picker"""
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save()
            messages.success(request, f'Hotel "{hotel.name}" added successfully at selected location!')
            return redirect('users:admin_hotels')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HotelForm()
    
    destinations = Destination.objects.all()
    context = {
        'form': form,
        'destinations': destinations,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }
    return render(request, 'users/admin_add_hotel_maps.html', context)

# Update the existing admin_hotels view to link to new template
@user_passes_test(is_admin)
def admin_hotels(request):
    """Admin hotel management view"""
    hotels = Hotel.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        hotels = hotels.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by destination
    destination_id = request.GET.get('destination', '')
    if destination_id:
        hotels = hotels.filter(destination_id=destination_id)
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        hotels = hotels.filter(category=category)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        hotels = hotels.filter(is_active=True)
    elif status == 'inactive':
        hotels = hotels.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(hotels, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_hotels = Hotel.objects.count()
    active_hotels = Hotel.objects.filter(is_active=True).count()
    destinations = Destination.objects.all()
    
    context = {
        'hotels': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'total_hotels': total_hotels,
        'active_hotels': active_hotels,
        'destinations': destinations,
    }
    
    return render(request, 'users/admin_hotels.html', context)