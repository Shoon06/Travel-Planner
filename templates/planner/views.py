# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# COMPLETE FIXED FILE

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta, datetime
import json
from django.conf import settings
from .models import Destination, Hotel, Flight, BusService, CarRental, TripPlan
from .real_hotels_service import real_hotels_service

# ========== HELPER FUNCTIONS ==========
def calculate_nights(start_date, end_date):
    if start_date and end_date:
        return (end_date - start_date).days
    return 1

# ========== DASHBOARD VIEW ==========
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'planner/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        trips = TripPlan.objects.filter(user=user).order_by('-created_at')
        
        total_trips = trips.count()
        upcoming_trips = trips.filter(
            status__in=['draft', 'planning', 'booked'],
            start_date__gte=timezone.now().date()
        ).count()
        
        total_spent = 0
        for trip in trips.filter(status__in=['booked', 'completed']):
            total_spent += trip.get_total_cost()
        
        destinations_visited = trips.values('destination__name').distinct().count()
        
        context.update({
            'trips': trips,
            'total_trips': total_trips,
            'upcoming_trips': upcoming_trips,
            'total_spent': total_spent,
            'destinations_visited': destinations_visited,
        })
        
        return context

# ========== PLAN TRIP VIEW ==========
class PlanTripView(LoginRequiredMixin, View):
    template_name = 'planner/plan.html'
    
    def get(self, request):
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Initialize context with empty values
        context = {
            'today': today.strftime('%Y-%m-%d'),
            'tomorrow': tomorrow.strftime('%Y-%m-%d'),
            'origin_input': '',
            'selected_origin_id': '',
            'destination_input': '',
            'selected_destination_id': '',
            'selected_hotel_id': '',
            'selected_hotel_name': '',
            'selected_transport_id': '',
            'selected_transport_type': '',
            'selected_transport_name': '',
            'travelers': 2,  # Default value
        }
        
        # Try to get existing trip from database
        existing_trip = TripPlan.objects.filter(
            user=request.user,
            status__in=['draft', 'planning']
        ).first()
        
        if existing_trip:
            # Restore ALL data from existing trip
            if existing_trip.origin:
                context['origin_input'] = existing_trip.origin.name
                context['selected_origin_id'] = existing_trip.origin.id
            if existing_trip.destination:
                context['destination_input'] = existing_trip.destination.name
                context['selected_destination_id'] = existing_trip.destination.id
            if existing_trip.selected_hotel:
                context['selected_hotel_id'] = existing_trip.selected_hotel.id
                context['selected_hotel_name'] = existing_trip.selected_hotel.name
            if existing_trip.selected_transport:
                context['selected_transport_id'] = existing_trip.selected_transport.get('id', '')
                context['selected_transport_type'] = existing_trip.selected_transport.get('type', '')
                context['selected_transport_name'] = existing_trip.selected_transport.get('name', '')
            if existing_trip.start_date:
                context['today'] = existing_trip.start_date.strftime('%Y-%m-%d')
            if existing_trip.end_date:
                context['tomorrow'] = existing_trip.end_date.strftime('%Y-%m-%d')
            if existing_trip.travelers:
                context['travelers'] = existing_trip.travelers
        
        # Check for parameters from redirects (these should override)
        hotel_id = request.GET.get('hotel_id')
        if hotel_id:
            try:
                hotel = Hotel.objects.get(id=hotel_id)
                context['selected_hotel_id'] = hotel_id
                context['selected_hotel_name'] = hotel.name
            except Hotel.DoesNotExist:
                pass
        
        transport_id = request.GET.get('transport_id')
        if transport_id:
            context['selected_transport_id'] = transport_id
            context['selected_transport_type'] = request.GET.get('transport_type', '')
            context['selected_transport_name'] = request.GET.get('transport_name', '')
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.handle_ajax(request)
        return redirect('planner:plan')
    
    def handle_ajax(self, request):
        try:
            origin_id = request.POST.get('origin_id')
            destination_id = request.POST.get('destination_id')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            travelers = request.POST.get('travelers', 1)
            
            if not all([origin_id, destination_id, start_date, end_date]):
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            if origin_id == destination_id:
                return JsonResponse({'success': False, 'error': 'Origin and destination cannot be the same'})
            
            # Parse dates
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid date format'})
            
            if end_date_obj <= start_date_obj:
                return JsonResponse({'success': False, 'error': 'End date must be after start date'})
            
            # Get or create trip
            existing_trip = TripPlan.objects.filter(
                user=request.user,
                status__in=['draft', 'planning']
            ).first()
            
            if existing_trip:
                trip = existing_trip
                trip.origin_id = origin_id
                trip.destination_id = destination_id
                trip.start_date = start_date_obj
                trip.end_date = end_date_obj
                trip.travelers = travelers
                trip.status = 'planning'
            else:
                trip = TripPlan.objects.create(
                    user=request.user,
                    origin_id=origin_id,
                    destination_id=destination_id,
                    start_date=start_date_obj,
                    end_date=end_date_obj,
                    travelers=travelers,
                    budget_range='medium',
                    status='planning'
                )
            
            trip.save()
            
            return JsonResponse({
                'success': True,
                'trip_id': trip.id,
                'message': 'Trip saved successfully'
            })
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"AJAX Error: {error_details}")
            return JsonResponse({'success': False, 'error': str(e)})

# ========== DESTINATION SEARCH (AUTO-COMPLETE) ==========
class DestinationSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip().lower()
        
        if not query:
            return JsonResponse({'results': []})
        
        try:
            if len(query) == 1:
                destinations = Destination.objects.filter(
                    Q(name__istartswith=query) | Q(region__istartswith=query)
                ).order_by('name')[:20]
            else:
                destinations = Destination.objects.filter(
                    Q(name__icontains=query) | 
                    Q(region__icontains=query) |
                    Q(name__istartswith=query[:2]) |
                    Q(region__istartswith=query[:2])
                ).order_by('name')[:15]
            
            results = []
            for dest in destinations:
                results.append({
                    'id': dest.id,
                    'name': dest.name,
                    'region': dest.region,
                    'type': dest.get_type_display(),
                    'full_name': f"{dest.name}, {dest.region}",
                    'has_coordinates': bool(dest.latitude and dest.longitude)
                })
            
            if not results and len(query) >= 1:
                popular_destinations = ['Yangon', 'Mandalay', 'Bagan', 'Inle Lake', 'Naypyidaw']
                destinations = Destination.objects.filter(
                    name__in=popular_destinations
                ).order_by('name')[:5]
                
                for dest in destinations:
                    results.append({
                        'id': dest.id,
                        'name': dest.name,
                        'region': dest.region,
                        'type': dest.get_type_display(),
                        'full_name': f"{dest.name}, {dest.region}",
                        'has_coordinates': bool(dest.latitude and dest.longitude)
                    })
            
            return JsonResponse({'results': results})
            
        except Exception as e:
            print(f"Error searching destinations: {e}")
            return JsonResponse({'results': [], 'error': str(e)})

# ========== HOTEL SELECTION WITH MAP ==========
class SelectHotelWithMapView(LoginRequiredMixin, View):
    template_name = 'planner/select_hotel_map_real.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        nights = trip.calculate_nights()
        
        # Get hotels for this destination
        hotels = Hotel.objects.filter(
            destination=trip.destination,
            is_active=True
        ).order_by('price_per_night')
        
        # Prepare hotel data for template
        hotel_data = []
        for hotel in hotels:
            # Fix: Check if image exists before accessing .url
            image_url = ''
            if hotel.image and hasattr(hotel.image, 'url'):
                try:
                    image_url = hotel.image.url
                except:
                    image_url = ''
            
            hotel_data.append({
                'id': hotel.id,
                'name': hotel.name,
                'address': hotel.address,
                'latitude': float(hotel.latitude) if hotel.latitude else 0,
                'longitude': float(hotel.longitude) if hotel.longitude else 0,
                'price': float(hotel.price_per_night),
                'price_display': hotel.price_in_mmk(),
                'rating': float(hotel.rating),
                'review_count': hotel.review_count,
                'category': hotel.category,
                'category_display': hotel.get_category_display(),
                'amenities': hotel.amenities[:5],
                'is_real_hotel': hotel.is_real_hotel,
                'description': hotel.description[:100] + '...' if len(hotel.description) > 100 else (hotel.description or ''),
                'image_url': image_url,
                'phone_number': hotel.phone_number or '',
                'website': hotel.website or '',
                'gallery_images': getattr(hotel, 'gallery_images', []),
                'has_image': bool(image_url),
            })
        
        # Prepare hotel markers for map (JSON format)
        hotel_markers = []
        for hotel in hotels:
            if hotel.latitude and hotel.longitude:
                marker_data = {
                    'id': hotel.id,
                    'name': hotel.name,
                    'address': hotel.address,
                    'latitude': float(hotel.latitude),
                    'longitude': float(hotel.longitude),
                    'price': float(hotel.price_per_night),
                    'price_display': hotel.price_in_mmk(),
                    'rating': float(hotel.rating),
                    'review_count': hotel.review_count,
                    'category': hotel.category,
                    'category_display': hotel.get_category_display(),
                    'amenities': hotel.amenities[:5],
                    'is_real': hotel.is_real_hotel,
                    'is_our_hotel': hotel.created_by_admin,
                    'description': hotel.description[:100] + '...' if len(hotel.description) > 100 else (hotel.description or '')
                }
                hotel_markers.append(marker_data)
        
        # Determine center coordinates for map
        if trip.destination.latitude and trip.destination.longitude:
            center_lat = float(trip.destination.latitude)
            center_lng = float(trip.destination.longitude)
        else:
            # Default to Kalawe coordinates if destination doesn't have coordinates
            if 'Kalawe' in trip.destination.name:
                center_lat = 20.6333
                center_lng = 96.5667
            else:
                center_lat = 16.8409  # Yangon
                center_lng = 96.1735
        
        # Get all unique amenities for filtering
        all_amenities = set()
        for hotel in hotels:
            if hotel.amenities:
                all_amenities.update(hotel.amenities)
        all_amenities = sorted(list(all_amenities))
        
        context = {
            'trip': trip,
            'hotels': hotels,
            'hotel_markers': json.dumps(hotel_markers),
            'nights': nights,
            'center_lat': center_lat,
            'center_lng': center_lng,
            'all_amenities': all_amenities,
            'destination_name': trip.destination.name,
            'destination_id': trip.destination.id,
        }
        return render(request, self.template_name, context)

# ========== FILTER HOTELS VIEW ==========
class FilterHotelsView(View):
    def get(self, request, destination_id):
        destination = get_object_or_404(Destination, id=destination_id)
        
        category = request.GET.get('category', 'all')
        min_price = request.GET.get('min_price', 0)
        max_price = request.GET.get('max_price', 1000000)
        amenities = request.GET.getlist('amenities[]')
        sort_by = request.GET.get('sort_by', 'price_asc')
        
        try:
            min_price = float(min_price)
            max_price = float(max_price)
        except:
            min_price = 0
            max_price = 1000000
        
        hotels = Hotel.objects.filter(
            destination=destination,
            is_active=True
        ).exclude(latitude__isnull=True).exclude(longitude__isnull=True)
        
        if category != 'all':
            hotels = hotels.filter(category=category)
        
        hotels = hotels.filter(price_per_night__gte=min_price, price_per_night__lte=max_price)
        
        if amenities:
            for amenity in amenities:
                hotels = hotels.filter(amenities__contains=[amenity])
        
        if sort_by == 'price_asc':
            hotels = hotels.order_by('price_per_night')
        elif sort_by == 'price_desc':
            hotels = hotels.order_by('-price_per_night')
        elif sort_by == 'rating_desc':
            hotels = hotels.order_by('-rating')
        elif sort_by == 'name_asc':
            hotels = hotels.order_by('name')
        
        hotel_data = []
        for hotel in hotels:
            hotel_data.append({
                'id': hotel.id,
                'name': hotel.name,
                'address': hotel.address,
                'latitude': float(hotel.latitude) if hotel.latitude else None,
                'longitude': float(hotel.longitude) if hotel.longitude else None,
                'price': float(hotel.price_per_night),
                'price_display': hotel.price_in_mmk(),
                'rating': float(hotel.rating),
                'review_count': hotel.review_count,
                'category': hotel.category,
                'category_display': hotel.get_category_display(),
                'amenities': hotel.amenities,
                'description': hotel.description,
                'phone': hotel.phone_number or '',
                'website': hotel.website or '',
                'is_real_hotel': hotel.is_real_hotel,
                'has_image': bool(hotel.image)
            })
        
        return JsonResponse({
            'success': True,
            'hotels': hotel_data,
            'count': len(hotel_data)
        })
# Add this to your existing views.py file (around line 700-800)

# ========== PLAN SELECTION VIEW ==========
class PlanSelectionView(LoginRequiredMixin, View):
    """Display 3 travel plans (Cultural Explorer, Adventure Seeker, Relaxed Wanderer)"""
    template_name = 'planner/plan_selection.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        # Calculate trip duration
        nights = trip.calculate_nights()
        days = nights + 1 if nights > 0 else 3
        
        # Get destination for weather
        destination_name = trip.destination.name
        
        # Define the 3 travel plans
        plans = [
            {
                'id': 'cultural',
                'title': 'Cultural Explorer',
                'subtitle': 'Immerse yourself in Myanmar\'s rich cultural heritage',
                'category': 'Culture & History',
                'duration': f"{days} Days",
                'estimated_cost': 1250,
                'highlights': [
                    'Shwedagon Pagoda at sunrise',
                    'Colonial architecture walking tour',
                    'Traditional puppet show',
                    'Local tea house experience',
                    'Museum visits',
                    'Monastery meditation session'
                ],
                'icon': 'fas fa-landmark',
                'color': '#3498db',
                'days': self.generate_cultural_itinerary(trip, days),
                'total_activities': days * 4
            },
            {
                'id': 'adventure',
                'title': 'Adventure Seeker',
                'subtitle': 'Active exploration with outdoor activities',
                'category': 'Active & Adventurous',
                'duration': f"{days} Days",
                'estimated_cost': 1450,
                'highlights': [
                    'Circular train ride',
                    'Kayaking on Kandawgyi Lake',
                    'Hiking to hidden temples',
                    'Street food tour',
                    'Bicycle tour',
                    'Sunrise hot air balloon'
                ],
                'icon': 'fas fa-hiking',
                'color': '#2ecc71',
                'days': self.generate_adventure_itinerary(trip, days),
                'total_activities': days * 4
            },
            {
                'id': 'relaxed',
                'title': 'Relaxed Wanderer',
                'subtitle': 'Leisurely pace with ample free time',
                'category': 'Relaxed & Flexible',
                'duration': f"{days} Days",
                'estimated_cost': 1100,
                'highlights': [
                    'Spa and wellness sessions',
                    'Leisurely lake walks',
                    'Café hopping',
                    'Sunset photography spots',
                    'Massage therapy',
                    'Gardens and parks'
                ],
                'icon': 'fas fa-spa',
                'color': '#9b59b6',
                'days': self.generate_relaxed_itinerary(trip, days),
                'total_activities': days * 3  # Fewer activities for relaxed plan
            }
        ]
        
        context = {
            'trip': trip,
            'plans': plans,
            'destination': trip.destination,
            'days': days,
            'nights': nights,
            'destination_name': destination_name,
            'start_date': trip.start_date.strftime('%Y-%m-%d'),
            'end_date': trip.end_date.strftime('%Y-%m-%d'),
            'travelers': trip.travelers
        }
        
        return render(request, self.template_name, context)
    
    def generate_cultural_itinerary(self, trip, days):
        """Generate cultural itinerary"""
        itinerary = []
        
        for day in range(1, days + 1):
            day_activities = [
                {
                    'time': '09:00 AM',
                    'title': 'Shwedagon Pagoda Visit',
                    'location': 'Downtown Yangon',
                    'duration': '2 hours',
                    'description': 'Explore the golden pagoda at its morning glory',
                    'type': 'cultural',
                    'icon': 'fas fa-place-of-worship'
                },
                {
                    'time': '12:00 PM',
                    'title': 'Lunch at Feel Myanmar',
                    'location': 'Traditional Restaurant',
                    'duration': '1.5 hours',
                    'description': 'Authentic Myanmar cuisine',
                    'type': 'food',
                    'icon': 'fas fa-utensils'
                },
                {
                    'time': '02:00 PM',
                    'title': 'Bogyoke Market',
                    'location': 'Pabedan Township',
                    'duration': '2 hours',
                    'description': 'Shop for local crafts and souvenirs',
                    'type': 'shopping',
                    'icon': 'fas fa-shopping-bag'
                },
                {
                    'time': '05:00 PM',
                    'title': 'Traditional Puppet Show',
                    'location': 'Cultural Center',
                    'duration': '1.5 hours',
                    'description': 'Enjoy traditional Myanmar puppetry',
                    'type': 'entertainment',
                    'icon': 'fas fa-mask'
                }
            ]
            
            # Customize activities based on destination
            if 'Bagan' in trip.destination.name:
                day_activities[0]['title'] = 'Temple Sunrise Tour'
                day_activities[0]['location'] = 'Ancient Temples'
            
            itinerary.append({
                'day_number': day,
                'date': self.calculate_date(trip.start_date, day - 1),
                'activities': day_activities
            })
        
        return itinerary
    
    def generate_adventure_itinerary(self, trip, days):
        """Generate adventure itinerary"""
        itinerary = []
        
        for day in range(1, days + 1):
            day_activities = [
                {
                    'time': '07:00 AM',
                    'title': 'Circular Train Ride',
                    'location': 'Yangon Circular Railway',
                    'duration': '3 hours',
                    'description': 'Experience local life on the train',
                    'type': 'adventure',
                    'icon': 'fas fa-train'
                },
                {
                    'time': '11:00 AM',
                    'title': 'Street Food Walk',
                    'location': 'Local Markets',
                    'duration': '2 hours',
                    'description': 'Taste authentic street food',
                    'type': 'food',
                    'icon': 'fas fa-utensils'
                },
                {
                    'time': '02:00 PM',
                    'title': 'Kayaking on Lake',
                    'location': 'Kandawgyi Lake',
                    'duration': '2.5 hours',
                    'description': 'Paddle through scenic waters',
                    'type': 'water_sports',
                    'icon': 'fas fa-water'
                },
                {
                    'time': '06:00 PM',
                    'title': 'Sunset Hike',
                    'location': 'Nearby Hills',
                    'duration': '2 hours',
                    'description': 'Hike to a sunset viewpoint',
                    'type': 'hiking',
                    'icon': 'fas fa-mountain'
                }
            ]
            
            if 'Inle Lake' in trip.destination.name:
                day_activities[2]['title'] = 'Inle Lake Boat Tour'
                day_activities[2]['location'] = 'Inle Lake'
            
            itinerary.append({
                'day_number': day,
                'date': self.calculate_date(trip.start_date, day - 1),
                'activities': day_activities
            })
        
        return itinerary
    
    def generate_relaxed_itinerary(self, trip, days):
        """Generate relaxed itinerary"""
        itinerary = []
        
        for day in range(1, days + 1):
            day_activities = [
                {
                    'time': '10:00 AM',
                    'title': 'Late Breakfast',
                    'location': 'Hotel Restaurant',
                    'duration': '1.5 hours',
                    'description': 'Leisurely morning meal',
                    'type': 'food',
                    'icon': 'fas fa-coffee'
                },
                {
                    'time': '12:00 PM',
                    'title': 'Spa & Wellness',
                    'location': 'Wellness Center',
                    'duration': '2 hours',
                    'description': 'Relaxing massage and spa treatment',
                    'type': 'wellness',
                    'icon': 'fas fa-spa'
                },
                {
                    'time': '03:00 PM',
                    'title': 'Leisurely Lake Walk',
                    'location': 'Local Park/Lake',
                    'duration': '1.5 hours',
                    'description': 'Gentle walk around the lake',
                    'type': 'walking',
                    'icon': 'fas fa-walking'
                },
                {
                    'time': '05:00 PM',
                    'title': 'Sunset Photography',
                    'location': 'Scenic Viewpoint',
                    'duration': '1 hour',
                    'description': 'Capture beautiful sunset moments',
                    'type': 'photography',
                    'icon': 'fas fa-camera'
                }
            ]
            
            itinerary.append({
                'day_number': day,
                'date': self.calculate_date(trip.start_date, day - 1),
                'activities': day_activities
            })
        
        return itinerary
    
    def calculate_date(self, start_date, day_offset):
        """Calculate date for a specific day"""
        from datetime import timedelta
        return (start_date + timedelta(days=day_offset)).strftime('%Y-%m-%d')


# ========== SELECT PLAN VIEW ==========
class SelectPlanView(LoginRequiredMixin, View):
    """Handle plan selection and redirect to detailed itinerary"""
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        plan_id = request.POST.get('plan_id')
        
        if not plan_id:
            messages.error(request, 'Please select a plan.')
            return redirect('planner:plan_selection', trip_id=trip.id)
        
        # Save selected plan to trip
        trip.selected_plan = plan_id
        trip.save()
        
        return redirect('planner:itinerary_detail', trip_id=trip.id, plan_id=plan_id)
# ========== SAVE HOTEL VIEW ==========
class SaveHotelView(LoginRequiredMixin, View):
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        hotel_id = request.POST.get('hotel_id')
        
        if hotel_id:
            try:
                hotel = Hotel.objects.get(id=hotel_id)
                trip.selected_hotel = hotel
                trip.accommodation_type = hotel.category
                trip.save()
                
                # Build redirect URL with all parameters to preserve form data
                redirect_url = reverse('planner:plan')
                params = []
                
                # Add origin if exists
                if trip.origin:
                    params.append(f'origin_id={trip.origin.id}')
                    params.append(f'origin_name={trip.origin.name}')
                
                # Add destination if exists
                if trip.destination:
                    params.append(f'destination_id={trip.destination.id}')
                    params.append(f'destination_name={trip.destination.name}')
                
                # Add hotel
                params.append(f'hotel_id={hotel_id}')
                params.append(f'hotel_name={hotel.name}')
                
                # Add dates if they exist
                if trip.start_date:
                    params.append(f'start_date={trip.start_date.strftime("%Y-%m-%d")}')
                if trip.end_date:
                    params.append(f'end_date={trip.end_date.strftime("%Y-%m-%d")}')
                
                # Add travelers
                params.append(f'travelers={trip.travelers}')
                
                # Build final URL
                if params:
                    redirect_url += '?' + '&'.join(params)
                
                messages.success(request, f'Hotel {hotel.name} selected successfully!')
                return redirect(redirect_url)
                
            except Hotel.DoesNotExist:
                messages.error(request, 'Hotel not found.')
        
        messages.error(request, 'Please select a hotel')
        return redirect('planner:select_hotel_map', trip_id=trip.id)

# ========== REAL HOTELS VIEW ==========
class GetRealHotelsView(LoginRequiredMixin, View):
    def get(self, request):
        destination_id = request.GET.get('destination_id')
        latitude = request.GET.get('lat')
        longitude = request.GET.get('lng')
        
        try:
            if latitude and longitude:
                lat = float(latitude)
                lng = float(longitude)
            elif destination_id:
                destination = get_object_or_404(Destination, id=destination_id)
                if destination.latitude and destination.longitude:
                    lat = float(destination.latitude)
                    lng = float(destination.longitude)
                else:
                    geocoded = real_hotels_service.geocode_location(
                        f"{destination.name}, {destination.region}, Myanmar"
                    )
                    if geocoded:
                        lat = geocoded['latitude']
                        lng = geocoded['longitude']
                    else:
                        return JsonResponse({
                            'success': False,
                            'error': 'Could not determine location'
                        })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing location information'
                })
            
            real_hotels = real_hotels_service.search_nearby_hotels(lat, lng)
            
            return JsonResponse({
                'success': True,
                'hotels': real_hotels,
                'count': len(real_hotels),
                'location': {'lat': lat, 'lng': lng}
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

# ========== SIMPLE REDIRECT VIEWS ==========
class SelectHotelView(LoginRequiredMixin, View):
    def get(self, request, trip_id):
        return redirect('planner:select_hotel_map', trip_id=trip_id)

class SelectTransportCategoryView(LoginRequiredMixin, View):
    template_name = 'planner/transport_category.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        context = {'trip': trip}
        return render(request, self.template_name, context)

# In the SaveTransportView class, update the transport_name generation:

class SaveTransportView(LoginRequiredMixin, View):
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.POST.get('transport_type')
        transport_id = request.POST.get('transport_id')
        
        try:
            trip.transportation_preference = transport_type
            
            if transport_type == 'flight':
                transport = Flight.objects.get(id=transport_id)
                # Simplified naming - just show class
                if transport.category == 'low':
                    transport_name = "Economy Flight"
                elif transport.category == 'medium':
                    transport_name = "Business Flight"
                else:
                    transport_name = "Luxury Flight"
                    
            elif transport_type == 'bus':
                transport = BusService.objects.get(id=transport_id)
                # Simplified naming - just show class
                if transport.bus_type == 'standard':
                    transport_name = "Standard Bus"
                elif transport.bus_type == 'vip':
                    transport_name = "VIP Bus"
                else:
                    transport_name = "Luxury Bus"
                    
            elif transport_type == 'car':
                transport = CarRental.objects.get(id=transport_id)
                # Simplified naming - just show class
                if transport.car_type == 'economy':
                    transport_name = "Economy Car"
                elif transport.car_type == 'suv':
                    transport_name = "SUV"
                else:
                    transport_name = "Luxury Car"
                    
            else:
                messages.error(request, 'Invalid transport type.')
                return redirect('planner:select_transport_category', trip_id=trip.id)
            
            trip.selected_transport = {
                'type': transport_type,
                'id': transport_id,
                'name': transport_name,
                'price': transport.price_in_mmk() if hasattr(transport, 'price_in_mmk') else transport.price_per_day
            }
            trip.save()
            
            # Build redirect URL with all parameters
            redirect_url = reverse('planner:plan')
            params = []
            
            # Add all trip parameters
            if trip.origin:
                params.append(f'origin_id={trip.origin.id}')
                params.append(f'origin_name={trip.origin.name}')
            
            if trip.destination:
                params.append(f'destination_id={trip.destination.id}')
                params.append(f'destination_name={trip.destination.name}')
            
            # Add hotel if exists
            if trip.selected_hotel:
                params.append(f'hotel_id={trip.selected_hotel.id}')
                params.append(f'hotel_name={trip.selected_hotel.name}')
            
            # Add transport
            params.append(f'transport_id={transport_id}')
            params.append(f'transport_type={transport_type}')
            params.append(f'transport_name={transport_name}')
            
            # Add dates
            if trip.start_date:
                params.append(f'start_date={trip.start_date.strftime("%Y-%m-%d")}')
            if trip.end_date:
                params.append(f'end_date={trip.end_date.strftime("%Y-%m-%d")}')
            
            # Add travelers
            params.append(f'travelers={trip.travelers}')
            
            # Build final URL
            if params:
                redirect_url += '?' + '&'.join(params)
            
            return redirect(redirect_url)
            
        except Exception as e:
            messages.error(request, f'Error saving transport: {str(e)}')
            return redirect('planner:select_transport_category', trip_id=trip.id)

# ========== SELECT TRANSPORT VIEW ==========
class SelectTransportView(LoginRequiredMixin, View):
    template_name = 'planner/transport_list.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.GET.get('type', 'flight')
        budget_filter = request.GET.get('budget', 'all')
        
        transport_items = []
        
        if transport_type == 'flight':
            items = Flight.objects.filter(
                departure=trip.origin,
                arrival=trip.destination,
                is_active=True
            )
            
            if budget_filter == 'low':
                items = items.filter(price__lt=50000)
            elif budget_filter == 'medium':
                items = items.filter(price__gte=50000, price__lt=120000)
            elif budget_filter == 'high':
                items = items.filter(price__gte=120000)
                
            transport_items = items.order_by('price')
            
        elif transport_type == 'bus':
            items = BusService.objects.filter(
                departure=trip.origin,
                arrival=trip.destination,
                is_active=True
            )
            
            if budget_filter == 'low':
                items = items.filter(price__lt=30000)
            elif budget_filter == 'medium':
                items = items.filter(price__gte=30000, price__lt=60000)
            elif budget_filter == 'high':
                items = items.filter(price__gte=60000)
                
            transport_items = items.order_by('price')
            
        elif transport_type == 'car':
            items = CarRental.objects.filter(
                location=trip.origin,
                is_available=True
            )
            
            if budget_filter == 'low':
                items = items.filter(price_per_day__lt=50000)
            elif budget_filter == 'medium':
                items = items.filter(price_per_day__gte=50000, price_per_day__lt=100000)
            elif budget_filter == 'high':
                items = items.filter(price_per_day__gte=100000)
                
            transport_items = items.order_by('price_per_day')
        
        context = {
            'trip': trip,
            'transport_type': transport_type,
            'transport_items': transport_items,
            'budget_filter': budget_filter,
        }
        return render(request, self.template_name, context)

# ========== SELECT SEATS VIEW ==========
class SelectSeatsView(LoginRequiredMixin, View):
    template_name = 'planner/select_seats.html'
    
    def get(self, request, trip_id, transport_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.GET.get('type', 'flight')
        
        if transport_type == 'flight':
            transport = get_object_or_404(Flight, id=transport_id)
        elif transport_type == 'bus':
            transport = get_object_or_404(BusService, id=transport_id)
        else:
            transport = get_object_or_404(CarRental, id=transport_id)
            trip.transportation_preference = 'car'
            trip.selected_transport = {
                'type': 'car',
                'id': transport_id,
                'name': f"{transport.company} - {transport.car_model}",
            }
            trip.save()
            
            # Redirect with all parameters
            redirect_url = reverse('planner:plan')
            params = []
            
            if trip.origin:
                params.append(f'origin_id={trip.origin.id}')
                params.append(f'origin_name={trip.origin.name}')
            
            if trip.destination:
                params.append(f'destination_id={trip.destination.id}')
                params.append(f'destination_name={trip.destination.name}')
            
            if trip.selected_hotel:
                params.append(f'hotel_id={trip.selected_hotel.id}')
                params.append(f'hotel_name={trip.selected_hotel.name}')
            
            params.append(f'transport_id={transport_id}')
            params.append(f'transport_type=car')
            params.append(f'transport_name={trip.selected_transport["name"]}')
            
            if trip.start_date:
                params.append(f'start_date={trip.start_date.strftime("%Y-%m-%d")}')
            if trip.end_date:
                params.append(f'end_date={trip.end_date.strftime("%Y-%m-%d")}')
            
            params.append(f'travelers={trip.travelers}')
            
            if params:
                redirect_url += '?' + '&'.join(params)
            
            return redirect(redirect_url)
        
        context = {
            'trip': trip,
            'transport': transport,
            'transport_type': transport_type,
        }
        return render(request, self.template_name, context)

# ========== SEARCH REAL HOTELS VIEW ==========
class SearchRealHotelsView(LoginRequiredMixin, View):
    def get(self, request, destination_id):
        destination = get_object_or_404(Destination, id=destination_id)
        
        try:
            if destination.latitude and destination.longitude:
                lat = float(destination.latitude)
                lng = float(destination.longitude)
            else:
                geocoded = real_hotels_service.geocode_location(f"{destination.name}, Myanmar")
                if geocoded:
                    lat = geocoded['latitude']
                    lng = geocoded['longitude']
                else:
                    return JsonResponse({
                        'success': False,
                        'error': 'Destination coordinates not available'
                    })
            
            real_hotels = real_hotels_service.search_nearby_hotels(lat, lng)
            
            return JsonResponse({
                'success': True,
                'hotels': real_hotels,
                'count': len(real_hotels),
                'location': f'{destination.name}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

# ========== BOOK REAL HOTEL VIEW ==========
class BookRealHotelView(LoginRequiredMixin, View):
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            hotel_data = data.get('hotel_data')
            
            if not hotel_data:
                return JsonResponse({
                    'success': False,
                    'error': 'No hotel data provided'
                })
            
            booking_id = f"RB{int(timezone.now().timestamp())}"
            
            messages.success(
                request, 
                f"Simulated booking successful for {hotel_data.get('name', 'Hotel')}! "
                f"Booking ID: {booking_id}"
            )
            
            return JsonResponse({
                'success': True,
                'booking_id': booking_id,
                'message': 'Simulated booking successful',
                'hotel_name': hotel_data.get('name'),
                'total_price': hotel_data.get('price', 0) * trip.calculate_nights()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

# ========== CLEAR TRIP VIEW ==========
class ClearTripDataView(LoginRequiredMixin, View):
    def get(self, request):
        # Clear any draft trips
        TripPlan.objects.filter(
            user=request.user,
            status__in=['draft', 'planning']
        ).delete()
        
        messages.success(request, 'Trip data cleared. You can start a new trip.')
        return redirect('planner:plan')

# ========== TEST VIEW ==========
def test_view(request):
    """Simple test view to check if URLs are working"""
    return JsonResponse({'status': 'OK', 'message': 'Test view works'})

# Add this to your views.py (after the SelectPlanView)

# ========== ITINERARY DETAIL VIEW ==========
class ItineraryDetailView(LoginRequiredMixin, View):
    """Display detailed itinerary with weather and activity management"""
    template_name = 'planner/itinerary_detail.html'
    
    def get(self, request, trip_id, plan_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        # Get itinerary based on plan
        days = trip.calculate_nights() + 1
        itinerary_generator = PlanSelectionView()
        
        if plan_id == 'cultural':
            days_data = itinerary_generator.generate_cultural_itinerary(trip, days)
            plan_title = 'Cultural Explorer'
        elif plan_id == 'adventure':
            days_data = itinerary_generator.generate_adventure_itinerary(trip, days)
            plan_title = 'Adventure Seeker'
        elif plan_id == 'relaxed':
            days_data = itinerary_generator.generate_relaxed_itinerary(trip, days)
            plan_title = 'Relaxed Wanderer'
        else:
            days_data = []
            plan_title = 'Custom Plan'
        
        # Get weather forecast
        from .weather_service import weather_service
        weather_forecast = weather_service.get_weather_forecast(
            trip.destination.name,
            trip.start_date.strftime('%Y-%m-%d'),
            trip.end_date.strftime('%Y-%m-%d')
        )
        
        # Get trip cost estimate
        cost_estimate = self.calculate_cost_estimate(trip, plan_id)
        
        # Get selected hotel and transport
        hotel = trip.selected_hotel
        transport = trip.selected_transport
        
        context = {
            'trip': trip,
            'plan_id': plan_id,
            'plan_title': plan_title,
            'days_data': days_data,
            'weather_forecast': weather_forecast,
            'cost_estimate': cost_estimate,
            'hotel': hotel,
            'transport': transport,
            'total_days': days,
            'total_activities': sum(len(day['activities']) for day in days_data),
            'destination_name': trip.destination.name,
        }
        
        return render(request, self.template_name, context)
    
    def calculate_cost_estimate(self, trip, plan_id):
        """Calculate cost estimate based on plan"""
        nights = trip.calculate_nights()
        
        # Base costs by plan
        plan_costs = {
            'cultural': 1250,
            'adventure': 1450,
            'relaxed': 1100
        }
        
        base_cost = plan_costs.get(plan_id, 1000)
        
        # Adjust for number of travelers
        traveler_multiplier = 1 + ((trip.travelers - 1) * 0.7)  # 70% for additional travelers
        
        # Adjust for duration
        duration_multiplier = (nights + 1) / 3  # Based on 3-day base plan
        
        # Add hotel cost
        hotel_cost = 0
        if trip.selected_hotel:
            hotel_cost = float(trip.selected_hotel.price_per_night) * nights / 1300  # Convert MMK to USD approx
        
        # Add transport cost
        transport_cost = 0
        if trip.selected_transport and 'price' in trip.selected_transport:
            transport_cost = float(trip.selected_transport['price']) / 1300  # Convert MMK to USD approx
        
        total_cost = (base_cost * duration_multiplier * traveler_multiplier) + hotel_cost + transport_cost
        
        return {
            'total': round(total_cost),
            'breakdown': {
                'plan_base': round(base_cost * duration_multiplier),
                'hotel': round(hotel_cost),
                'transport': round(transport_cost),
                'additional_travelers': round(base_cost * duration_multiplier * (traveler_multiplier - 1))
            }
        }


# ========== ADD/REMOVE ACTIVITY VIEWS ==========
class AddActivityView(LoginRequiredMixin, View):
    """Add a new activity to itinerary"""
    def post(self, request, trip_id, plan_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            day_number = data.get('day_number')
            activity_data = data.get('activity')
            
            # In a real app, you would save this to a database
            # For now, we'll just return success
            
            return JsonResponse({
                'success': True,
                'message': 'Activity added successfully',
                'activity': activity_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class RemoveActivityView(LoginRequiredMixin, View):
    """Remove an activity from itinerary"""
    def post(self, request, trip_id, plan_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            day_number = data.get('day_number')
            activity_index = data.get('activity_index')
            
            # In a real app, you would remove from database
            
            return JsonResponse({
                'success': True,
                'message': 'Activity removed successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


# ========== DOWNLOAD PDF VIEW ==========
class DownloadItineraryPDFView(LoginRequiredMixin, View):
    """Generate and download itinerary as PDF"""
    def get(self, request, trip_id, plan_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        try:
            # For now, we'll create a simple HTML response
            # In production, use a PDF library like ReportLab or WeasyPrint
            
            from django.template.loader import render_to_string
            from django.http import HttpResponse
            
            itinerary_generator = PlanSelectionView()
            days = trip.calculate_nights() + 1
            
            if plan_id == 'cultural':
                days_data = itinerary_generator.generate_cultural_itinerary(trip, days)
                plan_title = 'Cultural Explorer'
            elif plan_id == 'adventure':
                days_data = itinerary_generator.generate_adventure_itinerary(trip, days)
                plan_title = 'Adventure Seeker'
            else:
                days_data = itinerary_generator.generate_relaxed_itinerary(trip, days)
                plan_title = 'Relaxed Wanderer'
            
            context = {
                'trip': trip,
                'plan_title': plan_title,
                'days_data': days_data,
                'current_date': timezone.now().strftime('%Y-%m-%d'),
                'hotel': trip.selected_hotel,
                'transport': trip.selected_transport,
            }
            
            html_content = render_to_string('planner/itinerary_pdf.html', context)
            
            # Create PDF response (simplified)
            response = HttpResponse(html_content, content_type='text/html')
            response['Content-Disposition'] = f'attachment; filename="itinerary_{trip.destination.name}_{plan_title}.html"'
            
            return response
            
        except Exception as e:
            messages.error(request, f'Error generating PDF: {str(e)}')
            return redirect('planner:itinerary_detail', trip_id=trip.id, plan_id=plan_id)