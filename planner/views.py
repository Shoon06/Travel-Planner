# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# FIX THE IMPORTS AT THE TOP

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
import random  # ADD THIS IMPORT
from django.conf import settings
from .models import Destination, Hotel, Flight, BusService, CarRental, TripPlan, Airline  # ADD Airline HERE
from .real_hotels_service import real_hotels_service


# ========== UPDATE SELECT SEATS VIEW ==========
class SelectSeatsView(LoginRequiredMixin, View):
    template_name = 'planner/select_seats.html'
    
    def get(self, request, trip_id, transport_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.GET.get('type', 'flight')
        
        if transport_type == 'flight':
            transport = get_object_or_404(Flight, id=transport_id)
            
            # Generate or get seat map
            if not transport.seat_map:
                transport.seat_map = transport.generate_seat_map()
                transport.save()
            
            # Get seat map data
            seat_map = transport.seat_map
            
            # Prepare seat layout for template
            rows = seat_map.get('total_rows', 30)
            seats_per_row = seat_map.get('seats_per_row', 6)
            occupied_seats = seat_map.get('occupied_seats', [])
            
            # Generate seat layout
            seat_layout = []
            seat_letters = ['A', 'B', 'C', 'D', 'E', 'F']
            
            for row in range(1, rows + 1):
                row_seats = []
                for col in range(seats_per_row):
                    seat_number = f"{row}{seat_letters[col]}"
                    seat_type = 'economy'
                    
                    # Determine seat type
                    if seat_number in seat_map.get('premium_seats', []):
                        seat_type = 'premium'
                    elif row <= seat_map.get('first_class_rows', 0):
                        seat_type = 'first'
                    elif row <= seat_map.get('first_class_rows', 0) + seat_map.get('business_class_rows', 0):
                        seat_type = 'business'
                    
                    # Check if occupied
                    is_occupied = seat_number in occupied_seats
                    
                    row_seats.append({
                        'number': seat_number,
                        'type': seat_type,
                        'occupied': is_occupied,
                        'price_multiplier': 1.5 if seat_type == 'premium' else 1.0
                    })
                
                seat_layout.append({
                    'row_number': row,
                    'seats': row_seats,
                    'is_first_class': row <= seat_map.get('first_class_rows', 0),
                    'is_business_class': row <= seat_map.get('first_class_rows', 0) + seat_map.get('business_class_rows', 0) and row > seat_map.get('first_class_rows', 0)
                })
            
            context = {
                'trip': trip,
                'transport': transport,
                'transport_type': transport_type,
                'seat_layout': seat_layout,
                'seat_letters': seat_letters,
                'seat_map_data': json.dumps(seat_map),
                'rows': rows,
                'seats_per_row': seats_per_row,
                'total_seats': transport.total_seats,
                'available_seats': transport.available_seats,
                'occupied_seats_count': len(occupied_seats),
            }
            
        elif transport_type == 'bus':
            transport = get_object_or_404(BusService, id=transport_id)
            
            # Generate bus seat map
            bus_seat_map = self.generate_bus_seat_map(transport)
            
            context = {
                'trip': trip,
                'transport': transport,
                'transport_type': transport_type,
                'seat_layout': bus_seat_map['layout'],
                'bus_seat_map': json.dumps(bus_seat_map),
                'total_seats': transport.total_seats,
                'available_seats': transport.available_seats,
            }
            
        else:
            # Car rental - no seat selection needed
            transport = get_object_or_404(CarRental, id=transport_id)
            trip.transportation_preference = 'car'
            trip.selected_transport = {
                'type': 'car',
                'id': transport_id,
                'name': f"{transport.company} - {transport.car_model}",
                'price': transport.price_in_mmk()
            }
            trip.save()
            
            return self.redirect_to_plan_with_transport(trip, transport_id, 'car', 
                                                       f"{transport.company} - {transport.car_model}")
        
        return render(request, self.template_name, context)
    # C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# UPDATE THE SelectSeatsView.post() method:

    def post(self, request, trip_id, transport_id):
        """Handle seat selection - REAL BOOKING SYSTEM"""
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.POST.get('transport_type', 'flight')
        
        try:
            selected_seats = json.loads(request.POST.get('selected_seats', '[]'))
            
            if not selected_seats:
                messages.error(request, 'Please select at least one seat.')
                return redirect('planner:select_seats', trip_id=trip_id, transport_id=transport_id)
            
            if len(selected_seats) > trip.travelers:
                messages.error(request, f'You can only select {trip.travelers} seat(s) for your trip.')
                return redirect('planner:select_seats', trip_id=trip_id, transport_id=transport_id)
            
            # REAL BOOKING PROCESS - Save booked seats to database
            booking_reference = f"BOOK{random.randint(100000, 999999)}"
            booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if seats are already booked
            from .models import BookedSeat
            
            already_booked_seats = []
            available_seats = []
            
            for seat_number in selected_seats:
                # Check if seat is already booked
                is_booked = BookedSeat.objects.filter(
                    transport_type=transport_type,
                    transport_id=transport_id,
                    seat_number=seat_number,
                    is_cancelled=False
                ).exists()
                
                if is_booked:
                    already_booked_seats.append(seat_number)
                else:
                    available_seats.append(seat_number)
            
            if already_booked_seats:
                messages.error(request, 
                    f'Some seats are already booked: {", ".join(already_booked_seats)}. '
                    f'Please select different seats.'
                )
                return redirect('planner:select_seats', trip_id=trip_id, transport_id=transport_id)
            
            # Book the available seats
            booked_seats_objects = []
            for seat_number in available_seats:
                booked_seat = BookedSeat.objects.create(
                    transport_type=transport_type,
                    transport_id=transport_id,
                    seat_number=seat_number,
                    trip=trip,
                    booked_by=request.user,
                    is_cancelled=False
                )
                booked_seats_objects.append(booked_seat)
            
            # Update transport availability
            if transport_type == 'flight':
                transport = Flight.objects.get(id=transport_id)
                transport.available_seats -= len(available_seats)
                transport.save()
                
                # Generate booking details
                booking_details = {
                    'booking_id': booking_reference,
                    'airline': transport.airline.name,
                    'flight_number': transport.flight_number,
                    'departure': transport.departure.name,
                    'arrival': transport.arrival.name,
                    'departure_time': transport.departure_time.strftime("%H:%M"),
                    'seats': available_seats,
                    'total_price': float(transport.price) * len(available_seats),
                    'booking_time': booking_time,
                    'status': 'CONFIRMED',
                    'note': 'Seats have been reserved for you.'
                }
                
            elif transport_type == 'bus':
                transport = BusService.objects.get(id=transport_id)
                transport.available_seats -= len(available_seats)
                transport.save()
                
                booking_details = {
                    'booking_id': booking_reference,
                    'company': transport.company,
                    'bus_type': transport.get_bus_type_display(),
                    'departure': transport.departure.name,
                    'arrival': transport.arrival.name,
                    'departure_time': transport.departure_time.strftime("%H:%M"),
                    'seats': available_seats,
                    'total_price': float(transport.price) * len(available_seats),
                    'booking_time': booking_time,
                    'status': 'CONFIRMED',
                    'note': 'Seats have been reserved for you.'
                }
            
            # Save to trip
            trip.selected_transport = {
                'type': transport_type,
                'id': transport_id,
                'name': f"{transport.airline.name if hasattr(transport, 'airline') else transport.company}",
                'price': booking_details['total_price'],
                'booking_details': booking_details,
                'seats': available_seats,
                'booking_id': booking_reference
            }
            trip.status = 'booked'  # Mark trip as booked
            trip.save()
            
            # Show success message with real booking details
            messages.success(request, 
                f"Booking successful! Reference: {booking_reference}<br>"
                f"Selected seats: {', '.join(available_seats)}<br>"
                f"Total: {booking_details['total_price']:,} MMK<br>"
                f"<small class='text-muted'>Your seats have been reserved.</small>"
            )
            
            return self.redirect_to_plan_with_transport(
                trip, transport_id, transport_type, 
                f"{transport.airline.name if hasattr(transport, 'airline') else transport.company}"
            )
            
        except Exception as e:
            messages.error(request, f'Error processing booking: {str(e)}')
            return redirect('planner:select_seats', trip_id=trip_id, transport_id=transport_id)
    # In the SelectSeatsView class in views.py, update generate_bus_seat_map:

    def generate_bus_seat_map(self, bus):
        """Generate seat map for bus using real booked seats"""
        from .models import BookedSeat
        
        total_rows = bus.total_seats // 4  # Assuming 4 seats per row
        
        # Get real occupied seats from database
        booked_seats = BookedSeat.objects.filter(
            transport_type='bus',
            transport_id=bus.id,
            is_cancelled=False
        ).values_list('seat_number', flat=True)
        
        occupied_seats = set(booked_seats)
        
        # Create layout
        layout = []
        for row in range(1, total_rows + 1):
            row_seats = []
            for seat in ['A', 'B', 'C', 'D']:
                seat_number = f"{row}{seat}"
                row_seats.append({
                    'number': seat_number,
                    'type': 'standard',
                    'occupied': seat_number in occupied_seats,
                    'is_window': seat in ['A', 'D'],
                    'is_aisle': seat in ['B', 'C']
                })
            layout.append({
                'row_number': row,
                'seats': row_seats
            })
        
        return {
            'layout': layout,
            'total_rows': total_rows,
            'seats_per_row': 4,
            'occupied_seats': list(occupied_seats),
            'configuration': '2-2'
        }
    def redirect_to_plan_with_transport(self, trip, transport_id, transport_type, transport_name):
        """Helper method to redirect back to plan page with transport selected"""
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
        params.append(f'transport_type={transport_type}')
        params.append(f'transport_name={transport_name}')
        
        if trip.start_date:
            params.append(f'start_date={trip.start_date.strftime("%Y-%m-%d")}')
        if trip.end_date:
            params.append(f'end_date={trip.end_date.strftime("%Y-%m-%d")}')
        
        params.append(f'travelers={trip.travelers}')
        
        if params:
            redirect_url += '?' + '&'.join(params)
        
        return redirect(redirect_url)

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
# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# UPDATE THE PlanTripView.get method:

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# UPDATE THE PlanTripView.get method:

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# UPDATE THE PlanTripView class:

class PlanTripView(LoginRequiredMixin, View):
    template_name = 'planner/plan.html'
    
    def get(self, request):
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # ALWAYS GET URL PARAMETERS FIRST
        origin_id = request.GET.get('origin_id')
        origin_name = request.GET.get('origin_name')
        destination_id = request.GET.get('destination_id')
        destination_name = request.GET.get('destination_name')
        start_date_param = request.GET.get('start_date')
        end_date_param = request.GET.get('end_date')
        travelers_param = request.GET.get('travelers')
        hotel_id = request.GET.get('hotel_id')
        hotel_name = request.GET.get('hotel_name')
        transport_id = request.GET.get('transport_id')
        transport_type = request.GET.get('transport_type')
        transport_name = request.GET.get('transport_name')
        
        # Initialize context
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
            'travelers': 2,
        }
        
        # 1. FIRST PRIORITY: URL parameters
        if origin_id and origin_name:
            context['selected_origin_id'] = origin_id
            context['origin_input'] = origin_name
        if destination_id and destination_name:
            context['selected_destination_id'] = destination_id
            context['destination_input'] = destination_name
        if start_date_param:
            context['today'] = start_date_param
        if end_date_param:
            context['tomorrow'] = end_date_param
        if travelers_param:
            context['travelers'] = int(travelers_param)
        if hotel_id and hotel_name:
            context['selected_hotel_id'] = hotel_id
            context['selected_hotel_name'] = hotel_name
        if transport_id and transport_name:
            context['selected_transport_id'] = transport_id
            context['selected_transport_type'] = transport_type
            context['selected_transport_name'] = transport_name
        
        # 2. SECOND PRIORITY: Existing trip in database
        if not (origin_id and destination_id):
            existing_trip = TripPlan.objects.filter(
                user=request.user,
                status__in=['draft', 'planning']
            ).first()
            
            if existing_trip:
                # Restore data from existing trip
                if not context['origin_input'] and existing_trip.origin:
                    context['origin_input'] = existing_trip.origin.name
                    context['selected_origin_id'] = existing_trip.origin.id
                if not context['destination_input'] and existing_trip.destination:
                    context['destination_input'] = existing_trip.destination.name
                    context['selected_destination_id'] = existing_trip.destination.id
                if not context['selected_hotel_id'] and existing_trip.selected_hotel:
                    context['selected_hotel_id'] = existing_trip.selected_hotel.id
                    context['selected_hotel_name'] = existing_trip.selected_hotel.name
                if not context['selected_transport_id'] and existing_trip.selected_transport:
                    context['selected_transport_id'] = existing_trip.selected_transport.get('id', '')
                    context['selected_transport_type'] = existing_trip.selected_transport.get('type', '')
                    context['selected_transport_name'] = existing_trip.selected_transport.get('name', '')
                if not start_date_param and existing_trip.start_date:
                    context['today'] = existing_trip.start_date.strftime('%Y-%m-%d')
                if not end_date_param and existing_trip.end_date:
                    context['tomorrow'] = existing_trip.end_date.strftime('%Y-%m-%d')
                if not travelers_param and existing_trip.travelers:
                    context['travelers'] = existing_trip.travelers
        
        # 3. THIRD PRIORITY: Individual GET parameters
        if not hotel_id and request.GET.get('hotel_id'):
            try:
                hotel = Hotel.objects.get(id=request.GET.get('hotel_id'))
                context['selected_hotel_id'] = hotel.id
                context['selected_hotel_name'] = hotel.name
            except Hotel.DoesNotExist:
                pass
        
        if not transport_id and request.GET.get('transport_id'):
            context['selected_transport_id'] = request.GET.get('transport_id')
            context['selected_transport_type'] = request.GET.get('transport_type', '')
            context['selected_transport_name'] = request.GET.get('transport_name', '')
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Handle both regular form submission and AJAX requests"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.handle_ajax(request)
        else:
            # Handle regular form submission
            return self.handle_form_submission(request)
    
    def handle_ajax(self, request):
        """Handle AJAX requests for saving trip info"""
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
    
    def handle_form_submission(self, request):
        """Handle regular form submission (when Continue button is clicked)"""
        try:
            origin_id = request.POST.get('origin_id')
            destination_id = request.POST.get('destination_id')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            travelers = request.POST.get('travelers', 1)
            hotel_id = request.POST.get('selected_hotel_id')
            transport_id = request.POST.get('selected_transport_id')
            transport_type = request.POST.get('selected_transport_type')
            
            # Validate required fields
            if not all([origin_id, destination_id, start_date, end_date, hotel_id, transport_id]):
                messages.error(request, 'Please fill in all required fields and select both hotel and transport.')
                return redirect('planner:plan')
            
            # Parse dates
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Invalid date format.')
                return redirect('planner:plan')
            
            if end_date_obj <= start_date_obj:
                messages.error(request, 'End date must be after start date.')
                return redirect('planner:plan')
            
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
                trip.selected_hotel_id = hotel_id
                trip.transportation_preference = transport_type
                trip.status = 'booked'
            else:
                trip = TripPlan.objects.create(
                    user=request.user,
                    origin_id=origin_id,
                    destination_id=destination_id,
                    start_date=start_date_obj,
                    end_date=end_date_obj,
                    travelers=travelers,
                    selected_hotel_id=hotel_id,
                    transportation_preference=transport_type,
                    budget_range='medium',
                    status='booked'
                )
            
            # Save transport details
            if transport_id:
                if transport_type == 'flight':
                    transport = Flight.objects.get(id=transport_id)
                    transport_name = f"{transport.airline} Flight {transport.flight_number}"
                elif transport_type == 'bus':
                    transport = BusService.objects.get(id=transport_id)
                    transport_name = f"{transport.company} Bus"
                elif transport_type == 'car':
                    transport = CarRental.objects.get(id=transport_id)
                    transport_name = f"{transport.company} - {transport.car_model}"
                
                trip.selected_transport = {
                    'type': transport_type,
                    'id': transport_id,
                    'name': transport_name,
                    'price': getattr(transport, 'price', getattr(transport, 'price_per_day', 0))
                }
            
            trip.save()
            
            messages.success(request, 'Trip booked successfully!')
            return redirect('planner:dashboard')
            
        except Exception as e:
            messages.error(request, f'Error booking trip: {str(e)}')
            return redirect('planner:plan')
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

# ========== SAVE HOTEL VIEW ==========
# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# UPDATE THE SaveHotelView.post method:

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
                
                # Build redirect URL with ALL trip parameters
                redirect_url = reverse('planner:plan')
                params = []
                
                # CRITICAL: Always include origin and destination
                if trip.origin:
                    params.append(f'origin_id={trip.origin.id}')
                    params.append(f'origin_name={trip.origin.name}')
                
                if trip.destination:
                    params.append(f'destination_id={trip.destination.id}')
                    params.append(f'destination_name={trip.destination.name}')
                
                # Add hotel
                params.append(f'hotel_id={hotel_id}')
                params.append(f'hotel_name={hotel.name}')
                
                # Add dates
                if trip.start_date:
                    params.append(f'start_date={trip.start_date.strftime("%Y-%m-%d")}')
                if trip.end_date:
                    params.append(f'end_date={trip.end_date.strftime("%Y-%m-%d")}')
                
                # Add travelers
                params.append(f'travelers={trip.travelers}')
                
                # IMPORTANT: Check if transport already exists and include it
                if trip.selected_transport:
                    transport_data = trip.selected_transport
                    if transport_data.get('id'):
                        params.append(f'transport_id={transport_data.get("id")}')
                        params.append(f'transport_type={transport_data.get("type", "")}')
                        params.append(f'transport_name={transport_data.get("name", "")}')
                
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


# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# UPDATE THE SaveTransportView.post method:

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# UPDATE THE SaveTransportView.post method:

class SaveTransportView(LoginRequiredMixin, View):
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.POST.get('transport_type')
        transport_id = request.POST.get('transport_id')
        
        try:
            trip.transportation_preference = transport_type
            
            if transport_type == 'flight':
                transport = Flight.objects.get(id=transport_id)
                transport_name = f"{transport.airline} Flight {transport.flight_number}"
                price = transport.price_in_mmk()
            elif transport_type == 'bus':
                transport = BusService.objects.get(id=transport_id)
                transport_name = f"{transport.company} Bus"
                price = transport.price_in_mmk()
            elif transport_type == 'car':
                transport = CarRental.objects.get(id=transport_id)
                transport_name = f"{transport.company} - {transport.car_model}"
                price = transport.price_in_mmk() if hasattr(transport, 'price_in_mmk') else transport.price_per_day
            else:
                messages.error(request, 'Invalid transport type.')
                return redirect('planner:select_transport_category', trip_id=trip.id)
            
            trip.selected_transport = {
                'type': transport_type,
                'id': transport_id,
                'name': transport_name,
                'price': price
            }
            trip.save()
            
            # Build redirect URL with ALL trip parameters
            redirect_url = reverse('planner:plan')
            params = []
            
            # CRITICAL: Always include origin and destination
            if trip.origin:
                params.append(f'origin_id={trip.origin.id}')
                params.append(f'origin_name={trip.origin.name}')
            
            if trip.destination:
                params.append(f'destination_id={trip.destination.id}')
                params.append(f'destination_name={trip.destination.name}')
            
            # IMPORTANT: Check if hotel already exists and include it
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

class SelectTransportView(LoginRequiredMixin, View):
    template_name = 'planner/transport_list.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.GET.get('type', 'flight')
        transport_class = request.GET.get('class', 'all')
        
        transport_items = []
        
        if transport_type == 'flight':
            # Check if both origin and destination have airports
            if not self.check_has_airport(trip.origin) or not self.check_has_airport(trip.destination):
                context = {
                    'trip': trip,
                    'transport_type': transport_type,
                    'transport_items': [],
                    'transport_class': transport_class,
                    'error_message': f'Air travel not available. {trip.origin.name} or {trip.destination.name} does not have an airport.',
                }
                return render(request, self.template_name, context)
            
            # Always create 3 simple flight options (Low, Medium, High)
            transport_items = self.create_simple_flights(trip, transport_class)
            
        elif transport_type == 'bus':
            # Always create 3 simple bus options (Low, Medium, High)
            transport_items = self.create_simple_buses(trip, transport_class)
            
        elif transport_type == 'car':
            # Always create 3 simple car options (Low, Medium, High)
            transport_items = self.create_simple_cars(trip, transport_class)
        
        context = {
            'trip': trip,
            'transport_type': transport_type,
            'transport_items': transport_items,
            'transport_class': transport_class,
        }
        return render(request, self.template_name, context)
    
    def check_has_airport(self, destination):
        """Check if a destination has an airport using the model method"""
        return destination.has_airport()
    
    def create_simple_flights(self, trip, transport_class):
        """Create 3 simple flight options (Low, Medium, High)"""
        from datetime import timedelta
        
        # Check if flights already exist for this trip
        existing_flights = Flight.objects.filter(
            departure=trip.origin,
            arrival=trip.destination,
            is_active=True
        )
        
        # Define flight options (Low, Medium, High)
        flight_options = [
            {
                'class': 'low',
                'name': 'Economy Flight',
                'description': 'Basic seating with standard service',
                'base_price': 50000,
                'departure_times': ['08:00', '14:00', '20:00'],
                'duration_hours': random.randint(1, 3),
                'total_seats': 150,
                'available_seats': random.randint(80, 140),
            },
            {
                'class': 'medium',
                'name': 'Business Flight',
                'description': 'Comfortable seating with extra legroom',
                'base_price': 100000,
                'departure_times': ['09:00', '15:00', '21:00'],
                'duration_hours': random.randint(1, 3),
                'total_seats': 120,
                'available_seats': random.randint(50, 100),
            },
            {
                'class': 'high',
                'name': 'Luxury Flight',
                'description': 'Premium service with full amenities',
                'base_price': 180000,
                'departure_times': ['10:00', '16:00', '22:00'],
                'duration_hours': random.randint(1, 3),
                'total_seats': 100,
                'available_seats': random.randint(30, 80),
            }
        ]
        
        flights_to_return = []
        
        for option in flight_options:
            if transport_class != 'all' and transport_class != option['class']:
                continue
            
            # Check if this flight already exists
            existing = existing_flights.filter(category=option['class']).first()
            
            if not existing:
                # Get a default airline
                airline, _ = Airline.objects.get_or_create(
                    name="Myanmar Travel Airlines",
                    defaults={'code': 'MTA', 'is_default_for_domestic': True}
                )
                
                # Create the flight
                departure_time = random.choice(option['departure_times'])
                arrival_hour = int(departure_time.split(':')[0]) + option['duration_hours']
                if arrival_hour >= 24:
                    arrival_hour -= 24
                arrival_time = f"{arrival_hour:02d}:{random.choice(['00', '30'])}"
                
                flight = Flight.objects.create(
                    airline=airline,
                    flight_number=f"MTA{random.randint(100, 999)}",
                    departure=trip.origin,
                    arrival=trip.destination,
                    departure_time=departure_time,
                    arrival_time=arrival_time,
                    duration=timedelta(hours=option['duration_hours']),
                    price=option['base_price'] + random.randint(-5000, 10000),
                    category=option['class'],
                    total_seats=option['total_seats'],
                    available_seats=option['available_seats'],
                    description=option['description'],
                    is_active=True
                )
                
                # Generate seat map
                flight.seat_map = flight.generate_seat_map()
                flight.save()
                
                flights_to_return.append(flight)
            else:
                flights_to_return.append(existing)
        
        return flights_to_return
    
    def create_simple_buses(self, trip, transport_class):
        """Create 3 simple bus options (Low, Medium, High)"""
        from datetime import timedelta
        
        # Check if buses already exist for this trip
        existing_buses = BusService.objects.filter(
            departure=trip.origin,
            arrival=trip.destination,
            is_active=True
        )
        
        # Define bus options (Low, Medium, High)
        bus_options = [
            {
                'class': 'low',
                'bus_type': 'standard',
                'name': 'Standard Bus',
                'description': 'Regular bus with basic amenities',
                'base_price': 20000,
                'departure_times': ['08:00', '20:00'],
                'duration_hours': random.randint(4, 10),
                'total_seats': 40,
                'available_seats': random.randint(15, 35),
            },
            {
                'class': 'medium',
                'bus_type': 'vip',
                'name': 'VIP Bus',
                'description': 'Comfortable bus with AC and snacks',
                'base_price': 40000,
                'departure_times': ['09:00', '21:00'],
                'duration_hours': random.randint(4, 10),
                'total_seats': 32,
                'available_seats': random.randint(10, 25),
            },
            {
                'class': 'high',
                'bus_type': 'luxury',
                'name': 'Luxury Bus',
                'description': 'Premium bus with sleeper seats and meals',
                'base_price': 70000,
                'departure_times': ['10:00', '22:00'],
                'duration_hours': random.randint(4, 10),
                'total_seats': 24,
                'available_seats': random.randint(5, 20),
            }
        ]
        
        buses_to_return = []
        
        for option in bus_options:
            if transport_class != 'all' and transport_class != option['class']:
                continue
            
            # Check if this bus already exists
            existing = existing_buses.filter(bus_type=option['bus_type']).first()
            
            if not existing:
                # Create the bus
                departure_time = random.choice(option['departure_times'])
                
                bus = BusService.objects.create(
                    company="Myanmar Express Bus",
                    departure=trip.origin,
                    arrival=trip.destination,
                    departure_time=departure_time,
                    duration=timedelta(hours=option['duration_hours']),
                    price=option['base_price'] + random.randint(-3000, 5000),
                    bus_type=option['bus_type'],
                    total_seats=option['total_seats'],
                    available_seats=option['available_seats'],
                    bus_number=f"MEB{random.randint(100, 999)}",
                    description=option['description'],
                    is_active=True
                )
                
                buses_to_return.append(bus)
            else:
                buses_to_return.append(existing)
        
        return buses_to_return
    
    def create_simple_cars(self, trip, transport_class):
        """Create 3 simple car options (Low, Medium, High)"""
        
        # Check if cars already exist for this location
        existing_cars = CarRental.objects.filter(
            location=trip.origin,
            is_available=True
        )
        
        # Define car options (Low, Medium, High)
        car_options = [
            {
                'class': 'low',
                'car_type': 'economy',
                'name': 'Economy Car',
                'car_model': 'Toyota Vios',
                'description': 'Fuel-efficient car for city driving',
                'base_price': 40000,
                'seats': 5,
                'features': ['AC', 'Radio', 'Airbag'],
            },
            {
                'class': 'medium',
                'car_type': 'suv',
                'name': 'SUV',
                'car_model': 'Toyota Fortuner',
                'description': 'Spacious SUV for family trips',
                'base_price': 80000,
                'seats': 7,
                'features': ['AC', 'GPS', 'Bluetooth', 'Airbag', 'USB Ports'],
            },
            {
                'class': 'high',
                'car_type': 'luxury',
                'name': 'Luxury Car',
                'car_model': 'Mercedes-Benz',
                'description': 'Premium luxury car with all features',
                'base_price': 150000,
                'seats': 5,
                'features': ['Premium AC', 'GPS Navigation', 'Leather Seats', 'Premium Sound', 'Sunroof'],
            }
        ]
        
        cars_to_return = []
        
        for option in car_options:
            if transport_class != 'all' and transport_class != option['class']:
                continue
            
            # Check if this car already exists
            existing = existing_cars.filter(car_type=option['car_type']).first()
            
            if not existing:
                # Create the car
                car = CarRental.objects.create(
                    company="Myanmar Car Rentals",
                    car_model=option['car_model'],
                    car_type=option['car_type'],
                    seats=option['seats'],
                    price_per_day=option['base_price'] + random.randint(-5000, 10000),
                    features=option['features'],
                    is_available=True,
                    location=trip.origin,
                    description=option['description'],
                    transmission='automatic',
                    fuel_type='Petrol'
                )
                
                cars_to_return.append(car)
            else:
                cars_to_return.append(existing)
        
        return cars_to_return
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