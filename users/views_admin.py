from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model  # Add this line
from planner.models import TripPlan, Destination
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.conf import settings
import json
from planner.models_room import Room, RoomType, RoomBooking
from django.http import JsonResponse
from django import forms
from datetime import datetime
from .models import CustomUser, SystemSettings
from .forms_admin import AdminUserCreationForm 

from .models import CustomUser
from planner.models import TripPlan, Destination, Hotel, Flight, BusService, CarRental, Airline, TransportSchedule
from posts.models import Post
from .forms_admin import (
    CustomUserAdminForm,
    AdminAddDestinationForm, AdminEditDestinationForm,  # ADD THIS
     AdminAddHotelFormWithMap,
    AdminAddHotelForm, AdminEditHotelForm,
    AdminAddFlightForm, AdminEditFlightForm,
    AdminAddBusForm, AdminEditBusForm,
    AdminAddCarForm, AdminEditCarForm,
    AdminAddAirlineForm, AdminEditAirlineForm,
    
   
)
# users/views_admin.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from django.utils import timezone
from planner.models import TripPlan, Destination
User = get_user_model()
# Add these imports if not already present
from django.http import JsonResponse
import json

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser or u.user_type == 'admin')
def admin_toggle_destination_active(request, destination_id):
    """Toggle destination active status"""
    if request.method == 'POST':
        try:
            destination = Destination.objects.get(id=destination_id)
            destination.is_active = not destination.is_active
            destination.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Destination "{destination.name}" is now {"active" if destination.is_active else "inactive"}',
                'is_active': destination.is_active
            })
        except Destination.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Destination not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser or u.user_type == 'admin')
def admin_delete_destination_ajax(request, destination_id):
    """Delete destination via AJAX"""
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
# In users/views_admin.py, update the admin_trip_list function:
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_user_roles(request):
    """User role management view - handles both GET and POST"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user_type = request.POST.get('user_type')
        action = request.POST.get('action')
        
        print(f"DEBUG: Received POST - user_id: {user_id}, user_type: {user_type}, action: {action}")
        
        if action == 'update_role' and user_id and user_type:
            try:
                user = CustomUser.objects.get(id=user_id)
                
                # Prevent modifying your own account
                if user == request.user:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False,
                            'error': 'Cannot modify your own role'
                        })
                    messages.error(request, 'Cannot modify your own role')
                else:
                    # Update user role
                    old_role = user.user_type
                    user.user_type = user_type
                    
                    # Update staff status based on role
                    if user_type == 'admin':
                        user.is_staff = True
                        user.is_superuser = True
                    else:
                        user.is_staff = False
                        user.is_superuser = False
                    
                    user.save()
                    
                    success_message = f'User {user.username} role changed from {old_role} to {user_type}'
                    print(f"DEBUG: {success_message}")
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': success_message
                        })
                    
                    messages.success(request, success_message)
                    
            except CustomUser.DoesNotExist:
                error_msg = 'User not found'
                print(f"DEBUG: {error_msg}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': error_msg})
                messages.error(request, error_msg)
            except Exception as e:
                error_msg = f'Error updating role: {str(e)}'
                print(f"DEBUG: {error_msg}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': error_msg})
                messages.error(request, error_msg)
        
        # If not AJAX, redirect back
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return redirect('users:admin_user_roles')
    
    # GET request - show the page
    users = CustomUser.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
        'user_types': CustomUser.USER_TYPE_CHOICES,
        'admin_count': users.filter(user_type='admin').count(),
        'user_count': users.filter(user_type='user').count(),
    }
    
    return render(request, 'users/admin_user_roles.html', context)
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_trip_list(request):
    """Admin view to list all trips with filtering"""
    # Get custom user model
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    trips = TripPlan.objects.all().select_related('user', 'destination').order_by('-created_at')
    
    # Apply filters
    status = request.GET.get('status')
    user_id = request.GET.get('user')
    destination_id = request.GET.get('destination')
    
    if status:
        trips = trips.filter(status=status)
    if user_id:
        trips = trips.filter(user_id=user_id)
    if destination_id:
        trips = trips.filter(destination_id=destination_id)
    
    # Get filter options - Use 'trips' instead of 'tripplan'
    all_users = User.objects.filter(trips__isnull=False).distinct()  # CHANGED: trips instead of tripplan
    destinations = Destination.objects.all()
    
    # Pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = request.GET.get('page', 1)
    paginator = Paginator(trips, 20)  # 20 trips per page
    
    try:
        trips_page = paginator.page(page)
    except PageNotAnInteger:
        trips_page = paginator.page(1)
    except EmptyPage:
        trips_page = paginator.page(paginator.num_pages)
    
    context = {
        'trips': trips_page,
        'all_users': all_users,
        'destinations': destinations,
        'is_paginated': True,
        'page_obj': trips_page,
    }
    
    return render(request, 'users/admin_trip_list.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_trip_detail(request, trip_id):
    """Admin view to see and manage a specific trip"""
    trip = get_object_or_404(TripPlan.objects.select_related('user', 'destination'), id=trip_id)
    
    if request.method == 'POST':
        # Handle status update
        new_status = request.POST.get('status')
        if new_status and new_status in ['draft', 'planning', 'booked', 'completed', 'cancelled']:
            trip.status = new_status
            trip.save()
            messages.success(request, f'Trip status updated to {new_status.capitalize()}')
            return redirect('users:admin_trip_detail', trip_id=trip.id)
        
        # Handle note update
        note = request.POST.get('note')
        if note:
            trip.notes = note
            trip.save()
            messages.success(request, 'Note updated successfully')
            return redirect('users:admin_trip_detail', trip_id=trip.id)
    
    # Calculate nights
    if trip.start_date and trip.end_date:
        nights = (trip.end_date - trip.start_date).days
    else:
        nights = 0
    
    context = {
        'trip': trip,
        'nights': nights,
        'days': nights + 1 if nights > 0 else 1,
    }
    
    return render(request, 'users/admin_trip_detail.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_delete_trip(request, trip_id):
    """Admin view to delete a trip"""
    if request.method == 'POST':
        trip = get_object_or_404(TripPlan, id=trip_id)
        trip.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Trip deleted successfully'})
        
        messages.success(request, 'Trip deleted successfully')
        return redirect('users:admin_trip_list')
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_update_trip_status(request, trip_id):
    """AJAX view to update trip status"""
    if request.method == 'POST':
        trip = get_object_or_404(TripPlan, id=trip_id)
        new_status = request.POST.get('status')
        
        if new_status and new_status in ['draft', 'planning', 'booked', 'completed', 'cancelled']:
            trip.status = new_status
            trip.save()
            return JsonResponse({'success': True, 'message': f'Status updated to {new_status}'})
        
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

# In users/views_admin.py, update the admin_trip_analytics function:
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_trip_analytics(request):
    """Admin analytics dashboard for trips"""
    # Get custom user model
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Basic statistics
    total_trips = TripPlan.objects.count()
    active_trips = TripPlan.objects.filter(
        Q(status='planning') | Q(status='booked')
    ).count()
    completed_trips = TripPlan.objects.filter(status='completed').count()
    
    # Calculate revenue (simplified - using budget field if exists)
    try:
        total_revenue = TripPlan.objects.filter(status__in=['booked', 'completed']).aggregate(
            total=Sum('budget')
        )['total'] or 0
    except:
        total_revenue = completed_trips * 500000  # Fallback calculation
    
    # Monthly trends (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_data = []
    
    for i in range(6):
        month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_trips = TripPlan.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end
        ).count()
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'trips': month_trips
        })
    
    monthly_data.reverse()  # Show oldest to newest
    
    # Popular destinations
    popular_destinations = Destination.objects.annotate(
        trip_count=Count('tripplan')  # This might also need to change
    ).order_by('-trip_count')[:5]
    
    # Active users - Use 'trips' instead of 'tripplan'
    active_users = User.objects.annotate(
        trip_count=Count('trips')  # CHANGED: trips instead of tripplan
    ).filter(trip_count__gt=0).order_by('-trip_count')[:10]
    
    context = {
        'total_trips': total_trips,
        'active_trips': active_trips,
        'completed_trips': completed_trips,
        'total_revenue': total_revenue,
        'monthly_data': monthly_data,
        'popular_destinations': popular_destinations,
        'active_users': active_users,
    }
    
    return render(request, 'users/admin_trip_analytics.html', context)

# =================== ADMIN CHECK ====================
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
    total_schedules = TransportSchedule.objects.count()
    
    # Recent activities
    recent_hotels = Hotel.objects.order_by('-created_at')[:5]
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    recent_trips = TripPlan.objects.select_related('user', 'destination').order_by('-created_at')[:5]
    recent_schedules = TransportSchedule.objects.select_related().order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_hotels': total_hotels,
        'total_trips': total_trips,
        'total_destinations': total_destinations,
        'total_flights': total_flights,
        'total_buses': total_buses,
        'total_schedules': total_schedules,
        'recent_hotels': recent_hotels,
        'recent_users': recent_users,
        'recent_trips': recent_trips,
        'recent_schedules': recent_schedules,
    }
    
    return render(request, 'users/admin_dashboard.html', context)

# ==================== HOTEL MANAGEMENT ====================
@user_passes_test(is_admin)
def admin_edit_trip(request, trip_id):
    """Edit trip view"""
    trip = get_object_or_404(TripPlan, id=trip_id)
    
    if request.method == 'POST':
        # Handle trip editing here
        # You'll need to create a form for this
        messages.success(request, f'Trip #{trip.id} updated successfully!')
        return redirect('users:admin_trip_list')
    
    # For now, redirect to the trip plan page
    return redirect('planner:plan_selection', trip_id=trip.id)

@user_passes_test(is_admin)
def admin_hotels(request):
    """Admin hotel management view"""
    hotels = Hotel.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        hotels = hotels.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(destination__name__icontains=search_query)  # Add destination name search
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

# C:\Users\ASUS\MyanmarTravelPlanner\users\views_admin.py

@user_passes_test(is_admin)
def admin_add_hotel(request):
    """Add new hotel with manual coordinate input and rooms"""
    if request.method == 'POST':
        form = AdminAddHotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save()
            
            # Handle room creation (same as in admin_add_hotel_with_map)
            room_numbers = request.POST.getlist('room_number')
            room_types = request.POST.getlist('room_type')
            floors = request.POST.getlist('floor')
            custom_prices = request.POST.getlist('custom_price')
            bed_types = request.POST.getlist('bed_type')
            square_feets = request.POST.getlist('square_feet')
            features_list = request.POST.getlist('features')
            has_windows = request.POST.getlist('has_window')
            has_balconies = request.POST.getlist('has_balcony')
            
            from planner.models_room import Room, RoomType
            from decimal import Decimal
            
            rooms_created = 0
            for i in range(len(room_numbers)):
                if room_numbers[i].strip():
                    try:
                        room_type = RoomType.objects.get(code=room_types[i])
                        
                        features = []
                        if features_list[i].strip():
                            features = [f.strip() for f in features_list[i].split(',') if f.strip()]
                        
                        custom_price = None
                        if custom_prices[i] and custom_prices[i].strip():
                            custom_price = Decimal(custom_prices[i])
                        
                        floor = 1
                        if floors[i] and floors[i].strip():
                            floor = int(floors[i])
                        
                        square_feet = None
                        if square_feets[i] and square_feets[i].strip():
                            square_feet = int(square_feets[i])
                        
                        Room.objects.create(
                            hotel=hotel,
                            room_type=room_type,
                            room_number=room_numbers[i],
                            floor=floor,
                            custom_price=custom_price,
                            features=features,
                            bed_type=bed_types[i] if i < len(bed_types) and bed_types[i] else 'Queen',
                            has_window=(has_windows[i] == 'yes') if i < len(has_windows) else True,
                            has_balcony=(has_balconies[i] == 'yes') if i < len(has_balconies) else False,
                            square_feet=square_feet,
                            is_active=True
                        )
                        rooms_created += 1
                    except Exception as e:
                        print(f"Error creating room: {e}")
            
            messages.success(request, f'Hotel "{hotel.name}" added successfully with {rooms_created} rooms!')
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
def admin_edit_user(request, user_id):
    """Edit user view - CUSTOM VERSION"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Prevent editing your own account to avoid accidental lockout
    if user == request.user:
        messages.warning(request, 'You cannot edit your own account from this page. Use your profile settings instead.')
        return redirect('users:admin_dashboard_users')
    
    if request.method == 'POST':
        form = CustomUserAdminForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user.username}" updated successfully!')
            return redirect('users:admin_dashboard_users')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserAdminForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'title': f'Edit User {user.username}'
    }
    return render(request, 'users/admin_edit_user.html', context)
# C:\Users\ASUS\MyanmarTravelPlanner\users\views_admin.py
# Update the admin_add_hotel_with_map function:

# C:\Users\ASUS\MyanmarTravelPlanner\users\views_admin.py
# Update the admin_add_hotel_with_map function:

# C:\Users\ASUS\MyanmarTravelPlanner\users\views_admin.py
# Update the admin_add_hotel_with_map function (around line 100):

# C:\Users\ASUS\MyanmarTravelPlanner\users\views_admin.py

# C:\Users\ASUS\MyanmarTravelPlanner\users\views_admin.py

@user_passes_test(is_admin)
def admin_add_hotel_with_map(request):
    """Add new hotel with map location picker and rooms"""
    if request.method == 'POST':
        form = AdminAddHotelFormWithMap(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save()
            
            # Handle room creation
            room_numbers = request.POST.getlist('room_number')
            room_types = request.POST.getlist('room_type')
            floors = request.POST.getlist('floor')
            custom_prices = request.POST.getlist('custom_price')
            bed_types = request.POST.getlist('bed_type')
            square_feets = request.POST.getlist('square_feet')
            features_list = request.POST.getlist('features')
            has_windows = request.POST.getlist('has_window')
            has_balconies = request.POST.getlist('has_balcony')
            
            from planner.models_room import Room, RoomType
            from decimal import Decimal
            
            rooms_created = 0
            for i in range(len(room_numbers)):
                if room_numbers[i].strip():
                    try:
                        room_type = RoomType.objects.get(code=room_types[i])
                        
                        # Parse features
                        features = []
                        if features_list[i].strip():
                            features = [f.strip() for f in features_list[i].split(',') if f.strip()]
                        
                        # Parse custom price
                        custom_price = None
                        if custom_prices[i] and custom_prices[i].strip():
                            custom_price = Decimal(custom_prices[i])
                        
                        # Parse floor
                        floor = 1
                        if floors[i] and floors[i].strip():
                            floor = int(floors[i])
                        
                        # Parse square feet
                        square_feet = None
                        if square_feets[i] and square_feets[i].strip():
                            square_feet = int(square_feets[i])
                        
                        Room.objects.create(
                            hotel=hotel,
                            room_type=room_type,
                            room_number=room_numbers[i],
                            floor=floor,
                            custom_price=custom_price,
                            features=features,
                            bed_type=bed_types[i] if i < len(bed_types) and bed_types[i] else 'Queen',
                            has_window=(has_windows[i] == 'yes') if i < len(has_windows) else True,
                            has_balcony=(has_balconies[i] == 'yes') if i < len(has_balconies) else False,
                            square_feet=square_feet,
                            is_active=True
                        )
                        rooms_created += 1
                    except RoomType.DoesNotExist:
                        print(f"Room type {room_types[i]} not found")
                    except Exception as e:
                        print(f"Error creating room: {e}")
            
            messages.success(request, f'Hotel "{hotel.name}" added successfully with {rooms_created} rooms!')
            return redirect('users:admin_hotels')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminAddHotelFormWithMap()
    
    destinations = Destination.objects.all()
    context = {
        'form': form,
        'destinations': destinations,
    }
    return render(request, 'users/admin_add_hotel_maps.html', context)
# C:\Users\ASUS\MyanmarTravelPlanner\users\views_admin.py

@user_passes_test(is_admin)
def admin_edit_hotel(request, hotel_id):
    """Edit hotel view - WITHOUT rooms displayed"""
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    if request.method == 'POST':
        form = AdminEditHotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, f'Hotel "{hotel.name}" updated successfully!')
            return redirect('users:admin_hotels')
        else:
            messages.error(request, 'Please correct the errors below.')
            # Print form errors for debugging
            print("Form errors:", form.errors)
    else:
        form = AdminEditHotelForm(instance=hotel)
    
    # Get room count for display
    from planner.models_room import Room
    room_count = Room.objects.filter(hotel=hotel).count()
    
    context = {
        'form': form,
        'hotel': hotel,
        'room_count': room_count,
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

# Replace the existing AdminAddUserView class with this:



class AdminAddUserView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = CustomUser
    form_class = AdminUserCreationForm  # Use the new form
    template_name = 'users/admin_add_user.html'
    success_url = reverse_lazy('users:admin_dashboard_users')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Add additional fields if needed
        form.fields['is_staff'] = forms.BooleanField(
            required=False,
            initial=False,
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            label='Staff Status',
            help_text='Designates whether this user can access the admin site.'
        )
        
        return form
    
    def form_valid(self, form):
        # Save the user (form.save() already handles password hashing)
        user = form.save()
        
        # Set staff status from form if superuser is editing
        if self.request.user.is_superuser and 'is_staff' in form.cleaned_data:
            user.is_staff = form.cleaned_data['is_staff']
            user.save()
        
        messages.success(self.request, f'User {user.username} created successfully!')
        
        # Handle "Save & Add Another"
        if 'add_another' in self.request.POST:
            return redirect('users:admin_add_user')
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New User'
        return context

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
        # DEBUG: Print all POST data
        print("\n" + "="*50)
        print("FORM SUBMISSION DEBUG")
        print("="*50)
        print("POST data:")
        for key, value in request.POST.items():
            print(f"  {key}: {value} (type: {type(value).__name__})")
        
        print("\nFILES data:")
        for key in request.FILES:
            print(f"  {key}: {request.FILES[key].name}")
        
        form = AdminAddDestinationForm(request.POST, request.FILES)
        
        # DEBUG: Check if form is valid
        if form.is_valid():
            print("\n✓ FORM IS VALID")
            print("Cleaned data:")
            for key, value in form.cleaned_data.items():
                print(f"  {key}: {value} (type: {type(value).__name__})")
            
            destination = form.save(commit=False)
            print(f"\n✓ Destination before save: type={destination.type}, name={destination.name}")
            
            # Handle parent creation if it's a string (new parent city/town)
            # Only for attractions - check the destination type
            if destination.type == 'attraction' and hasattr(destination, '_temp_parent_name') and destination._temp_parent_name:
                parent_name = destination._temp_parent_name
                print(f"\n✓ Parent temp name: {parent_name}")
                try:
                    # Try to find existing parent
                    parent = Destination.objects.get(
                        Q(name__iexact=parent_name) | 
                        Q(name__icontains=parent_name),
                        type__in=['city', 'town']
                    )
                    destination.parent = parent
                    print(f"✓ Found existing parent: {parent.name}")
                except Destination.DoesNotExist:
                    # Create new parent city/town
                    parent = Destination.objects.create(
                        name=parent_name.title(),
                        region=form.cleaned_data.get('region', ''),
                        type='town',
                        description=f"{parent_name.title()} is a town/city in Myanmar.",
                        is_active=True,
                        is_region=False
                    )
                    destination.parent = parent
                    print(f"✓ Created new parent: {parent.name}")
                    messages.info(request, f'Created new parent city/town: "{parent_name}"')
            
            destination.save()
            print(f"\n✓ Destination saved: {destination.name} (ID: {destination.id})")
            messages.success(request, f'Destination "{destination.name}" added successfully!')
            return redirect('users:admin_destinations')
        else:
            print("\n✗ FORM IS INVALID")
            print("Form errors:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
            print("\nForm data that caused errors:")
            for field in form.fields:
                if field in form.data:
                    print(f"  {field}: {form.data.get(field)}")
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
        print("\n" + "="*50)
        print("EDIT DESTINATION DEBUG")
        print("="*50)
        print("POST data:")
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        
        print("\nFILES data:")
        for key in request.FILES:
            print(f"  {key}: {request.FILES[key].name}")
        
        form = AdminEditDestinationForm(request.POST, request.FILES, instance=destination)
        
        if form.is_valid():
            print("\n✓ FORM IS VALID")
            destination = form.save(commit=False)
            
            # Handle parent creation if it's a string (new parent city/town)
            if hasattr(destination, '_temp_parent_name') and destination._temp_parent_name:
                parent_name = destination._temp_parent_name
                try:
                    # Try to find existing parent
                    parent = Destination.objects.get(
                        Q(name__iexact=parent_name) | 
                        Q(name__icontains=parent_name),
                        type__in=['city', 'town']
                    )
                    destination.parent = parent
                except Destination.DoesNotExist:
                    # Create new parent city/town
                    parent = Destination.objects.create(
                        name=parent_name.title(),
                        region=form.cleaned_data.get('region', destination.region),
                        type='town',
                        description=f"{parent_name.title()} is a town/city in Myanmar.",
                        is_active=True,
                        is_region=True
                    )
                    destination.parent = parent
                    messages.info(request, f'Created new parent city/town: "{parent_name}"')
            else:
                # If parent field is empty, set parent to None
                if not form.cleaned_data.get('parent'):
                    destination.parent = None
            
            destination.save()
            messages.success(request, f'Destination "{destination.name}" updated successfully!')
            return redirect('users:admin_destinations')
        else:
            print("\n✗ FORM IS INVALID")
            print("Form errors:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminEditDestinationForm(instance=destination)
    
    context = {
        'form': form,
        'destination': destination,
        'title': f'Edit {destination.name}'
    }
    return render(request, 'users/admin_edit_destination.html', context)
@user_passes_test(is_admin)
def admin_edit_city(request, destination_id):
    """Edit city/town destination"""
    destination = get_object_or_404(Destination, id=destination_id)
    
    if request.method == 'POST':
        print("\n" + "="*50)
        print("EDIT CITY/TOWN DEBUG")
        print("="*50)
        print("POST data:")
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        
        print("\nFILES data:")
        for key in request.FILES:
            print(f"  {key}: {request.FILES[key].name}")
        
        form = AdminEditDestinationForm(request.POST, request.FILES, instance=destination)
        
        if form.is_valid():
            print("\n✓ FORM IS VALID")
            destination = form.save(commit=False)
            destination.is_region = True  # Ensure cities/towns are regions
            destination.save()
            messages.success(request, f'City/Town "{destination.name}" updated successfully!')
            return redirect('users:admin_destinations')
        else:
            print("\n✗ FORM IS INVALID")
            print("Form errors:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminEditDestinationForm(instance=destination)
    
    context = {
        'form': form,
        'destination': destination,
        'title': f'Edit City/Town: {destination.name}'
    }
    return render(request, 'users/admin_edit_city.html', context)

@user_passes_test(is_admin)
def admin_edit_attraction(request, destination_id):
    """Edit attraction destination"""
    destination = get_object_or_404(Destination, id=destination_id)
    
    if request.method == 'POST':
        print("\n" + "="*50)
        print("EDIT ATTRACTION DEBUG")
        print("="*50)
        print("POST data:")
        for key, value in request.POST.items():
            print(f"  {key}: {value}")
        
        print("\nFILES data:")
        for key in request.FILES:
            print(f"  {key}: {request.FILES[key].name}")
        
        form = AdminEditDestinationForm(request.POST, request.FILES, instance=destination)
        
        if form.is_valid():
            print("\n✓ FORM IS VALID")
            destination = form.save(commit=False)
            destination.is_region = False  # Attractions are not regions
            
            # Handle parent creation if it's a string (new parent city/town)
            if hasattr(destination, '_temp_parent_name') and destination._temp_parent_name:
                parent_name = destination._temp_parent_name
                try:
                    # Try to find existing parent
                    parent = Destination.objects.get(
                        Q(name__iexact=parent_name) | 
                        Q(name__icontains=parent_name),
                        type__in=['city', 'town']
                    )
                    destination.parent = parent
                except Destination.DoesNotExist:
                    # Create new parent city/town
                    parent = Destination.objects.create(
                        name=parent_name.title(),
                        region=form.cleaned_data.get('region', destination.region),
                        type='town',
                        description=f"{parent_name.title()} is a town/city in Myanmar.",
                        is_active=True,
                        is_region=True
                    )
                    destination.parent = parent
                    messages.info(request, f'Created new parent city/town: "{parent_name}"')
            else:
                # If parent field is empty, set parent to None
                if not form.cleaned_data.get('parent'):
                    destination.parent = None
            
            destination.save()
            messages.success(request, f'Attraction "{destination.name}" updated successfully!')
            return redirect('users:admin_destinations')
        else:
            print("\n✗ FORM IS INVALID")
            print("Form errors:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminEditDestinationForm(instance=destination)
    
    context = {
        'form': form,
        'destination': destination,
        'title': f'Edit Attraction: {destination.name}'
    }
    return render(request, 'users/admin_edit_attraction.html', context)


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
        # Get custom user model
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        context['all_users'] = User.objects.all()
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
        # Get custom user model
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
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
        
        # Active users (users with most trips) - Use custom User model
        active_users = []
        for user in User.objects.all():
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
        'total_cost': trip.get_total_cost_in_mmk(),
    }
    
    return render(request, 'users/admin_trip_details.html', context)

# ==================== FLIGHT MANAGEMENT ====================
@user_passes_test(is_admin)
def admin_flights(request):
    """Admin flights view with AJAX statistics support"""
    # Check if it's an AJAX request for statistics only
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.GET.get('ajax_stats'):
        total_flights = Flight.objects.count()
        active_flights = Flight.objects.filter(is_active=True).count()
        # Count distinct airlines (not flight.airline but Flight objects with distinct airline codes)
        airline_count = Flight.objects.values('airline__name').distinct().count()
        
        return JsonResponse({
            'success': True,
            'total_flights': total_flights,
            'active_flights': active_flights,
            'airline_count': airline_count,
        })
    
    flights = Flight.objects.select_related('departure', 'arrival', 'airline').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        flights = flights.filter(
            Q(airline__name__icontains=search_query) |
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
    
    # Statistics - CALCULATE DYNAMICALLY
    total_flights = Flight.objects.count()
    active_flights = Flight.objects.filter(is_active=True).count()
    # Count distinct airlines
    airline_count = Flight.objects.values('airline__name').distinct().count()
    
    context = {
        'flights': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'total_flights': total_flights,
        'active_flights': active_flights,
        'airline_count': airline_count,
        'flight_categories': Flight._meta.get_field('category').choices,
    }
    
    return render(request, 'users/admin_flights.html', context)
# C:\Users\ASUS\MyanmarTravelPlanner\users\views_admin.py
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
    
    # Get all airlines for the dropdown
    airlines = Airline.objects.filter(is_active=True).order_by('name')
    
    context = {
        'form': form,
        'airlines': airlines,  # Add this line
        'title': 'Add Flight'
    }
    return render(request, 'users/admin_add_flight.html', context)
@user_passes_test(is_admin)
def admin_edit_flight(request, flight_id):
    """Edit flight view - CUSTOM VERSION"""
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
    # Change this line to use your custom template
    return render(request, 'users/admin_edit_flight.html', context)

@user_passes_test(is_admin)
def admin_delete_flight(request, flight_id):
    """Delete flight view (AJAX)"""
    if request.method == 'POST':
        try:
            flight = Flight.objects.get(id=flight_id)
            flight_name = f"{flight.airline} {flight.flight_number}"
            flight.delete()
            return JsonResponse({'success': True, 'message': f'Flight {flight_name} deleted successfully!'})
        except Flight.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Flight not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@user_passes_test(is_admin)
def admin_buses(request):
    """Admin buses view with AJAX statistics support"""
    # Check if it's an AJAX request for statistics only
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.GET.get('ajax_stats'):
        total_buses = BusService.objects.count()
        active_buses = BusService.objects.filter(is_active=True).count()
        # Count distinct bus types
        bus_type_count = BusService.objects.values('bus_type').distinct().count()
        
        return JsonResponse({
            'success': True,
            'total_buses': total_buses,
            'active_buses': active_buses,
            'bus_type_count': bus_type_count,
        })
    
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
    
    # Statistics - CALCULATE DYNAMICALLY
    total_buses = BusService.objects.count()
    active_buses = BusService.objects.filter(is_active=True).count()
    # Count distinct bus types
    bus_type_count = BusService.objects.values('bus_type').distinct().count()
    
    context = {
        'buses': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'total_buses': total_buses,
        'active_buses': active_buses,
        'bus_type_count': bus_type_count,
        'bus_types': BusService._meta.get_field('bus_type').choices,
    }
    
    return render(request, 'users/admin_buses.html', context)
# C:\Users\ASUS\MyanmarTravelPlanner\users\views_admin.py
# Update the admin_add_bus function:
@login_required
@user_passes_test(is_admin)
def admin_update_user_role_form(request):
    """Handle user role update from form submission"""
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user_type = request.POST.get('user_type')
        
        try:
            user = CustomUser.objects.get(id=user_id)
            
            # Prevent modifying your own account
            if user == request.user:
                messages.error(request, 'Cannot modify your own role')
                return redirect('users:admin_user_roles')
            
            # Update user role
            old_role = user.user_type
            user.user_type = user_type
            
            # Update staff status based on role
            if user_type == 'admin':
                user.is_staff = True
                user.is_superuser = True
            else:
                user.is_staff = False
                user.is_superuser = False
            
            user.save()
            
            messages.success(request, 
                f'User {user.username} role changed from {old_role} to {user_type}'
            )
            
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found')
        except Exception as e:
            messages.error(request, f'Error updating role: {str(e)}')
    
    return redirect('users:admin_user_roles')
@user_passes_test(is_admin)
def admin_add_bus(request):
    """Add new bus service with recurring schedules"""
    if request.method == 'POST':
        form = AdminAddBusForm(request.POST, request.FILES)
        if form.is_valid():
            bus = form.save()
            
            # Get schedule parameters
            schedule_type = request.POST.get('schedule_type', 'recurring')
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            num_days = int(request.POST.get('num_days', 30))
            
            # Create schedules
            schedules_created = create_bus_schedules(bus, schedule_type, start_date_str, end_date_str, num_days)
            
            messages.success(request, 
                f'Bus service "{bus.company}" added successfully with {schedules_created} schedule(s)!'
            )
            return redirect('users:admin_buses')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminAddBusForm()
    
    # Calculate default dates for template
    from datetime import date, timedelta
    today = date.today()
    next_month = today + timedelta(days=30)
    
    context = {
        'form': form,
        'title': 'Add Bus Service',
        'today': today,
        'next_month': next_month,
    }
    return render(request, 'users/admin_edit_bus.html', context)

def create_bus_schedules(bus, schedule_type, start_date_str, end_date_str=None, num_days=30):
    """Create transport schedules for a bus"""
    from datetime import datetime, timedelta
    import calendar
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        # Determine end date
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = start_date + timedelta(days=num_days - 1)
        
        schedules_created = 0
        
        # Generate dates based on schedule type
        current_date = start_date
        while current_date <= end_date:
            # Check if we should create schedule for this date
            create_schedule = False
            
            if schedule_type == 'single':
                create_schedule = (current_date == start_date)
            elif schedule_type == 'recurring':
                create_schedule = True
            elif schedule_type == 'weekdays':
                # Monday=0, Sunday=6
                create_schedule = current_date.weekday() < 5
            elif schedule_type == 'weekends':
                create_schedule = current_date.weekday() >= 5
            
            if create_schedule:
                # Create TransportSchedule
                schedule, created = TransportSchedule.objects.get_or_create(
                    transport_type='bus',
                    transport_id=bus.id,
                    travel_date=current_date,
                    defaults={
                        'departure_time': bus.departure_time,
                        'total_seats': bus.total_seats,
                        'available_seats': bus.available_seats,
                        'price': bus.price,
                        'is_active': bus.is_active,
                    }
                )
                if created:
                    schedules_created += 1
            
            current_date += timedelta(days=1)
        
        return schedules_created
        
    except Exception as e:
        print(f"Error creating bus schedules: {e}")
        return 0

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

# ==================== SCHEDULE MANAGEMENT ====================
@user_passes_test(is_admin)
def admin_schedules(request):
    """Admin transport schedules view"""
    schedules = TransportSchedule.objects.select_related().order_by('-travel_date', 'transport_type')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        schedules = schedules.filter(
            Q(transport_type__icontains=search_query) |
            Q(travel_date__icontains=search_query)
        )
    
    # Filter by transport type
    transport_type = request.GET.get('transport_type', '')
    if transport_type:
        schedules = schedules.filter(transport_type=transport_type)
    
    # Filter by date range
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        schedules = schedules.filter(travel_date__gte=date_from)
    if date_to:
        schedules = schedules.filter(travel_date__lte=date_to)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        schedules = schedules.filter(is_active=True)
    elif status == 'inactive':
        schedules = schedules.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(schedules, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_schedules = TransportSchedule.objects.count()
    active_schedules = TransportSchedule.objects.filter(is_active=True).count()
    upcoming_schedules = TransportSchedule.objects.filter(travel_date__gte=timezone.now().date()).count()
    
    context = {
        'schedules': page_obj,
        'page_obj': page_obj,
        'is_paginated': paginator.num_pages > 1,
        'total_schedules': total_schedules,
        'active_schedules': active_schedules,
        'upcoming_schedules': upcoming_schedules,
        'transport_types': [('flight', 'Flight'), ('bus', 'Bus'), ('car', 'Car')],
    }
    
    return render(request, 'users/admin_schedules.html', context)

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
        'schedules_count': TransportSchedule.objects.count(),
        'posts_count': Post.objects.count(),
        
        # Recent content
        'recent_destinations': Destination.objects.order_by('-created_at')[:5],
        'recent_hotels': Hotel.objects.order_by('-created_at')[:5],
        'recent_flights': Flight.objects.order_by('-created_at')[:5],
        'recent_buses': BusService.objects.order_by('-created_at')[:5],
        'recent_schedules': TransportSchedule.objects.order_by('-created_at')[:5],
        'recent_posts': Post.objects.order_by('-created_at')[:5],
    }
    
    return render(request, 'users/admin_content.html', context)

# ==================== SYSTEM SETTINGS ====================

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

# ==================== USERNAME CHANGE ====================
@login_required
@user_passes_test(is_admin)
def admin_system_settings(request):
    """Simple username and password change for admin"""
    
    # Get current user
    user = request.user
    context = {
        'username_error': None,
        'password_error': None,
        'new_username_value': '',
    }
    
    if request.method == 'POST':
        # Get form data
        new_username = request.POST.get('new_username', '').strip()
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Handle username change
        if new_username and current_password:
            # Validate new username
            if len(new_username) < 3:
                context['username_error'] = 'Username must be at least 3 characters'
            elif len(new_username) > 30:
                context['username_error'] = 'Username cannot exceed 30 characters'
            elif CustomUser.objects.filter(username=new_username).exclude(id=user.id).exists():
                context['username_error'] = 'Username already taken'
            # Verify current password
            elif not user.check_password(current_password):
                context['password_error'] = 'Current password is incorrect'
            else:
                # Update username
                old_username = user.username
                user.username = new_username
                user.save()
                messages.success(request, f'Username changed from "{old_username}" to "{new_username}"')
                context['new_username_value'] = ''
                return redirect('users:admin_system_settings')
            
            # Keep form value on error
            context['new_username_value'] = new_username
        
        # Handle password change
        elif new_password and current_password:
            # Validate new password
            if len(new_password) < 8:
                messages.error(request, 'New password must be at least 8 characters')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
            # Verify current password
            elif not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect')
            else:
                # Update password
                user.set_password(new_password)
                user.save()
                
                # Re-authenticate user
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                
                messages.success(request, 'Password changed successfully')
                return redirect('users:admin_system_settings')
    
    return render(request, 'users/admin_system_settings.html', context)
@user_passes_test(is_admin)
def admin_add_city(request):
    """Add new city/town destination"""
    if request.method == 'POST':
        form = AdminAddDestinationForm(request.POST, request.FILES)
        
        if form.is_valid():
            destination = form.save(commit=False)
            destination.type = request.POST.get('type', 'city')  # Ensure type is city/town
            destination.is_region = True  # Cities/towns are regions
            destination.save()
            
            messages.success(request, f'City/Town "{destination.name}" added successfully!')
            return redirect('users:admin_destinations')
        else:
            # Debug output
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        # Initialize form with default values for city/town
        form = AdminAddDestinationForm(initial={
            'type': 'city',
            'is_region': True,
            'is_active': True
        })
    
    context = {
        'form': form,
        'title': 'Add City/Town',
        'destination_type': 'city_town'  # Flag for template
    }
    return render(request, 'users/admin_add_destination.html', context)

@user_passes_test(is_admin)
def admin_add_attraction(request):
    """Add new attraction/place destination"""
    if request.method == 'POST':
        form = AdminAddDestinationForm(request.POST, request.FILES)
        
        if form.is_valid():
            destination = form.save(commit=False)
            destination.type = 'attraction'
            destination.is_region = False  # Attractions are not regions
            
            # Handle parent creation if it's a string (new parent city/town)
            if hasattr(destination, '_temp_parent_name') and destination._temp_parent_name:
                parent_name = destination._temp_parent_name
                try:
                    # Try to find existing parent
                    parent = Destination.objects.get(
                        Q(name__iexact=parent_name) | 
                        Q(name__icontains=parent_name),
                        type__in=['city', 'town']
                    )
                    destination.parent = parent
                except Destination.DoesNotExist:
                    # Create new parent city/town
                    parent = Destination.objects.create(
                        name=parent_name.title(),
                        region=form.cleaned_data.get('region', ''),
                        type='town',
                        description=f"{parent_name.title()} is a town/city in Myanmar.",
                        is_active=True,
                        is_region=True
                    )
                    destination.parent = parent
                    messages.info(request, f'Created new parent city/town: "{parent_name}"')
            
            destination.save()
            messages.success(request, f'Attraction "{destination.name}" added successfully!')
            return redirect('users:admin_destinations')
        else:
            # Debug output
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        # Initialize form with default values for attraction
        form = AdminAddDestinationForm(initial={
            'type': 'attraction',
            'is_region': False,
            'is_active': True
        })
    
    context = {
        'form': form,
        'title': 'Add Attraction/Place',
        'destination_type': 'attraction'  # Flag for template
    }
    return render(request, 'users/admin_add_destination.html', context)
# C:\Users\ASUS\MyanmarTravelPlanner\users\views_admin.py
# Add these new views for room management



@user_passes_test(is_admin)
def admin_hotel_rooms(request, hotel_id):
    """Manage rooms for a specific hotel"""
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = Room.objects.filter(hotel=hotel).order_by('floor', 'room_number')
    
    # Get all room types for the form
    room_types = RoomType.objects.all()
    
    context = {
        'hotel': hotel,
        'rooms': rooms,
        'room_types': room_types,
    }
    return render(request, 'users/admin_hotel_rooms.html', context)

@user_passes_test(is_admin)
def admin_add_room(request, hotel_id):
    """Add a new room to hotel (AJAX)"""
    if request.method == 'POST':
        try:
            hotel = get_object_or_404(Hotel, id=hotel_id)
            
            room_number = request.POST.get('room_number')
            room_type_code = request.POST.get('room_type')
            floor = request.POST.get('floor', 1)
            custom_price = request.POST.get('custom_price')
            bed_type = request.POST.get('bed_type', 'Queen')
            square_feet = request.POST.get('square_feet')
            features = request.POST.get('features', '')
            has_window = request.POST.get('has_window') == 'yes'
            has_balcony = request.POST.get('has_balcony') == 'yes'
            
            # Get room type
            room_type = RoomType.objects.get(code=room_type_code)
            
            # Parse features
            features_list = [f.strip() for f in features.split(',') if f.strip()] if features else []
            
            # Parse custom price
            custom_price_value = None
            if custom_price and custom_price.strip():
                from decimal import Decimal
                custom_price_value = Decimal(custom_price)
            
            # Check if room number already exists
            if Room.objects.filter(hotel=hotel, room_number=room_number).exists():
                return JsonResponse({
                    'success': False,
                    'error': f'Room {room_number} already exists in this hotel'
                })
            
            # Create room
            room = Room.objects.create(
                hotel=hotel,
                room_type=room_type,
                room_number=room_number,
                floor=int(floor) if floor else 1,
                custom_price=custom_price_value,
                features=features_list,
                bed_type=bed_type,
                has_window=has_window,
                has_balcony=has_balcony,
                square_feet=int(square_feet) if square_feet and square_feet.strip() else None,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Room {room_number} added successfully',
                'room': {
                    'id': room.id,
                    'room_number': room.room_number,
                    'room_type': room.room_type.name,
                    'floor': room.floor,
                    'bed_type': room.bed_type,
                    'custom_price': str(room.custom_price) if room.custom_price else '',
                    'has_window': room.has_window,
                    'has_balcony': room.has_balcony,
                }
            })
            
        except RoomType.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid room type'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@user_passes_test(is_admin)
def admin_edit_room(request, room_id):
    """Edit an existing room (AJAX)"""
    if request.method == 'POST':
        try:
            room = get_object_or_404(Room, id=room_id)
            
            room.room_number = request.POST.get('room_number', room.room_number)
            room_type_code = request.POST.get('room_type')
            if room_type_code:
                room.room_type = RoomType.objects.get(code=room_type_code)
            
            room.floor = int(request.POST.get('floor', room.floor))
            
            custom_price = request.POST.get('custom_price')
            if custom_price and custom_price.strip():
                from decimal import Decimal
                room.custom_price = Decimal(custom_price)
            else:
                room.custom_price = None
            
            room.bed_type = request.POST.get('bed_type', room.bed_type)
            
            square_feet = request.POST.get('square_feet')
            if square_feet and square_feet.strip():
                room.square_feet = int(square_feet)
            
            features = request.POST.get('features', '')
            room.features = [f.strip() for f in features.split(',') if f.strip()] if features else []
            
            room.has_window = request.POST.get('has_window') == 'yes'
            room.has_balcony = request.POST.get('has_balcony') == 'yes'
            room.is_active = request.POST.get('is_active') == 'yes'
            
            room.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Room {room.room_number} updated successfully'
            })
            
        except RoomType.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid room type'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@user_passes_test(is_admin)
def admin_delete_room(request, room_id):
    """Delete a room (AJAX)"""
    if request.method == 'POST':
        try:
            room = get_object_or_404(Room, id=room_id)
            room_number = room.room_number
            
            # Check if room has any bookings
            if RoomBooking.objects.filter(room=room).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot delete room with existing bookings'
                })
            
            room.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Room {room_number} deleted successfully'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})