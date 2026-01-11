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
from django.conf import settings
import json
from datetime import datetime

from .models import CustomUser
from planner.models import TripPlan, Destination, Hotel, Flight, BusService, CarRental, Airline
from posts.models import Post
from .forms_admin import (
    CustomUserAdminForm,
    AdminAddDestinationForm, AdminEditDestinationForm,
    AdminAddHotelForm, AdminEditHotelForm,
    AdminAddFlightForm, AdminEditFlightForm,
    AdminAddBusForm, AdminEditBusForm,
    AdminAddCarForm, AdminEditCarForm,
    AdminAddAirlineForm, AdminEditAirlineForm,
    HotelFormWithMap
)

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

# ==================== HOTEL MANAGEMENT ====================
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
    """Add new hotel with manual coordinate input"""
    if request.method == 'POST':
        form = AdminAddHotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save()
            messages.success(request, f'Hotel "{hotel.name}" added successfully!')
            return redirect('users:admin_hotels')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminAddHotelForm()
    
    destinations = Destination.objects.all()
    context = {
        'form': form,
        'destinations': destinations,
    }
    return render(request, 'users/admin_add_hotel.html', context)

@user_passes_test(is_admin)
def admin_add_hotel_with_map(request):
    """Add new hotel with map location picker"""
    if request.method == 'POST':
        form = HotelFormWithMap(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save()
            messages.success(request, f'Hotel "{hotel.name}" added successfully with location!')
            return redirect('users:admin_hotels')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HotelFormWithMap()
    
    destinations = Destination.objects.all()
    context = {
        'form': form,
        'destinations': destinations,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    return render(request, 'users/admin_add_hotel_maps.html', context)

@user_passes_test(is_admin)
def admin_edit_hotel(request, hotel_id):
    """Edit hotel view"""
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    if request.method == 'POST':
        form = AdminEditHotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, f'Hotel "{hotel.name}" updated successfully!')
            return redirect('users:admin_hotels')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminEditHotelForm(instance=hotel)
    
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

# ==================== USER MANAGEMENT ====================
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

# ==================== AJAX USER FUNCTIONS ====================
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

# ==================== DESTINATION MANAGEMENT ====================
@user_passes_test(is_admin)
def admin_destinations(request):
    """Admin destinations view"""
    destinations = Destination.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        destinations = destinations.filter(
            Q(name__icontains=search_query) |
            Q(region__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by type
    dest_type = request.GET.get('type', '')
    if dest_type:
        destinations = destinations.filter(type=dest_type)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        destinations = destinations.filter(is_active=True)
    elif status == 'inactive':
        destinations = destinations.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(destinations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_destinations = Destination.objects.count()
    active_destinations = Destination.objects.filter(is_active=True).count()
    
    # Calculate popular destinations based on trips
    popular_destinations = []
    for dest in Destination.objects.all():
        trip_count = TripPlan.objects.filter(destination=dest).count()
        hotel_count = Hotel.objects.filter(destination=dest).count()
        if trip_count > 0 or hotel_count > 0:
            popular_destinations.append({
                'destination': dest,
                'trip_count': trip_count,
                'hotel_count': hotel_count
            })
    
    popular_destinations.sort(key=lambda x: x['trip_count'], reverse=True)
    
    context = {
        'destinations': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'total_destinations': total_destinations,
        'active_destinations': active_destinations,
        'popular_destinations': popular_destinations[:5],
        'destination_types': Destination._meta.get_field('type').choices,
    }
    
    return render(request, 'users/admin_destinations.html', context)

@user_passes_test(is_admin)
def admin_add_destination(request):
    """Add new destination with coordinates"""
    if request.method == 'POST':
        form = AdminAddDestinationForm(request.POST, request.FILES)
        if form.is_valid():
            destination = form.save()
            messages.success(request, f'Destination "{destination.name}" added successfully!')
            return redirect('users:admin_destinations')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminAddDestinationForm()
    
    context = {
        'form': form,
        'title': 'Add Destination'
    }
    return render(request, 'users/admin_add_destination.html', context)

@user_passes_test(is_admin)
def admin_edit_destination(request, destination_id):
    """Edit destination view"""
    destination = get_object_or_404(Destination, id=destination_id)
    
    if request.method == 'POST':
        form = AdminEditDestinationForm(request.POST, request.FILES, instance=destination)
        if form.is_valid():
            form.save()
            messages.success(request, f'Destination "{destination.name}" updated successfully!')
            return redirect('users:admin_destinations')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminEditDestinationForm(instance=destination)
    
    context = {
        'form': form,
        'destination': destination,
        'title': f'Edit {destination.name}'
    }
    return render(request, 'users/admin_add_destination.html', context)

@user_passes_test(is_admin)
def admin_delete_destination(request, destination_id):
    """Delete destination view (AJAX)"""
    if request.method == 'POST':
        try:
            destination = Destination.objects.get(id=destination_id)
            destination_name = destination.name
            
            # Check if destination has hotels or trips
            hotel_count = Hotel.objects.filter(destination=destination).count()
            trip_count = TripPlan.objects.filter(destination=destination).count()
            
            if hotel_count > 0 or trip_count > 0:
                return JsonResponse({
                    'success': False,
                    'error': f'Cannot delete destination with {hotel_count} hotels and {trip_count} trips'
                })
            
            destination.delete()
            return JsonResponse({'success': True, 'message': f'Destination "{destination_name}" deleted successfully!'})
        except Destination.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Destination not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

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

@user_passes_test(is_admin)
def admin_trip_details(request, trip_id):
    """View trip details"""
    trip = get_object_or_404(TripPlan, id=trip_id)
    
    context = {
        'trip': trip,
        'nights': trip.calculate_nights(),
        'total_cost': trip.get_total_cost(),
    }
    
    return render(request, 'users/admin_trip_details.html', context)

# ==================== FLIGHT MANAGEMENT ====================
@user_passes_test(is_admin)
def admin_flights(request):
    """Admin flights view"""
    flights = Flight.objects.select_related('departure', 'arrival').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        flights = flights.filter(
            Q(airline__icontains=search_query) |
            Q(flight_number__icontains=search_query) |
            Q(departure__name__icontains=search_query) |
            Q(arrival__name__icontains=search_query)
        )
    
    # Filter by category
    category = request.GET.get('category', '')
    if category:
        flights = flights.filter(category=category)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        flights = flights.filter(is_active=True)
    elif status == 'inactive':
        flights = flights.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(flights, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_flights = Flight.objects.count()
    active_flights = Flight.objects.filter(is_active=True).count()
    
    context = {
        'flights': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'total_flights': total_flights,
        'active_flights': active_flights,
        'flight_categories': Flight._meta.get_field('category').choices,
    }
    
    return render(request, 'users/admin_flights.html', context)

@user_passes_test(is_admin)
def admin_add_flight(request):
    """Add new flight"""
    if request.method == 'POST':
        form = AdminAddFlightForm(request.POST, request.FILES)
        if form.is_valid():
            flight = form.save()
            messages.success(request, f'Flight {flight.airline} {flight.flight_number} added successfully!')
            return redirect('users:admin_flights')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminAddFlightForm()
    
    context = {
        'form': form,
        'title': 'Add Flight'
    }
    return render(request, 'users/admin_add_flight.html', context)

@user_passes_test(is_admin)
def admin_edit_flight(request, flight_id):
    """Edit flight view"""
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        form = AdminEditFlightForm(request.POST, request.FILES, instance=flight)
        if form.is_valid():
            form.save()
            messages.success(request, f'Flight {flight.airline} {flight.flight_number} updated successfully!')
            return redirect('users:admin_flights')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminEditFlightForm(instance=flight)
    
    context = {
        'form': form,
        'flight': flight,
        'title': f'Edit Flight {flight.flight_number}'
    }
    return render(request, 'users/admin_add_flight.html', context)

# ==================== BUS MANAGEMENT ====================
@user_passes_test(is_admin)
def admin_buses(request):
    """Admin buses view"""
    buses = BusService.objects.select_related('departure', 'arrival').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        buses = buses.filter(
            Q(company__icontains=search_query) |
            Q(bus_number__icontains=search_query) |
            Q(departure__name__icontains=search_query) |
            Q(arrival__name__icontains=search_query)
        )
    
    # Filter by bus type
    bus_type = request.GET.get('bus_type', '')
    if bus_type:
        buses = buses.filter(bus_type=bus_type)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        buses = buses.filter(is_active=True)
    elif status == 'inactive':
        buses = buses.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(buses, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_buses = BusService.objects.count()
    active_buses = BusService.objects.filter(is_active=True).count()
    
    context = {
        'buses': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'total_buses': total_buses,
        'active_buses': active_buses,
        'bus_types': BusService._meta.get_field('bus_type').choices,
    }
    
    return render(request, 'users/admin_buses.html', context)

@user_passes_test(is_admin)
def admin_add_bus(request):
    """Add new bus service"""
    if request.method == 'POST':
        form = AdminAddBusForm(request.POST, request.FILES)
        if form.is_valid():
            bus = form.save()
            messages.success(request, f'Bus service {bus.company} added successfully!')
            return redirect('users:admin_buses')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminAddBusForm()
    
    context = {
        'form': form,
        'title': 'Add Bus Service'
    }
    return render(request, 'users/admin_add_bus.html', context)

@user_passes_test(is_admin)
def admin_edit_bus(request, bus_id):
    """Edit bus service view"""
    bus = get_object_or_404(BusService, id=bus_id)
    
    if request.method == 'POST':
        form = AdminEditBusForm(request.POST, request.FILES, instance=bus)
        if form.is_valid():
            form.save()
            messages.success(request, f'Bus service {bus.company} updated successfully!')
            return redirect('users:admin_buses')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminEditBusForm(instance=bus)
    
    context = {
        'form': form,
        'bus': bus,
        'title': f'Edit Bus Service {bus.bus_number}'
    }
    return render(request, 'users/admin_add_bus.html', context)

# ==================== CAR RENTAL MANAGEMENT ====================
@user_passes_test(is_admin)
def admin_cars(request):
    """Admin car rentals view"""
    cars = CarRental.objects.select_related('location').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        cars = cars.filter(
            Q(company__icontains=search_query) |
            Q(car_model__icontains=search_query) |
            Q(location__name__icontains=search_query)
        )
    
    # Filter by car type
    car_type = request.GET.get('car_type', '')
    if car_type:
        cars = cars.filter(car_type=car_type)
    
    # Filter by availability
    available = request.GET.get('available', '')
    if available == 'available':
        cars = cars.filter(is_available=True)
    elif available == 'unavailable':
        cars = cars.filter(is_available=False)
    
    # Pagination
    paginator = Paginator(cars, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_cars = CarRental.objects.count()
    available_cars = CarRental.objects.filter(is_available=True).count()
    
    context = {
        'cars': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'total_cars': total_cars,
        'available_cars': available_cars,
        'car_types': CarRental._meta.get_field('car_type').choices,
    }
    
    return render(request, 'users/admin_cars.html', context)

@user_passes_test(is_admin)
def admin_add_car(request):
    """Add new car rental"""
    if request.method == 'POST':
        form = AdminAddCarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save()
            messages.success(request, f'Car rental {car.company} - {car.car_model} added successfully!')
            return redirect('users:admin_cars')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminAddCarForm()
    
    context = {
        'form': form,
        'title': 'Add Car Rental'
    }
    return render(request, 'users/admin_add_car.html', context)

@user_passes_test(is_admin)
def admin_edit_car(request, car_id):
    """Edit car rental view"""
    car = get_object_or_404(CarRental, id=car_id)
    
    if request.method == 'POST':
        form = AdminEditCarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, f'Car rental {car.company} - {car.car_model} updated successfully!')
            return redirect('users:admin_cars')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminEditCarForm(instance=car)
    
    context = {
        'form': form,
        'car': car,
        'title': f'Edit Car Rental {car.car_model}'
    }
    return render(request, 'users/admin_add_car.html', context)

# ==================== AIRLINE MANAGEMENT ====================
@user_passes_test(is_admin)
def admin_airlines(request):
    """Admin airlines view"""
    airlines = Airline.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        airlines = airlines.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        airlines = airlines.filter(is_active=True)
    elif status == 'inactive':
        airlines = airlines.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(airlines, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_airlines = Airline.objects.count()
    active_airlines = Airline.objects.filter(is_active=True).count()
    default_domestic = Airline.objects.filter(is_default_for_domestic=True).count()
    
    context = {
        'airlines': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'total_airlines': total_airlines,
        'active_airlines': active_airlines,
        'default_domestic': default_domestic,
    }
    
    return render(request, 'users/admin_airlines.html', context)

@user_passes_test(is_admin)
def admin_add_airline(request):
    """Add new airline"""
    if request.method == 'POST':
        form = AdminAddAirlineForm(request.POST, request.FILES)
        if form.is_valid():
            airline = form.save()
            messages.success(request, f'Airline {airline.name} ({airline.code}) added successfully!')
            return redirect('users:admin_airlines')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminAddAirlineForm()
    
    context = {
        'form': form,
        'title': 'Add Airline'
    }
    return render(request, 'users/admin_add_airline.html', context)

@user_passes_test(is_admin)
def admin_edit_airline(request, airline_id):
    """Edit airline view"""
    airline = get_object_or_404(Airline, id=airline_id)
    
    if request.method == 'POST':
        form = AdminEditAirlineForm(request.POST, request.FILES, instance=airline)
        if form.is_valid():
            form.save()
            messages.success(request, f'Airline {airline.name} ({airline.code}) updated successfully!')
            return redirect('users:admin_airlines')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminEditAirlineForm(instance=airline)
    
    context = {
        'form': form,
        'airline': airline,
        'title': f'Edit Airline {airline.name}'
    }
    return render(request, 'users/admin_add_airline.html', context)

# ==================== CONTENT MANAGEMENT ====================
@user_passes_test(is_admin)
def admin_content(request):
    """Admin content dashboard"""
    # Statistics
    context = {
        'destinations_count': Destination.objects.count(),
        'hotels_count': Hotel.objects.count(),
        'flights_count': Flight.objects.count(),
        'buses_count': BusService.objects.count(),
        'cars_count': CarRental.objects.count(),
        'airlines_count': Airline.objects.count(),
        'posts_count': Post.objects.count(),
        
        # Recent content
        'recent_destinations': Destination.objects.order_by('-created_at')[:5],
        'recent_hotels': Hotel.objects.order_by('-created_at')[:5],
        'recent_flights': Flight.objects.order_by('-created_at')[:5],
        'recent_buses': BusService.objects.order_by('-created_at')[:5],
        'recent_posts': Post.objects.order_by('-created_at')[:5],
    }
    
    return render(request, 'users/admin_content.html', context)

# ==================== SYSTEM SETTINGS ====================
@user_passes_test(is_admin)
def admin_system_settings(request):
    """System settings view"""
    # System statistics
    context = {
        'total_users': CustomUser.objects.count(),
        'total_trips': TripPlan.objects.count(),
        'total_destinations': Destination.objects.count(),
        'total_hotels': Hotel.objects.count(),
        'total_flights': Flight.objects.count(),
        'total_buses': BusService.objects.count(),
        'total_cars': CarRental.objects.count(),
        'total_airlines': Airline.objects.count(),
        'total_posts': Post.objects.count(),
    }
    
    # Database info
    import sqlite3
    import os
    
    db_path = settings.DATABASES['default']['NAME']
    if os.path.exists(db_path):
        db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
        context['db_size'] = f"{db_size:.2f} MB"
        
        # Get table counts
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            context['table_count'] = len(tables)
            conn.close()
        except:
            context['table_count'] = 'N/A'
    
    return render(request, 'users/admin_system_settings.html', context)

@user_passes_test(is_admin)
def admin_database_backup(request):
    """Database backup view"""
    # List existing backups
    import os
    import glob
    
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
    
    context = {
        'backups': sorted(backups, key=lambda x: x['date'], reverse=True)
    }
    return render(request, 'users/admin_database_backup.html', context)

# ==================== SIMPLIFIED VIEWS ====================
@user_passes_test(is_admin)
def admin_trip_content_view(request):
    """Redirect to Django admin for trip content management"""
    messages.info(request, 'Redirecting to Django admin for trip content management')
    return redirect('/admin/planner/tripplan/')