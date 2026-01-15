# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# COMPLETE CORRECTED VERSION

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
import random
from django.conf import settings
from .models import Destination, Hotel, Flight, BusService, CarRental, TripPlan, Airline, BookedSeat,TransportSchedule 
from .real_hotels_service import real_hotels_service
import urllib.parse  # Add this import for URL encoding

# ========== UPDATE SELECT SEATS VIEW ==========
# ========== UPDATE SELECT SEATS VIEW ==========
class SelectSeatsView(LoginRequiredMixin, View):
    template_name = 'planner/select_seats.html'
    
    def get(self, request, trip_id, transport_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.GET.get('type', 'flight')
        
        # Get schedule for this date
        travel_date = trip.start_date
        schedule = get_object_or_404(
            TransportSchedule,
            transport_type=transport_type,
            transport_id=transport_id,
            travel_date=travel_date,
            is_active=True
        )
        
        # Check if enough seats available
        if schedule.available_seats < trip.travelers:
            messages.error(request, 
                f'Not enough seats available. Only {schedule.available_seats} seat(s) left.'
            )
            return redirect('planner:select_transport', trip_id=trip.id)
        
        if transport_type == 'flight':
            transport = get_object_or_404(Flight, id=transport_id)
            
            # Generate seat map with date-based occupied seats
            if not transport.seat_map:
                transport.seat_map = transport.generate_seat_map()
                transport.save()
            
            # Get occupied seats for this specific date
            occupied_seats = self.get_occupied_seats_for_date(transport_type, transport_id, travel_date)
            
            # DEBUG: Show seat information
            print(f"DEBUG: Flight {transport.flight_number} - Total seats: {transport.total_seats}")
            print(f"DEBUG: Occupied seats: {len(occupied_seats)}")
            print(f"DEBUG: Available in schedule: {schedule.available_seats}")
            
            # Update seat map with date-specific occupied seats
            seat_map = transport.seat_map
            seat_map['occupied_seats'] = occupied_seats
            
            # Prepare seat layout
            rows = seat_map.get('total_rows', 30)
            seats_per_row = seat_map.get('seats_per_row', 6)
            seat_letters = ['A', 'B', 'C', 'D', 'E', 'F']
            
            seat_layout = []
            for row in range(1, rows + 1):
                row_seats = []
                for col in range(seats_per_row):
                    seat_number = f"{row}{seat_letters[col]}"
                    seat_type = 'economy'
                    
                    if seat_number in seat_map.get('premium_seats', []):
                        seat_type = 'premium'
                    elif row <= seat_map.get('first_class_rows', 0):
                        seat_type = 'first'
                    elif row <= seat_map.get('first_class_rows', 0) + seat_map.get('business_class_rows', 0):
                        seat_type = 'business'
                    
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
                'seat_map_data': json.dumps(seat_map),
                'rows': rows,
                'seats_per_row': seats_per_row,
                'total_seats': transport.total_seats,
                'available_seats': schedule.available_seats,
                'occupied_seats_count': len(occupied_seats),
                'schedule': schedule,
                'travel_date': travel_date,
            }
            
        elif transport_type == 'bus':
            transport = get_object_or_404(BusService, id=transport_id)
            
            # Get occupied seats for this specific date
            occupied_seats = self.get_occupied_seats_for_date(transport_type, transport_id, travel_date)
            
            # DEBUG: Show seat information
            print(f"DEBUG: Bus {transport.company} - Total seats: {transport.total_seats}")
            print(f"DEBUG: Occupied seats: {len(occupied_seats)}")
            print(f"DEBUG: Available in schedule: {schedule.available_seats}")
            
            # Generate bus seat map with date-specific occupied seats
            bus_seat_map = self.generate_bus_seat_map(transport, occupied_seats)
            
            context = {
                'trip': trip,
                'transport': transport,
                'transport_type': transport_type,
                'seat_layout': bus_seat_map['layout'],
                'bus_seat_map': json.dumps(bus_seat_map),
                'total_seats': transport.total_seats,
                'available_seats': schedule.available_seats,
                'schedule': schedule,
                'travel_date': travel_date,
            }
            
        else:
            # Car rental - no seat selection needed
            transport = get_object_or_404(CarRental, id=transport_id)
            trip.transportation_preference = 'car'
            trip.selected_transport = {
                'type': 'car',
                'id': transport_id,
                'schedule_id': schedule.id,
                'name': f"{transport.company} - {transport.car_model}",
                'price': schedule.price,
                'travel_date': travel_date.strftime('%Y-%m-%d')
            }
            trip.save()
            
            return self.redirect_to_plan_with_transport(trip, transport_id, 'car', 
                                                       f"{transport.company} - {transport.car_model}")
        
        return render(request, self.template_name, context)
    
    def get_occupied_seats_for_date(self, transport_type, transport_id, travel_date):
        """Get occupied seats for specific date"""
        return list(BookedSeat.objects.filter(
            transport_type=transport_type,
            transport_id=transport_id,
            schedule_date=travel_date,
            is_cancelled=False
        ).values_list('seat_number', flat=True))
    
    def generate_bus_seat_map(self, bus, occupied_seats):
        """Generate seat map for bus with driver seat, door, etc."""
        # Bus configurations based on bus type
        configs = {
            'standard': {'rows': 10, 'seats_per_row': 4, 'layout': '2-2'},
            'vip': {'rows': 8, 'seats_per_row': 4, 'layout': '2-2'},
            'luxury': {'rows': 6, 'seats_per_row': 4, 'layout': '2-2'},
        }
        
        config = configs.get(bus.bus_type, configs['standard'])
        rows = config['rows']
        seats_per_row = config['seats_per_row']
        
        # Seat letters based on layout
        if config['layout'] == '2-2':
            seat_letters = ['A', 'B', 'C', 'D']
        elif config['layout'] == '2-1':
            seat_letters = ['A', 'B', 'C']
        else:
            seat_letters = ['A', 'B', 'C', 'D']
        
        # Generate seat layout
        seat_layout = []
        for row in range(1, rows + 1):
            row_seats = []
            for col in range(seats_per_row):
                seat_number = f"{row}{seat_letters[col]}"
                is_occupied = seat_number in occupied_seats
                
                # Determine seat type
                seat_type = 'regular'
                if row == 1 and seat_letters[col] in ['A', 'B']:
                    seat_type = 'premium'  # Front seats
                elif row == rows and seat_letters[col] in ['C', 'D']:
                    seat_type = 'back'  # Back seats
                
                row_seats.append({
                    'number': seat_number,
                    'type': seat_type,
                    'occupied': is_occupied,
                    'price_multiplier': 1.2 if seat_type == 'premium' else 1.0
                })
            
            seat_layout.append({
                'row_number': row,
                'seats': row_seats,
                'has_driver': row == 1,
                'has_door': row == 3 or row == rows - 2,
            })
        
        # Bus seat map data
        bus_seat_map = {
            'total_rows': rows,
            'seats_per_row': seats_per_row,
            'layout': config['layout'],
            'driver_seat': '1A',
            'door_positions': [3, rows - 2] if rows > 4 else [2],
            'premium_seats': ['1A', '1B'],
            'occupied_seats': occupied_seats,
            'seat_prices': {
                'premium': float(bus.price) * 1.2,
                'regular': float(bus.price),
                'back': float(bus.price) * 0.9
            }
        }
        
        return {
            'layout': seat_layout,
            'config': bus_seat_map,
            'bus_type': bus.bus_type,
            'total_seats': bus.total_seats,
            'occupied_count': len(occupied_seats)
        }
    
    def redirect_to_plan_with_transport(self, trip, transport_id, transport_type, transport_name):
        """Helper method to redirect to plan with transport selected"""
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
    
    def post(self, request, trip_id, transport_id):
        """Handle seat selection - Store selected seats temporarily, don't book yet"""
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.POST.get('transport_type', 'flight')
        travel_date = trip.start_date
        
        try:
            selected_seats = json.loads(request.POST.get('selected_seats', '[]'))
            
            if not selected_seats:
                messages.error(request, 'Please select at least one seat.')
                return redirect('planner:select_seats', trip_id=trip_id, transport_id=transport_id)
            
            if len(selected_seats) > trip.travelers:
                messages.error(request, f'You can only select {trip.travelers} seat(s) for your trip.')
                return redirect('planner:select_seats', trip_id=trip_id, transport_id=transport_id)
            
            # Get schedule for this date
            schedule = get_object_or_404(
                TransportSchedule,
                transport_type=transport_type,
                transport_id=transport_id,
                travel_date=travel_date,
                is_active=True
            )
            
            # Check if enough seats available (considering already booked seats)
            # First, count how many seats are already booked
            already_booked_count = BookedSeat.objects.filter(
                transport_type=transport_type,
                transport_id=transport_id,
                schedule_date=travel_date,
                is_cancelled=False
            ).count()
            
            # Calculate real available seats
            real_available_seats = schedule.total_seats - already_booked_count
            
            if real_available_seats < len(selected_seats):
                messages.error(request, 
                    f'Not enough seats available. Only {real_available_seats} seat(s) left.'
                )
                return redirect('planner:select_seats', trip_id=trip_id, transport_id=transport_id)
            
            # Check if seats are already booked for this date
            already_booked_seats = []
            available_seats = []
            
            for seat_number in selected_seats:
                is_booked = BookedSeat.objects.filter(
                    transport_type=transport_type,
                    transport_id=transport_id,
                    schedule_date=travel_date,
                    seat_number=seat_number,
                    is_cancelled=False
                ).exists()
                
                if is_booked:
                    already_booked_seats.append(seat_number)
                else:
                    available_seats.append(seat_number)
            
            if already_booked_seats:
                messages.error(request, 
                    f'Some seats are already booked for {travel_date}: {", ".join(already_booked_seats)}. '
                    f'Please select different seats.'
                )
                return redirect('planner:select_seats', trip_id=trip_id, transport_id=transport_id)
            
            # CRITICAL FIX: Don't book seats yet - just store them as pending selection
            # Generate temporary booking reference
            booking_reference = f"TEMP{int(timezone.now().timestamp())}"
            
            if transport_type == 'flight':
                transport = Flight.objects.get(id=transport_id)
                booking_details = {
                    'booking_id': booking_reference,
                    'airline': transport.airline.name,
                    'flight_number': transport.flight_number,
                    'departure': transport.departure.name,
                    'arrival': transport.arrival.name,
                    'departure_time': transport.departure_time.strftime("%H:%M"),
                    'travel_date': travel_date.strftime("%Y-%m-%d"),
                    'seats': available_seats,  # Store selected seats
                    'total_price': float(schedule.price) * len(available_seats),
                    'status': 'PENDING',  # Changed from CONFIRMED to PENDING
                    'is_temporary': True,  # Mark as temporary
                    'seat_count': len(available_seats),
                }
            elif transport_type == 'bus':
                transport = BusService.objects.get(id=transport_id)
                booking_details = {
                    'booking_id': booking_reference,
                    'company': transport.company,
                    'bus_type': transport.get_bus_type_display(),
                    'departure': transport.departure.name,
                    'arrival': transport.arrival.name,
                    'departure_time': transport.departure_time.strftime("%H:%M"),
                    'travel_date': travel_date.strftime("%Y-%m-%d"),
                    'seats': available_seats,
                    'total_price': float(schedule.price) * len(available_seats),
                    'status': 'PENDING',  # Changed from CONFIRMED to PENDING
                    'is_temporary': True,  # Mark as temporary
                    'seat_count': len(available_seats),
                }
            
            # Save to trip as PENDING selection
            trip.selected_transport = {
                'type': transport_type,
                'id': transport_id,
                'schedule_id': schedule.id,
                'name': f"{transport.airline.name if hasattr(transport, 'airline') else transport.company}",
                'price': booking_details['total_price'],
                'booking_details': booking_details,
                'seats': available_seats,  # Store selected seats
                'booking_id': booking_reference,
                'travel_date': travel_date.strftime("%Y-%m-%d"),
                'is_temporary': True,  # Mark as temporary
                'needs_confirmation': True,  # Needs final confirmation
                'seat_count': len(available_seats),
            }
            trip.status = 'planning'  # Keep as planning, NOT 'booked'
            trip.save()
            
            messages.success(request, 
                f"✅ Seats selected successfully!<br>"
                f"📌 Selected seats: {', '.join(available_seats)}<br>"
                f"💰 Total: {booking_details['total_price']:,} MMK<br>"
                f"<small class='text-muted'>Seats will be confirmed when you complete your trip planning.</small>"
            )
            
            return self.redirect_to_plan_with_transport(
                trip, transport_id, transport_type, 
                f"{transport.airline.name if hasattr(transport, 'airline') else transport.company}"
            )
            
        except Exception as e:
            import traceback
            print(f"ERROR in seat selection: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f'Error processing seat selection: {str(e)}')
            return redirect('planner:select_seats', trip_id=trip_id, transport_id=transport_id)
# IN THE DashboardView CLASS, UPDATE THE get_context_data METHOD:
# ========== CONFIRM SEAT BOOKING VIEW ==========
class ConfirmSeatBookingView(LoginRequiredMixin, View):
    """Final confirmation of seat booking after plan selection"""
    
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        # Check if trip has temporary seat selection
        if not trip.selected_transport or not trip.selected_transport.get('is_temporary', False):
            messages.error(request, 'No pending seat selection to confirm.')
            return redirect('planner:plan_selection', trip_id=trip.id)
        
        transport_type = trip.selected_transport.get('type')
        transport_id = trip.selected_transport.get('id')
        selected_seats = trip.selected_transport.get('seats', [])
        travel_date = trip.start_date
        
        try:
            # Get schedule for this date
            schedule = get_object_or_404(
                TransportSchedule,
                transport_type=transport_type,
                transport_id=transport_id,
                travel_date=travel_date,
                is_active=True
            )
            
            # Check if seats are still available
            already_booked_seats = []
            available_seats = []
            
            for seat_number in selected_seats:
                is_booked = BookedSeat.objects.filter(
                    transport_type=transport_type,
                    transport_id=transport_id,
                    schedule_date=travel_date,
                    seat_number=seat_number,
                    is_cancelled=False
                ).exists()
                
                if is_booked:
                    already_booked_seats.append(seat_number)
                else:
                    available_seats.append(seat_number)
            
            if already_booked_seats:
                messages.error(request, 
                    f'Some seats are no longer available: {", ".join(already_booked_seats)}. '
                    f'Please select different seats.'
                )
                # Redirect back to seat selection
                return redirect('planner:select_seats', trip_id=trip.id, transport_id=transport_id)
            
            # Check if enough seats available (using real calculation)
            already_booked_count = BookedSeat.objects.filter(
                transport_type=transport_type,
                transport_id=transport_id,
                schedule_date=travel_date,
                is_cancelled=False
            ).count()
            
            real_available_seats = schedule.total_seats - already_booked_count
            
            if real_available_seats < len(available_seats):
                messages.error(request, 
                    f'Not enough seats available. Only {real_available_seats} seat(s) left.'
                )
                return redirect('planner:select_seats', trip_id=trip.id, transport_id=transport_id)
            
            # NOW book the seats permanently
            booked_seats_objects = []
            for seat_number in available_seats:
                booked_seat = BookedSeat.objects.create(
                    transport_type=transport_type,
                    transport_id=transport_id,
                    schedule_date=travel_date,
                    seat_number=seat_number,
                    trip=trip,
                    booked_by=request.user,
                    is_cancelled=False
                )
                booked_seats_objects.append(booked_seat)
            
            # Update schedule availability
            schedule.available_seats -= len(available_seats)
            schedule.save()
            
            # Generate final booking reference
            booking_reference = f"BOOK{random.randint(100000, 999999)}"
            
            # Update trip with confirmed booking
            if transport_type == 'flight':
                transport = Flight.objects.get(id=transport_id)
                booking_details = {
                    'booking_id': booking_reference,
                    'airline': transport.airline.name,
                    'flight_number': transport.flight_number,
                    'departure': transport.departure.name,
                    'arrival': transport.arrival.name,
                    'departure_time': transport.departure_time.strftime("%H:%M"),
                    'travel_date': travel_date.strftime("%Y-%m-%d"),
                    'seats': available_seats,
                    'total_price': float(schedule.price) * len(available_seats),
                    'status': 'CONFIRMED',
                    'confirmed_at': timezone.now().isoformat(),
                }
            elif transport_type == 'bus':
                transport = BusService.objects.get(id=transport_id)
                booking_details = {
                    'booking_id': booking_reference,
                    'company': transport.company,
                    'bus_type': transport.get_bus_type_display(),
                    'departure': transport.departure.name,
                    'arrival': transport.arrival.name,
                    'departure_time': transport.departure_time.strftime("%H:%M"),
                    'travel_date': travel_date.strftime("%Y-%m-%d"),
                    'seats': available_seats,
                    'total_price': float(schedule.price) * len(available_seats),
                    'status': 'CONFIRMED',
                    'confirmed_at': timezone.now().isoformat(),
                }
            
            # Update trip with confirmed booking (remove temporary flag)
            trip.selected_transport = {
                'type': transport_type,
                'id': transport_id,
                'schedule_id': schedule.id,
                'name': f"{transport.airline.name if hasattr(transport, 'airline') else transport.company}",
                'price': booking_details['total_price'],
                'booking_details': booking_details,
                'seats': available_seats,
                'booking_id': booking_reference,
                'travel_date': travel_date.strftime("%Y-%m-%d"),
                'is_temporary': False,  # Remove temporary flag
                'needs_confirmation': False,  # Remove needs confirmation
                'confirmed_at': timezone.now().isoformat(),
            }
            trip.status = 'booked'  # Now mark as booked
            trip.save()
            
            messages.success(request, 
                f"🎉 Booking confirmed! Reference: {booking_reference}<br>"
                f"📅 Date: {travel_date.strftime('%Y-%m-%d')}<br>"
                f"💺 Seats: {', '.join(available_seats)}<br>"
                f"💰 Total: {booking_details['total_price']:,} MMK<br>"
                f"<small class='text-success'>Your seats are now officially reserved.</small>"
            )
            
            # Redirect to itinerary detail or dashboard
            return redirect('planner:itinerary_detail', trip_id=trip.id, plan_id='cultural')
            
        except Exception as e:
            import traceback
            print(f"ERROR confirming booking: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f'Error confirming booking: {str(e)}')
            return redirect('planner:plan_selection', trip_id=trip.id)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'planner/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.now().date()  # Dynamic date
        
        # Get all trips for this user
        trips = TripPlan.objects.filter(user=user).order_by('-created_at')
        
        # Calculate statistics
        total_trips = trips.count()
        
        # Upcoming trips (status: draft, planning, booked AND start_date in future)
        upcoming_trips = trips.filter(
            status__in=['draft', 'planning', 'booked'],
            start_date__gte=today
        ).count()
        
        # Total spent (only for booked and completed trips)
        total_spent = 0
        for trip in trips.filter(status__in=['booked', 'completed']):
            total_spent += trip.get_total_cost_in_mmk()
        
        # Unique destinations visited (trips that have ended)
        destinations_visited = trips.filter(
            Q(status='completed') | Q(end_date__lt=today)
        ).exclude(
            status='cancelled'
        ).values('destination__name').distinct().count()
        
        print(f"DASHBOARD DEBUG: Today: {today}, Destinations visited: {destinations_visited}")
        
        # Get upcoming trips for display
        upcoming_trips_list = trips.filter(
            status__in=['draft', 'planning', 'booked'],
            start_date__gte=today
        ).order_by('start_date')[:3]
        
        # Prepare upcoming trips data for template
        upcoming_trips_data = []
        for trip in upcoming_trips_list:
            upcoming_trips_data.append({
                'id': trip.id,
                'title': f"{trip.destination.name} Trip",
                'date_range': f"{trip.start_date.strftime('%b %d')} - {trip.end_date.strftime('%b %d, %Y')}",
                'travelers': trip.travelers,
                'status': trip.status,
                'cost': trip.get_total_cost_in_mmk(),
                'destination_name': trip.destination.name
            })
        
        context.update({
            'trips': trips,
            'total_trips': total_trips,
            'upcoming_trips': upcoming_trips,
            'total_spent': total_spent,
            'destinations_visited': destinations_visited,
            'upcoming_trips_list': upcoming_trips_data,
            'today': today,
        })
        
        return context


# ========== PLAN TRIP VIEW ==========
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
                trip.status = 'planning'  # Changed from 'booked' to 'planning'
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
                    status='planning'  # Changed from 'booked' to 'planning'
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
            
            # For AJAX requests, return success with trip_id
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'trip_id': trip.id,
                    'message': 'Trip saved successfully'
                })
            else:
                # For regular form submission, redirect to plan selection
                return redirect('planner:plan_selection', trip_id=trip.id)
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
            else:
                messages.error(request, f'Error saving trip: {str(e)}')
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
# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py

# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# Replace the entire SelectHotelWithMapView class with this:
# C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# Replace the SelectHotelWithMapView class with this SIMPLER version:

class SelectHotelWithMapView(LoginRequiredMixin, View):
    """View for selecting hotels with SIMPLE Google Maps iframe embeds (NO API KEY)"""
    template_name = 'planner/select_hotel_map_simple.html'  # Changed template name
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        nights = trip.calculate_nights()
        
        # Get hotels for this destination from YOUR DATABASE
        hotels = Hotel.objects.filter(
            destination=trip.destination,
            is_active=True
        ).order_by('price_per_night')
        
        # Prepare hotel data with Google Maps embed URL
        hotel_data = []
        for hotel in hotels:
            # Get image URL safely
            image_url = ''
            if hotel.image and hasattr(hotel.image, 'url'):
                try:
                    image_url = hotel.image.url
                except:
                    image_url = ''
            
            # Create Google Maps search query for iframe
            maps_query = f"{hotel.name} {hotel.address} {trip.destination.name} Myanmar"
            maps_query_encoded = urllib.parse.quote(maps_query)
            
            # Generate iframe URL (NO API KEY NEEDED)
            iframe_url = f"https://maps.google.com/maps?width=100%&height=300&hl=en&q={maps_query_encoded}&t=&z=14&ie=UTF8&iwloc=B&output=embed"
            
            hotel_data.append({
                'id': hotel.id,
                'name': hotel.name,
                'address': hotel.address,
                'price': float(hotel.price_per_night),
                'price_display': hotel.price_in_mmk(),
                'rating': float(hotel.rating),
                'review_count': hotel.review_count,
                'category': hotel.category,
                'category_display': hotel.get_category_display(),
                'amenities': hotel.amenities[:5] if hotel.amenities else [],
                'description': hotel.description[:100] + '...' if hotel.description and len(hotel.description) > 100 else (hotel.description or ''),
                'image_url': image_url,
                'phone_number': hotel.phone_number or '',
                'website': hotel.website or '',
                'has_image': bool(image_url),
                'maps_query': maps_query,
                'iframe_url': iframe_url,  # This is the iframe URL for Google Maps
                'has_coordinates': bool(hotel.latitude and hotel.longitude),
            })
        
        context = {
            'trip': trip,
            'hotels': hotel_data,
            'nights': nights,
            'destination_name': trip.destination.name,
            'destination_id': trip.destination.id,
            'today': timezone.now().date(),
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


# ========== SAVE TRANSPORT VIEW ==========
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


# ========== SELECT TRANSPORT VIEW ==========
# ========== SELECT TRANSPORT VIEW ==========
class SelectTransportView(LoginRequiredMixin, View):
    template_name = 'planner/transport_list.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.GET.get('type', 'flight')
        transport_class = request.GET.get('transport_class', 'all')
        
        # Check if trip has dates
        if not trip.start_date:
            messages.error(request, 'Please select travel dates first.')
            return redirect('planner:plan')
        
        travel_date = trip.start_date
        
        transport_items = []
        error_message = None
        
        if transport_type == 'flight':
            # Check if origin and destination exist
            if not trip.origin or not trip.destination:
                error_message = "Please select both origin and destination."
            # Check if both have airports
            elif not self.check_has_airport(trip.origin) or not self.check_has_airport(trip.destination):
                error_message = f"✈️ Air travel not available between these locations. Please check if both {trip.origin.name} and {trip.destination.name} have airports."
            else:
                # Get flights for this specific date
                transport_items = self.get_flights_for_date(trip, travel_date, transport_class)
                
                if not transport_items:
                    error_message = f"⚠️ No flights available on {travel_date.strftime('%B %d, %Y')}. Try a different date or check back later."
            
        elif transport_type == 'bus':
            if not trip.origin or not trip.destination:
                error_message = "Please select both origin and destination."
            else:
                # Get buses for this specific date
                transport_items = self.get_buses_for_date(trip, travel_date, transport_class)
                
                if not transport_items:
                    # Check if route exists but no schedules
                    route_exists = BusService.objects.filter(
                        departure=trip.origin,
                        arrival=trip.destination,
                        is_active=True
                    ).exists()
                    
                    if route_exists:
                        error_message = f"🚌 No bus schedules available for {travel_date.strftime('%B %d')}. Schedules might be sold out or not yet loaded."
                    else:
                        error_message = f"🚌 No direct bus route found from {trip.origin.name} to {trip.destination.name}."
            
        elif transport_type == 'car':
            if not trip.origin:
                error_message = "Please select an origin city."
            else:
                # Get cars available on this date
                transport_items = self.get_cars_for_date(trip, travel_date, transport_class)
                
                if not transport_items:
                    error_message = f"🚗 No cars available for rent in {trip.origin.name} on {travel_date.strftime('%B %d')}. Try a different date or city."
        
        # If no transport available and no error message yet, set generic message
        if not transport_items and not error_message:
            error_message = f"No {transport_type} options available for {travel_date.strftime('%B %d, %Y')}. Please try a different date or transport type."
        
        # DEBUG: Show what we found
        print(f"DEBUG: Transport Type: {transport_type}")
        print(f"DEBUG: Found {len(transport_items)} items")
        print(f"DEBUG: Error Message: {error_message}")
        
        context = {
            'trip': trip,
            'transport_type': transport_type,
            'transport_items': transport_items,
            'transport_class': transport_class,
            'travel_date': travel_date,
            'error_message': error_message,
        }
        
        return render(request, self.template_name, context)
    
    def check_has_airport(self, destination):
        """Check if a destination has an airport using the model method"""
        return destination.has_airport() if destination else False
    
    def get_flights_for_date(self, trip, travel_date, transport_class):
        """Get flights available for specific date"""
        # Get schedules for this date
        flight_schedules = TransportSchedule.objects.filter(
            transport_type='flight',
            travel_date=travel_date,
            is_active=True,
            available_seats__gte=trip.travelers  # Enough seats for all travelers
        )
        
        print(f"DEBUG: Found {flight_schedules.count()} flight schedules for {travel_date}")
        
        # Get actual flight objects
        flight_ids = flight_schedules.values_list('transport_id', flat=True)
        flights = Flight.objects.filter(
            id__in=flight_ids,
            departure=trip.origin,
            arrival=trip.destination,
            is_active=True
        )
        
        print(f"DEBUG: Found {flights.count()} flights for route {trip.origin.name} → {trip.destination.name}")
        
        # Filter by class if specified
        if transport_class != 'all':
            flights = flights.filter(category=transport_class)
        
        # Add schedule info to each flight
        transport_items = []
        for flight in flights:
            schedule = flight_schedules.filter(transport_id=flight.id).first()
            if schedule:
                # Create flight item with schedule data
                flight_item = flight
                flight_item.schedule_price = schedule.price
                flight_item.schedule_available_seats = schedule.available_seats
                flight_item.schedule_date = schedule.travel_date
                flight_item.schedule_id = schedule.id
                transport_items.append(flight_item)
                print(f"DEBUG: Added flight {flight.airline.name} {flight.flight_number} with {schedule.available_seats} seats")
        
        return transport_items
    
    def get_buses_for_date(self, trip, travel_date, transport_class):
        """Get buses available for specific date"""
        # Get schedules for this date
        bus_schedules = TransportSchedule.objects.filter(
            transport_type='bus',
            travel_date=travel_date,
            is_active=True,
            available_seats__gte=trip.travelers
        )
        
        print(f"DEBUG: Found {bus_schedules.count()} bus schedules for {travel_date}")
        
        # Get actual bus objects
        bus_ids = bus_schedules.values_list('transport_id', flat=True)
        buses = BusService.objects.filter(
            id__in=bus_ids,
            departure=trip.origin,
            arrival=trip.destination,
            is_active=True
        )
        
        print(f"DEBUG: Found {buses.count()} buses for route {trip.origin.name} → {trip.destination.name}")
        
        # Filter by class if specified
        if transport_class != 'all':
            if transport_class == 'low':
                buses = buses.filter(bus_type='standard')
            elif transport_class == 'medium':
                buses = buses.filter(bus_type='vip')
            elif transport_class == 'high':
                buses = buses.filter(bus_type='luxury')
        
        # Add schedule info to each bus
        transport_items = []
        for bus in buses:
            schedule = bus_schedules.filter(transport_id=bus.id).first()
            if schedule:
                bus.schedule_price = schedule.price
                bus.schedule_available_seats = schedule.available_seats
                bus.schedule_date = schedule.travel_date
                bus.schedule_id = schedule.id
                transport_items.append(bus)
                print(f"DEBUG: Added bus {bus.company} with {schedule.available_seats} seats")
        
        return transport_items
    
    def get_cars_for_date(self, trip, travel_date, transport_class):
        """Get cars available for specific date"""
        # Get schedules for this date
        car_schedules = TransportSchedule.objects.filter(
            transport_type='car',
            travel_date=travel_date,
            is_active=True,
            available_seats__gte=trip.travelers
        )
        
        print(f"DEBUG: Found {car_schedules.count()} car schedules for {travel_date}")
        
        # Get actual car objects
        car_ids = car_schedules.values_list('transport_id', flat=True)
        cars = CarRental.objects.filter(
            id__in=car_ids,
            location=trip.origin,
            is_available=True
        )
        
        print(f"DEBUG: Found {cars.count()} cars in {trip.origin.name}")
        
        # Filter by class if specified
        if transport_class != 'all':
            if transport_class == 'low':
                cars = cars.filter(car_type='economy')
            elif transport_class == 'medium':
                cars = cars.filter(car_type='suv')
            elif transport_class == 'high':
                cars = cars.filter(car_type='luxury')
        
        # Add schedule info to each car
        transport_items = []
        for car in cars:
            schedule = car_schedules.filter(transport_id=car.id).first()
            if schedule:
                car.schedule_price = schedule.price
                car.schedule_available_seats = schedule.available_seats
                car.schedule_date = schedule.travel_date
                car.schedule_id = schedule.id
                transport_items.append(car)
                print(f"DEBUG: Added car {car.company} {car.car_model} with {schedule.available_seats} seats")
        
        return transport_items
    
    def post(self, request, trip_id):
        """Handle transport selection directly (for cars and simple booking)"""
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.POST.get('transport_type')
        transport_id = request.POST.get('transport_id')
        schedule_id = request.POST.get('schedule_id')
        
        try:
            if transport_type == 'car':
                # Car rental - no seat selection needed
                car = get_object_or_404(CarRental, id=transport_id)
                
                if schedule_id:
                    schedule = get_object_or_404(TransportSchedule, id=schedule_id)
                    price = schedule.price
                else:
                    price = car.price_per_day
                
                trip.transportation_preference = 'car'
                trip.selected_transport = {
                    'type': 'car',
                    'id': transport_id,
                    'schedule_id': schedule_id,
                    'name': f"{car.company} - {car.car_model}",
                    'price': price,
                    'travel_date': trip.start_date.strftime('%Y-%m-%d')
                }
                trip.save()
                
                messages.success(request, f'Car selected: {car.company} - {car.car_model}')
                return redirect('planner:plan_selection', trip_id=trip.id)
                
            elif transport_type in ['flight', 'bus']:
                # Redirect to seat selection
                return redirect('planner:select_seats', 
                              trip_id=trip.id, 
                              transport_id=transport_id,
                              type=transport_type)
            
        except Exception as e:
            messages.error(request, f'Error selecting transport: {str(e)}')
            import traceback
            traceback.print_exc()
            return redirect('planner:select_transport', trip_id=trip.id, 
                          type=transport_type, transport_class='all')
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


# ========== NEW VIEWS FOR PLAN SELECTION ==========

# ========== NEW VIEWS FOR PLAN SELECTION ==========

# ========== NEW VIEWS FOR PLAN SELECTION ==========

# In C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# Update the PlanSelectionView class:

class PlanSelectionView(LoginRequiredMixin, View):
    """Display 3 travel plans (Cultural Explorer, Adventure Seeker, Relaxed Wanderer)"""
    template_name = 'planner/plan_selection.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        # Check if a plan has been selected (check session)
        selected_plan_id = request.session.get(f'selected_plan_{trip_id}')
        plan_selected = bool(selected_plan_id)
        
        # Calculate trip duration
        nights = trip.calculate_nights()
        days = nights + 1 if nights > 0 else 3
        
        # Define the 3 travel plans
        plans = [
            {
                'id': 'cultural',
                'title': 'Cultural Explorer',
                'subtitle': f'Immerse yourself in {trip.destination.name}\'s rich cultural heritage',
                'category': 'Culture & History',
                'duration': f"{days} Days",
                'estimated_cost': self.calculate_plan_cost(days, 'cultural'),
                'highlights': self.get_cultural_highlights(trip.destination),
                'icon': 'fas fa-landmark',
                'color': '#3498db',
                'days': self.generate_cultural_itinerary(trip, days),
                'total_activities': days * 4,
                'is_selected': selected_plan_id == 'cultural'
            },
            {
                'id': 'adventure',
                'title': 'Adventure Seeker',
                'subtitle': f'Active exploration with outdoor activities in {trip.destination.name}',
                'category': 'Active & Adventurous',
                'duration': f"{days} Days",
                'estimated_cost': self.calculate_plan_cost(days, 'adventure'),
                'highlights': self.get_adventure_highlights(trip.destination),
                'icon': 'fas fa-hiking',
                'color': '#2ecc71',
                'days': self.generate_adventure_itinerary(trip, days),
                'total_activities': days * 4,
                'is_selected': selected_plan_id == 'adventure'
            },
            {
                'id': 'relaxed',
                'title': 'Relaxed Wanderer',
                'subtitle': f'Leisurely pace with ample free time in {trip.destination.name}',
                'category': 'Relaxed & Flexible',
                'duration': f"{days} Days",
                'estimated_cost': self.calculate_plan_cost(days, 'relaxed'),
                'highlights': self.get_relaxed_highlights(trip.destination),
                'icon': 'fas fa-spa',
                'color': '#9b59b6',
                'days': self.generate_relaxed_itinerary(trip, days),
                'total_activities': days * 3,
                'is_selected': selected_plan_id == 'relaxed'
            }
        ]
        
        # Check if trip has pending seat selection
        has_pending_seats = False
        if trip.selected_transport and trip.selected_transport.get('is_temporary', False):
            has_pending_seats = True
        
        # Get the selected plan details if a plan is selected
        selected_plan_details = None
        if plan_selected:
            for plan in plans:
                if plan['id'] == selected_plan_id:
                    selected_plan_details = plan
                    break
        
        context = {
            'trip': trip,
            'plans': plans,
            'destination': trip.destination,
            'days': days,
            'nights': nights,
            'destination_name': trip.destination.name,
            'start_date': trip.start_date.strftime('%Y-%m-%d'),
            'end_date': trip.end_date.strftime('%Y-%m-%d'),
            'travelers': trip.travelers,
            'has_pending_seats': has_pending_seats,
            'selected_hotel': trip.selected_hotel,
            'selected_transport': trip.selected_transport,
            'plan_selected': plan_selected,
            'selected_plan_id': selected_plan_id,
            'selected_plan_details': selected_plan_details,
        }
        
        return render(request, self.template_name, context)
    
    # ... keep the rest of your existing methods ...   
    def calculate_plan_cost(self, days, plan_type):
        """Calculate dynamic cost based on destination and days"""
        base_costs = {
            'cultural': 1250,
            'adventure': 1450,
            'relaxed': 1100
        }
        
        base_cost = base_costs.get(plan_type, 1000)
        # Adjust for number of days (base cost is for 3 days)
        return int(base_cost * (days / 3))
    
    def get_cultural_highlights(self, destination):
        """Get destination-specific cultural highlights"""
        destination_name = destination.name.lower()
        
        highlights_map = {
            'yangon': [
                'Shwedagon Pagoda at sunrise',
                'Colonial architecture walking tour',
                'Traditional puppet show',
                'Local tea house experience',
                'Bogyoke Market shopping',
                'National Museum visit'
            ],
            'mandalay': [
                'Mandalay Palace tour',
                'Mandalay Hill sunset view',
                'Gold leaf making workshop',
                'Traditional marionette theater',
                'Kuthodaw Pagoda (World\'s largest book)',
                'U Bein Bridge at sunrise'
            ],
            'bagan': [
                'Temple sunrise hot air balloon',
                'Ancient temple exploration',
                'Lacquerware workshop visit',
                'Traditional horse cart ride',
                'Local village life experience',
                'Sunset at Buledi temple'
            ],
            'inle lake': [
                'Leg-rowing fishermen demonstration',
                'Floating village tour',
                'Traditional weaving workshop',
                'Phaung Daw Oo Pagoda visit',
                'Local market experience',
                'Stilt house village walk'
            ],
            'pyin oo lwin': [
                'Botanical gardens tour',
                'Colonial architecture walk',
                'Candy factory visit',
                'Local strawberry farm',
                'Waterfall visits',
                'Horse carriage ride'
            ]
        }
        
        # Find matching highlights
        for key, highlights in highlights_map.items():
            if key in destination_name or destination_name in key:
                return highlights
        
        # Default highlights for other destinations
        return [
            'Local cultural sites visit',
            'Traditional craft workshop',
            'Historical landmark tour',
            'Local market exploration',
            'Cultural performance show',
            'Traditional cuisine tasting'
        ]
    
    def get_adventure_highlights(self, destination):
        """Get destination-specific adventure highlights"""
        destination_name = destination.name.lower()
        
        highlights_map = {
            'yangon': [
                'Circular train ride',
                'Kayaking on Kandawgyi Lake',
                'Street food walking tour',
                'Bicycle tour around city',
                'Yangon River cruise',
                'Night market exploration'
            ],
            'mandalay': [
                'Mandalay Hill hiking',
                'Mingun day trip by boat',
                'Motorbike tour around city',
                'Traditional cooking class',
                'Irrawaddy River activities',
                'Local market food adventure'
            ],
            'bagan': [
                'Hot air balloon ride',
                'E-bike temple exploration',
                'Sunrise cycling tour',
                'Irrawaddy River boat trip',
                'Temple climbing adventure',
                'Photography safari'
            ],
            'inle lake': [
                'Boat tour on Inle Lake',
                'Trekking to hill tribe villages',
                'Bamboo rafting experience',
                'Fishing with local methods',
                'Mountain biking around lake',
                'Sunrise boat photography'
            ],
            'ngapali': [
                'Beach relaxation',
                'Snorkeling adventure',
                'Sunset fishing trip',
                'Beach volleyball',
                'Local seafood tasting',
                'Coastal walk exploration'
            ]
        }
        
        for key, highlights in highlights_map.items():
            if key in destination_name or destination_name in key:
                return highlights
        
        # Default highlights
        return [
            'Local hiking trails',
            'Outdoor exploration',
            'Traditional activities',
            'Nature walks',
            'Adventure sports',
            'Cultural adventures'
        ]
    
    def get_relaxed_highlights(self, destination):
        """Get destination-specific relaxed highlights"""
        destination_name = destination.name.lower()
        
        highlights_map = {
            'yangon': [
                'Spa and wellness sessions',
                'Leisurely park walks',
                'Café hopping downtown',
                'Sunset at Shwedagon',
                'Riverfront relaxation',
                'Art gallery visits'
            ],
            'mandalay': [
                'Spa treatments',
                'Royal garden walks',
                'Tea house relaxation',
                'Sunset viewing spots',
                'Cultural show evenings',
                'Leisurely shopping'
            ],
            'bagan': [
                'Temple view relaxation',
                'Sunset champagne viewing',
                'Poolside lounging',
                'Leisurely e-bike rides',
                'Traditional massage',
                'Stargazing nights'
            ],
            'inle lake': [
                'Lakeside relaxation',
                'Boat ride with tea',
                'Spa with lake view',
                'Leisurely village walks',
                'Sunset photography',
                'Traditional massage'
            ],
            'ngapali': [
                'Beachfront massage',
                'Sunset beach walks',
                'Hammock relaxation',
                'Seafood dining',
                'Beach yoga sessions',
                'Poolside lounging'
            ]
        }
        
        for key, highlights in highlights_map.items():
            if key in destination_name or destination_name in key:
                return highlights
        
        # Default highlights
        return [
            'Spa and wellness sessions',
            'Leisurely nature walks',
            'Local café exploration',
            'Sunset photography spots',
            'Relaxation activities',
            'Cultural appreciation'
        ]
    
    def generate_cultural_itinerary(self, trip, days):
        """Generate cultural itinerary for specific destination"""
        itinerary = []
        destination_name = trip.destination.name.lower()
        
        # Define destination-specific activities
        activities_map = {
            'yangon': [
                {'time': '09:00 AM', 'title': 'Shwedagon Pagoda Visit', 'location': 'Shwedagon Pagoda', 'duration': '2 hours', 'description': 'Explore Myanmar\'s most sacred Buddhist pagoda', 'type': 'cultural'},
                {'time': '12:00 PM', 'title': 'Lunch at Feel Myanmar', 'location': 'Traditional Restaurant', 'duration': '1.5 hours', 'description': 'Authentic Myanmar cuisine experience', 'type': 'food'},
                {'time': '02:00 PM', 'title': 'Bogyoke Market', 'location': 'Pabedan Township', 'duration': '2 hours', 'description': 'Shop for local crafts, jewelry and souvenirs', 'type': 'shopping'},
                {'time': '05:00 PM', 'title': 'Colonial Architecture Tour', 'location': 'Downtown Yangon', 'duration': '1.5 hours', 'description': 'Walk through historic colonial buildings', 'type': 'cultural'}
            ],
            'mandalay': [
                {'time': '08:00 AM', 'title': 'Mandalay Palace', 'location': 'Mandalay Palace', 'duration': '2 hours', 'description': 'Explore the last royal palace of Myanmar', 'type': 'cultural'},
                {'time': '11:00 AM', 'title': 'Gold Leaf Workshop', 'location': 'Traditional Workshop', 'duration': '1.5 hours', 'description': 'See how traditional gold leaf is made', 'type': 'workshop'},
                {'time': '02:00 PM', 'title': 'Kuthodaw Pagoda', 'location': 'Mandalay Hill', 'duration': '2 hours', 'description': 'Visit the world\'s largest book', 'type': 'cultural'},
                {'time': '05:00 PM', 'title': 'Sunset at U Bein Bridge', 'location': 'Amarapura', 'duration': '1.5 hours', 'description': 'Watch sunset on the world\'s longest teak bridge', 'type': 'scenic'}
            ],
            'bagan': [
                {'time': '05:30 AM', 'title': 'Hot Air Balloon Sunrise', 'location': 'Bagan Plains', 'duration': '1 hour', 'description': 'Spectacular sunrise view over ancient temples', 'type': 'adventure'},
                {'time': '09:00 AM', 'title': 'Ananda Temple', 'location': 'Old Bagan', 'duration': '2 hours', 'description': 'Visit one of Bagan\'s most beautiful temples', 'type': 'cultural'},
                {'time': '01:00 PM', 'title': 'Lacquerware Workshop', 'location': 'Myinkaba Village', 'duration': '2 hours', 'description': 'Learn about traditional lacquerware making', 'type': 'workshop'},
                {'time': '05:00 PM', 'title': 'Sunset at Buledi', 'location': 'Bagan Archaeological Zone', 'duration': '1.5 hours', 'description': 'Climb a temple for panoramic sunset views', 'type': 'scenic'}
            ],
            'inle lake': [
                {'time': '07:00 AM', 'title': 'Leg-Rowing Fishermen', 'location': 'Inle Lake', 'duration': '2 hours', 'description': 'See unique leg-rowing fishing technique', 'type': 'cultural'},
                {'time': '10:00 AM', 'title': 'Floating Village Tour', 'location': 'Inle Lake', 'duration': '2 hours', 'description': 'Visit stilt-house villages on the lake', 'type': 'cultural'},
                {'time': '01:00 PM', 'title': 'Traditional Weaving', 'location': 'Inn Paw Khon Village', 'duration': '2 hours', 'description': 'Watch lotus and silk weaving process', 'type': 'workshop'},
                {'time': '04:00 PM', 'title': 'Phaung Daw Oo Pagoda', 'location': 'Inle Lake', 'duration': '1.5 hours', 'description': 'Visit the lake\'s most important pagoda', 'type': 'cultural'}
            ]
        }
        
        # Get activities for this destination
        base_activities = activities_map.get(destination_name, [
            {'time': '09:00 AM', 'title': 'Cultural Site Visit', 'location': 'Main Attraction', 'duration': '2 hours', 'description': f'Explore cultural sites in {trip.destination.name}', 'type': 'cultural'},
            {'time': '12:00 PM', 'title': 'Local Cuisine Lunch', 'location': 'Traditional Restaurant', 'duration': '1.5 hours', 'description': 'Taste authentic local dishes', 'type': 'food'},
            {'time': '02:00 PM', 'title': 'Market Exploration', 'location': 'Local Market', 'duration': '2 hours', 'description': 'Experience local market culture', 'type': 'shopping'},
            {'time': '05:00 PM', 'title': 'Sunset Viewing', 'location': 'Scenic Spot', 'duration': '1.5 hours', 'description': 'Enjoy beautiful sunset views', 'type': 'scenic'}
        ])
        
        # Add icons to activities
        icon_map = {
            'cultural': 'fas fa-landmark',
            'food': 'fas fa-utensils',
            'shopping': 'fas fa-shopping-bag',
            'workshop': 'fas fa-hammer',
            'scenic': 'fas fa-camera',
            'adventure': 'fas fa-hiking'
        }
        
        for activity in base_activities:
            activity['icon'] = icon_map.get(activity['type'], 'fas fa-star')
        
        # Generate itinerary for each day
        for day in range(1, days + 1):
            # Vary activities slightly each day
            day_activities = []
            for i, activity in enumerate(base_activities):
                # Create a copy to modify
                activity_copy = activity.copy()
                
                # Vary times slightly for different days
                if day > 1:
                    time_parts = activity_copy['time'].split(' ')
                    hour_part = time_parts[0]
                    am_pm = time_parts[1] if len(time_parts) > 1 else 'AM'
                    hour = int(hour_part.split(':')[0])
                    
                    # Add 30 minutes for each subsequent day
                    hour_offset = (day - 1) * 0.5
                    new_hour = hour + hour_offset
                    
                    if new_hour >= 12 and am_pm == 'AM':
                        am_pm = 'PM'
                        if new_hour > 12:
                            new_hour -= 12
                    
                    activity_copy['time'] = f"{int(new_hour):02d}:{hour_part.split(':')[1]} {am_pm}"
                
                day_activities.append(activity_copy)
            
            itinerary.append({
                'day_number': day,
                'date': self.calculate_date(trip.start_date, day - 1),
                'activities': day_activities
            })
        
        return itinerary
    
    def generate_adventure_itinerary(self, trip, days):
        """Generate adventure itinerary for specific destination"""
        itinerary = []
        destination_name = trip.destination.name.lower()
        
        # Define destination-specific adventure activities
        activities_map = {
            'yangon': [
                {'time': '07:00 AM', 'title': 'Circular Train Ride', 'location': 'Yangon Central Station', 'duration': '3 hours', 'description': 'Experience local life on the circular railway', 'type': 'adventure'},
                {'time': '11:00 AM', 'title': 'Street Food Tour', 'location': 'Downtown Markets', 'duration': '2 hours', 'description': 'Taste authentic Yangon street food', 'type': 'food'},
                {'time': '02:00 PM', 'title': 'Kayaking on Lake', 'location': 'Kandawgyi Lake', 'duration': '2.5 hours', 'description': 'Paddle through scenic waters', 'type': 'water_sports'},
                {'time': '06:00 PM', 'title': 'Sunset Walking Tour', 'location': 'Downtown Area', 'duration': '2 hours', 'description': 'Explore the city at sunset', 'type': 'walking'}
            ],
            'mandalay': [
                {'time': '06:00 AM', 'title': 'Mandalay Hill Hike', 'location': 'Mandalay Hill', 'duration': '2 hours', 'description': 'Hike to the top for panoramic views', 'type': 'hiking'},
                {'time': '10:00 AM', 'title': 'Motorbike City Tour', 'location': 'Mandalay City', 'duration': '3 hours', 'description': 'Explore Mandalay on motorbike', 'type': 'adventure'},
                {'time': '02:00 PM', 'title': 'Mingun Boat Trip', 'location': 'Irrawaddy River', 'duration': '3 hours', 'description': 'Boat trip to Mingun ancient sites', 'type': 'boat'},
                {'time': '06:00 PM', 'title': 'Traditional Cooking Class', 'location': 'Local Kitchen', 'duration': '2 hours', 'description': 'Learn to cook Mandalay dishes', 'type': 'food'}
            ],
            'bagan': [
                {'time': '05:00 AM', 'title': 'Sunrise E-Bike Tour', 'location': 'Bagan Plains', 'duration': '3 hours', 'description': 'Explore temples by e-bike at sunrise', 'type': 'cycling'},
                {'time': '09:00 AM', 'title': 'Horse Cart Adventure', 'location': 'Ancient Temples', 'duration': '2 hours', 'description': 'Traditional horse cart temple tour', 'type': 'cultural'},
                {'time': '02:00 PM', 'title': 'Irrawaddy River Cruise', 'location': 'Irrawaddy River', 'duration': '2.5 hours', 'description': 'Boat trip on the mighty river', 'type': 'boat'},
                {'time': '06:00 PM', 'title': 'Sunset Temple Climb', 'location': 'Selected Temple', 'duration': '1.5 hours', 'description': 'Climb a temple for sunset views', 'type': 'hiking'}
            ],
            'inle lake': [
                {'time': '06:00 AM', 'title': 'Sunrise Boat Tour', 'location': 'Inle Lake', 'duration': '3 hours', 'description': 'Early morning boat tour of the lake', 'type': 'boat'},
                {'time': '10:00 AM', 'title': 'Trekking to Villages', 'location': 'Shan Hills', 'duration': '3 hours', 'description': 'Trek to remote hill tribe villages', 'type': 'hiking'},
                {'time': '02:00 PM', 'title': 'Bamboo Rafting', 'location': 'Streams near Lake', 'duration': '2 hours', 'description': 'Traditional bamboo raft experience', 'type': 'water_sports'},
                {'time': '05:00 PM', 'title': 'Bicycle Lake Tour', 'location': 'Lakeside Roads', 'duration': '2 hours', 'description': 'Cycle around the lake perimeter', 'type': 'cycling'}
            ]
        }
        
        base_activities = activities_map.get(destination_name, [
            {'time': '08:00 AM', 'title': 'Morning Exploration', 'location': 'Main Area', 'duration': '3 hours', 'description': f'Active exploration of {trip.destination.name}', 'type': 'adventure'},
            {'time': '12:00 PM', 'title': 'Local Food Experience', 'location': 'Traditional Restaurant', 'duration': '1.5 hours', 'description': 'Try local adventure foods', 'type': 'food'},
            {'time': '02:00 PM', 'title': 'Outdoor Activity', 'location': 'Natural Site', 'duration': '2.5 hours', 'description': 'Participate in local outdoor activities', 'type': 'adventure'},
            {'time': '05:00 PM', 'title': 'Evening Adventure', 'location': 'Scenic Location', 'duration': '2 hours', 'description': 'Evening adventure activities', 'type': 'adventure'}
        ])
        
        # Add icons
        icon_map = {
            'adventure': 'fas fa-hiking',
            'food': 'fas fa-utensils',
            'hiking': 'fas fa-mountain',
            'cycling': 'fas fa-bicycle',
            'boat': 'fas fa-ship',
            'water_sports': 'fas fa-water',
            'walking': 'fas fa-walking'
        }
        
        for activity in base_activities:
            activity['icon'] = icon_map.get(activity['type'], 'fas fa-compass')
        
        # Generate itinerary for each day
        for day in range(1, days + 1):
            day_activities = []
            for i, activity in enumerate(base_activities):
                activity_copy = activity.copy()
                
                # Vary activities for different days
                if day > 1:
                    # Change some activities for variety
                    if i == 2:  # Third activity
                        if 'hiking' in activity_copy['type']:
                            activity_copy['title'] = 'Nature Walk Exploration'
                        elif 'boat' in activity_copy['type']:
                            activity_copy['title'] = 'River/Lake Exploration'
                
                day_activities.append(activity_copy)
            
            itinerary.append({
                'day_number': day,
                'date': self.calculate_date(trip.start_date, day - 1),
                'activities': day_activities
            })
        
        return itinerary
    
    def generate_relaxed_itinerary(self, trip, days):
        """Generate relaxed itinerary for specific destination"""
        itinerary = []
        destination_name = trip.destination.name.lower()
        
        # Define destination-specific relaxed activities
        activities_map = {
            'yangon': [
                {'time': '10:00 AM', 'title': 'Late Breakfast', 'location': 'Hotel Restaurant', 'duration': '1.5 hours', 'description': 'Leisurely morning meal', 'type': 'food'},
                {'time': '12:00 PM', 'title': 'Spa & Wellness', 'location': 'City Spa', 'duration': '2 hours', 'description': 'Relaxing massage and treatments', 'type': 'wellness'},
                {'time': '03:00 PM', 'title': 'Park Walk', 'location': 'Kandawgyi Park', 'duration': '1.5 hours', 'description': 'Gentle walk in beautiful park', 'type': 'walking'},
                {'time': '05:00 PM', 'title': 'Sunset Photography', 'location': 'Shwedagon Pagoda', 'duration': '1 hour', 'description': 'Capture beautiful sunset moments', 'type': 'photography'}
            ],
            'mandalay': [
                {'time': '10:00 AM', 'title': 'Royal Garden Visit', 'location': 'Mandalay Palace Gardens', 'duration': '2 hours', 'description': 'Leisurely walk in royal gardens', 'type': 'walking'},
                {'time': '01:00 PM', 'title': 'Traditional Spa', 'location': 'Local Wellness Center', 'duration': '2 hours', 'description': 'Traditional Myanmar spa treatments', 'type': 'wellness'},
                {'time': '04:00 PM', 'title': 'Tea House Relaxation', 'location': 'Local Tea House', 'duration': '1.5 hours', 'description': 'Relax with local tea culture', 'type': 'food'},
                {'time': '06:00 PM', 'title': 'Sunset River View', 'location': 'Irrawaddy Riverfront', 'duration': '1 hour', 'description': 'Peaceful sunset by the river', 'type': 'scenic'}
            ],
            'bagan': [
                {'time': '09:00 AM', 'title': 'Poolside Breakfast', 'location': 'Hotel Pool', 'duration': '1.5 hours', 'description': 'Relaxed breakfast with temple views', 'type': 'food'},
                {'time': '11:00 AM', 'title': 'Temple View Massage', 'location': 'Spa with View', 'duration': '2 hours', 'description': 'Massage with ancient temple views', 'type': 'wellness'},
                {'time': '03:00 PM', 'title': 'Leisurely E-Bike Ride', 'location': 'Quiet Temple Area', 'duration': '1.5 hours', 'description': 'Gentle e-bike ride to quiet temples', 'type': 'cycling'},
                {'time': '05:00 PM', 'title': 'Sunset Champagne', 'location': 'Sunset Viewpoint', 'duration': '1.5 hours', 'description': 'Champagne while watching sunset', 'type': 'scenic'}
            ],
            'inle lake': [
                {'time': '09:30 AM', 'title': 'Lakeside Breakfast', 'location': 'Lake View Restaurant', 'duration': '1.5 hours', 'description': 'Breakfast overlooking the lake', 'type': 'food'},
                {'time': '11:30 AM', 'title': 'Floating Spa Treatment', 'location': 'Lake Spa', 'duration': '2 hours', 'description': 'Spa treatments on the water', 'type': 'wellness'},
                {'time': '03:00 PM', 'title': 'Gentle Boat Ride', 'location': 'Inle Lake', 'duration': '2 hours', 'description': 'Leisurely boat tour of the lake', 'type': 'boat'},
                {'time': '05:30 PM', 'title': 'Lakeside Sunset', 'location': 'Lake Shore', 'duration': '1 hour', 'description': 'Peaceful sunset by the lake', 'type': 'scenic'}
            ]
        }
        
        base_activities = activities_map.get(destination_name, [
            {'time': '10:00 AM', 'title': 'Leisurely Breakfast', 'location': 'Hotel Restaurant', 'duration': '1.5 hours', 'description': 'Relaxed morning meal', 'type': 'food'},
            {'time': '12:00 PM', 'title': 'Wellness Session', 'location': 'Local Spa', 'duration': '2 hours', 'description': 'Relaxation and wellness treatments', 'type': 'wellness'},
            {'time': '03:00 PM', 'title': 'Gentle Exploration', 'location': 'Scenic Area', 'duration': '1.5 hours', 'description': f'Leisurely exploration of {trip.destination.name}', 'type': 'walking'},
            {'time': '05:00 PM', 'title': 'Sunset Viewing', 'location': 'Best View Spot', 'duration': '1 hour', 'description': 'Enjoy beautiful sunset views', 'type': 'scenic'}
        ])
        
        # Add icons
        icon_map = {
            'food': 'fas fa-utensils',
            'wellness': 'fas fa-spa',
            'walking': 'fas fa-walking',
            'photography': 'fas fa-camera',
            'scenic': 'fas fa-eye',
            'cycling': 'fas fa-bicycle',
            'boat': 'fas fa-ship'
        }
        
        for activity in base_activities:
            activity['icon'] = icon_map.get(activity['type'], 'fas fa-star')
        
        # Generate itinerary for each day
        for day in range(1, days + 1):
            itinerary.append({
                'day_number': day,
                'date': self.calculate_date(trip.start_date, day - 1),
                'activities': base_activities.copy()  # Same relaxed schedule each day
            })
        
        return itinerary
    
    def calculate_date(self, start_date, day_offset):
        """Calculate date for a specific day"""
        from datetime import timedelta
        return (start_date + timedelta(days=day_offset)).strftime('%Y-%m-%d')

# In C:\Users\ASUS\MyanmarTravelPlanner\planner\views.py
# Update the SelectPlanView class:

class SelectPlanView(LoginRequiredMixin, View):
    """Handle plan selection and redirect to detailed itinerary"""
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        plan_id = request.POST.get('plan_id')
        
        if not plan_id:
            messages.error(request, 'Please select a plan.')
            return redirect('planner:plan_selection', trip_id=trip.id)
        
        # Store selected plan in session
        request.session[f'selected_plan_{trip.id}'] = plan_id
        
        messages.success(request, f'✅ Plan selected successfully! You can now confirm your trip.')
        
        # Redirect back to plan selection page to show confirmation section
        return redirect('planner:plan_selection', trip_id=trip.id)



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
        weather_forecast = self.get_weather_forecast_for_trip(trip)
        
        # Get trip cost estimate
        cost_estimate = self.calculate_cost_estimate(trip, plan_id)
        
        # Get selected hotel and transport
        hotel = trip.selected_hotel
        transport = trip.selected_transport
        
        # Calculate nights
        nights = trip.calculate_nights()
        
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
            'start_date': trip.start_date.strftime('%Y-%m-%d'),
            'end_date': trip.end_date.strftime('%Y-%m-%d'),
            'travelers': trip.travelers,
            'nights': nights,
        }
        
        return render(request, self.template_name, context)
    
    def get_weather_forecast_for_trip(self, trip):
        """Get weather forecast for the trip destination and dates"""
        try:
            from .weather_service import weather_service
            
            # Use the destination name
            destination_name = trip.destination.name
            
            print(f"Fetching weather for {destination_name} from {trip.start_date} to {trip.end_date}")
            
            # Get forecast using the weather service
            forecast = weather_service.get_weather_forecast(
                destination_name,
                trip.start_date.strftime('%Y-%m-%d'),
                trip.end_date.strftime('%Y-%m-%d')
            )
            
            if forecast:
                print(f"Successfully got weather forecast with {len(forecast)} days")
                # Check if we got real data or mock data
                first_date = list(forecast.keys())[0] if forecast else None
                if first_date and forecast[first_date].get('is_mock', True):
                    print("Using mock weather data (API may be unavailable)")
                else:
                    print("Using real weather data from API")
                
                return forecast
            else:
                print("No forecast data received, using mock data")
                return self.generate_mock_weather_forecast(trip.start_date, trip.end_date)
                
        except Exception as e:
            print(f"Error getting weather forecast: {e}")
            import traceback
            traceback.print_exc()
            return self.generate_mock_weather_forecast(trip.start_date, trip.end_date)
    
    def generate_mock_weather_forecast(self, start_date, end_date):
        """Generate realistic mock weather data for Myanmar"""
        from datetime import timedelta
        import random
        
        forecasts = {}
        current_date = start_date
        days = (end_date - start_date).days + 1
        
        # Typical Myanmar weather conditions
        myanmar_weather = [
            {'description': 'Sunny', 'icon': '01d', 'temp_range': (28, 35), 'probability': 0.4},
            {'description': 'Partly Cloudy', 'icon': '02d', 'temp_range': (26, 32), 'probability': 0.3},
            {'description': 'Cloudy', 'icon': '03d', 'temp_range': (24, 30), 'probability': 0.2},
            {'description': 'Light Rain', 'icon': '10d', 'temp_range': (23, 28), 'probability': 0.1},
        ]
        
        # Weighted random selection based on probability
        for i in range(days):
            date_str = current_date.strftime('%Y-%m-%d')
            day_name = current_date.strftime('%A')
            
            # Select weather condition based on probability
            rand_val = random.random()
            cumulative = 0
            condition = None
            
            for weather in myanmar_weather:
                cumulative += weather['probability']
                if rand_val <= cumulative:
                    condition = weather
                    break
            
            if not condition:
                condition = myanmar_weather[0]  # Default to sunny
            
            # Generate temperature
            temp = random.randint(condition['temp_range'][0], condition['temp_range'][1])
            
            # Generate hourly forecasts (4 key times of day)
            hourly_forecasts = []
            time_slots = [
                {'hour': 8, 'name': 'Morning', 'temp_adjust': -2},
                {'hour': 12, 'name': 'Noon', 'temp_adjust': 0},
                {'hour': 16, 'name': 'Afternoon', 'temp_adjust': 1},
                {'hour': 20, 'name': 'Evening', 'temp_adjust': -1},
            ]
            
            for slot in time_slots:
                hour_temp = temp + slot['temp_adjust'] + random.randint(-1, 1)
                hourly_forecasts.append({
                    'time': f"{slot['hour']:02d}:00",
                    'temperature': hour_temp,
                    'description': condition['description'],
                    'icon': condition['icon'],
                    'feels_like': hour_temp + random.randint(-1, 1),
                    'humidity': random.randint(50, 80),
                    'wind_speed': round(random.uniform(1.0, 5.0), 1),
                })
            
            # Determine min and max temps
            hourly_temps = [h['temperature'] for h in hourly_forecasts]
            min_temp = min(hourly_temps)
            max_temp = max(hourly_temps)
            
            # Noon forecast is usually used as daily summary
            noon_forecast = hourly_forecasts[1]  # 12:00
            
            forecasts[date_str] = {
                'date': date_str,
                'day_name': day_name,
                'daily_summary': {
                    'temperature': noon_forecast['temperature'],
                    'description': noon_forecast['description'],
                    'icon': noon_forecast['icon'],
                },
                'hourly_forecasts': hourly_forecasts,
                'min_temp': min_temp,
                'max_temp': max_temp,
                'is_mock': True,
            }
            
            current_date += timedelta(days=1)
        
        return forecasts
    
    def calculate_cost_estimate(self, trip, plan_id):
        """Calculate cost estimate based on plan IN MMK"""
        nights = trip.calculate_nights()
        days = nights + 1 if nights > 0 else 3
        
        # Get cost breakdown from trip
        breakdown = trip.get_cost_breakdown()
        
        # Adjust based on plan type
        plan_multipliers = {
            'cultural': 1.0,
            'adventure': 1.15,  # 15% more for adventure
            'relaxed': 0.9,     # 10% less for relaxed
        }
        
        multiplier = plan_multipliers.get(plan_id, 1.0)
        
        # Apply plan multiplier to destination activities cost
        if 'destination' in breakdown:
            breakdown['destination'] = int(breakdown['destination'] * multiplier)
        
        # Recalculate total
        breakdown['total'] = sum([
            breakdown.get('hotel', 0),
            breakdown.get('transport', 0),
            breakdown.get('destination', 0),
            breakdown.get('additional_travelers', 0)
        ])
        
        return {
            'total': breakdown['total'],
            'breakdown': breakdown
        }  

class AddActivityView(LoginRequiredMixin, View):
    """Add a new activity to itinerary"""
    def post(self, request, trip_id, plan_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        try:
            data = json.loads(request.body)
            day_number = data.get('day_number')
            activity_data = data.get('activity')
            
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
            
            return JsonResponse({
                'success': True,
                'message': 'Activity removed successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class DownloadItineraryPDFView(LoginRequiredMixin, View):
    """Generate and download itinerary as PDF"""
    def get(self, request, trip_id, plan_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        try:
            # For now, we'll create a simple HTML response
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


class TestWeatherAPIView(LoginRequiredMixin, View):
    """View to test weather API from browser"""
    def get(self, request):
        from .weather_service import weather_service
        import requests
        
        results = {
            'api_key_configured': bool(getattr(settings, 'OPENWEATHER_API_KEY', '')),
            'tests': []
        }
        
        # Test 1: Direct API call
        test_cases = [
            ("Yangon", "MM"),
            ("Mandalay", "MM"),
        ]
        
        for city, country in test_cases:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={weather_service.api_key}&units=metric"
            
            try:
                response = requests.get(url, timeout=5)
                data = response.json()
                
                if data.get('cod') == 200:
                    results['tests'].append({
                        'city': city,
                        'status': 'success',
                        'temperature': data['main']['temp'],
                        'description': data['weather'][0]['description'],
                        'message': 'API working'
                    })
                else:
                    results['tests'].append({
                        'city': city,
                        'status': 'api_error',
                        'message': data.get('message', 'Unknown API error')
                    })
                    
            except Exception as e:
                results['tests'].append({
                    'city': city,
                    'status': 'error',
                    'message': str(e)
                })
        
        # Test 2: Using weather service
        try:
            weather_data = weather_service.get_weather_by_city("Yangon")
            results['weather_service_test'] = {
                'status': 'success' if not weather_data.get('is_mock') else 'using_mock',
                'temperature': weather_data.get('temperature'),
                'is_mock': weather_data.get('is_mock', True),
                'message': 'Using real data' if not weather_data.get('is_mock') else 'Using mock data (API may be unavailable)'
            }
        except Exception as e:
            results['weather_service_test'] = {
                'status': 'error',
                'message': str(e)
            }
        
        return JsonResponse(results)
# ========== DESTINATION BROWSING VIEWS ==========

class DestinationListView(View):
    """Browse destinations by region/city"""
    template_name = 'planner/destinations.html'
    
    def get(self, request):
        # Get filter parameters
        region_filter = request.GET.get('region', 'all')
        type_filter = request.GET.get('type', 'all')
        search_query = request.GET.get('search', '')
        
        # Get all destinations
        destinations = Destination.objects.filter(is_active=True)
        
        # Apply filters
        if region_filter != 'all':
            destinations = destinations.filter(region__iexact=region_filter)
        
        if type_filter != 'all':
            destinations = destinations.filter(type=type_filter)
        
        if search_query:
            destinations = destinations.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(region__icontains=search_query)
            )
        
        # Group by region
        destinations_by_region = {}
        for destination in destinations.order_by('region', 'name'):
            region = destination.region
            if region not in destinations_by_region:
                destinations_by_region[region] = []
            destinations_by_region[region].append(destination)
        
        # Get unique regions for filter
        all_regions = Destination.objects.filter(is_active=True).values_list('region', flat=True).distinct()
        all_types = Destination.objects.filter(is_active=True).values_list('type', flat=True).distinct()
        
        context = {
            'destinations_by_region': destinations_by_region,
            'all_regions': all_regions,
            'all_types': all_types,
            'selected_region': region_filter,
            'selected_type': type_filter,
            'search_query': search_query,
            'destinations_count': destinations.count(),
        }
        
        return render(request, self.template_name, context)


class DestinationDetailView(View):
    """Detailed view of a destination"""
    template_name = 'planner/destination_detail.html'
    
    def get(self, request, destination_id):
        destination = get_object_or_404(Destination, id=destination_id, is_active=True)
        
        # Get weather forecast for this destination
        weather_service_instance = weather_service
        weather_data = weather_service_instance.get_weather_by_city(destination.name)
        
        # Get hotels in this destination
        hotels = Hotel.objects.filter(destination=destination, is_active=True).order_by('price_per_night')[:5]
        
        # Get similar destinations (same region)
        similar_destinations = Destination.objects.filter(
            region=destination.region,
            is_active=True
        ).exclude(id=destination.id).order_by('?')[:4]
        
        # Get popular attractions (for major cities)
        attractions = []
        if destination.name.lower() in ['yangon', 'mandalay', 'bagan']:
            attractions = self.get_popular_attractions(destination.name)
        
        context = {
            'destination': destination,
            'weather_data': weather_data,
            'hotels': hotels,
            'similar_destinations': similar_destinations,
            'attractions': attractions,
            'has_coordinates': bool(destination.latitude and destination.longitude),
        }
        
        return render(request, self.template_name, context)
    
    def get_popular_attractions(self, city_name):
        """Get popular attractions for major cities"""
        attractions_map = {
            'yangon': [
                {'name': 'Shwedagon Pagoda', 'type': 'Religious Site', 'description': 'Gilded pagoda with beautiful sunset views'},
                {'name': 'Bogyoke Market', 'type': 'Market', 'description': 'Colonial-era market with local crafts'},
                {'name': 'Kandawgyi Park', 'type': 'Park', 'description': 'Beautiful park with royal barge'},
                {'name': 'Sule Pagoda', 'type': 'Religious Site', 'description': 'Ancient pagoda in city center'},
                {'name': 'National Museum', 'type': 'Museum', 'description': 'Largest museum in Myanmar'},
            ],
            'mandalay': [
                {'name': 'Mandalay Palace', 'type': 'Historical Site', 'description': 'Last royal palace of Myanmar'},
                {'name': 'Mandalay Hill', 'type': 'Natural Site', 'description': 'Hill with panoramic city views'},
                {'name': 'U Bein Bridge', 'type': 'Bridge', 'description': 'World\'s longest teak bridge'},
                {'name': 'Kuthodaw Pagoda', 'type': 'Religious Site', 'description': 'Home to the world\'s largest book'},
                {'name': 'Mingun Pahtodawgyi', 'type': 'Historical Site', 'description': 'Massive unfinished stupa'},
            ],
            'bagan': [
                {'name': 'Ananda Temple', 'type': 'Temple', 'description': 'One of Bagan\'s most beautiful temples'},
                {'name': 'Shwezigon Pagoda', 'type': 'Pagoda', 'description': 'Gilded pagoda built in 11th century'},
                {'name': 'Dhammayangyi Temple', 'type': 'Temple', 'description': 'Largest temple in Bagan'},
                {'name': 'Sunset at Buledi', 'type': 'Viewpoint', 'description': 'Popular sunset viewing spot'},
                {'name': 'Hot Air Balloon Ride', 'type': 'Activity', 'description': 'Spectacular sunrise over temples'},
            ]
        }
        
        city_lower = city_name.lower()
        for key, attractions in attractions_map.items():
            if key in city_lower:
                return attractions
        
        return []


class DestinationAutocompleteView(View):
    """AJAX endpoint for destination autocomplete"""
    def get(self, request):
        query = request.GET.get('q', '').strip().lower()
        
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        destinations = Destination.objects.filter(
            Q(name__icontains=query) | 
            Q(region__icontains=query),
            is_active=True
        ).order_by('name')[:10]
        
        results = []
        for dest in destinations:
            results.append({
                'id': dest.id,
                'name': dest.name,
                'region': dest.region,
                'type': dest.get_type_display(),
                'full_name': f"{dest.name}, {dest.region}",
                'image_url': dest.image.url if dest.image else '',
            })
        
        return JsonResponse({'results': results})
# ========== NEW VIEWS FOR CARD CLICKS ==========

class TripListView(LoginRequiredMixin, TemplateView):
    """View for showing all trips when clicking 'Total Trips' card"""
    template_name = 'planner/trip_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get all trips for this user
        trips = TripPlan.objects.filter(user=user).order_by('-created_at')
        
        # Categorize trips
        upcoming_trips = trips.filter(
            status__in=['draft', 'planning', 'booked'],
            start_date__gte=timezone.now().date()
        )
        
        completed_trips = trips.filter(status='completed')
        
        # Prepare trip data for template
        trip_data = []
        for trip in trips:
            trip_data.append({
                'id': trip.id,
                'origin': trip.origin.name if trip.origin else 'Not specified',
                'destination': trip.destination.name if trip.destination else 'Not specified',
                'start_date': trip.start_date,
                'end_date': trip.end_date,
                'total_days': trip.calculate_nights() + 1,
                'status': trip.status,
                'status_display': trip.get_status_display(),
                'total_cost_mmk': trip.get_total_cost_in_mmk(),
                'travelers': trip.travelers,
                'created_at': trip.created_at,
                'is_upcoming': trip.start_date >= timezone.now().date() if trip.start_date else False,
                'is_completed': trip.status == 'completed',
                'has_hotel': bool(trip.selected_hotel),
                'has_transport': bool(trip.selected_transport),
            })
        
        context.update({
            'trips': trip_data,
            'total_trips': trips.count(),
            'upcoming_count': upcoming_trips.count(),
            'completed_count': completed_trips.count(),
            'total_spent_mmk': sum(trip.get_total_cost_in_mmk() for trip in trips.filter(status__in=['booked', 'completed'])),
        })
        
        return context


class UpcomingTripsView(LoginRequiredMixin, TemplateView):
    """View for showing only upcoming trips"""
    template_name = 'planner/upcoming_trips.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get upcoming trips (draft, planning, booked AND start_date in future)
        upcoming_trips = TripPlan.objects.filter(
            user=user,
            status__in=['draft', 'planning', 'booked'],
            start_date__gte=timezone.now().date()
        ).order_by('start_date')
        
        # Prepare trip data
        trip_data = []
        for trip in upcoming_trips:
            trip_data.append({
                'id': trip.id,
                'origin': trip.origin.name if trip.origin else 'Not specified',
                'destination': trip.destination.name if trip.destination else 'Not specified',
                'start_date': trip.start_date,
                'end_date': trip.end_date,
                'total_days': trip.calculate_nights() + 1,
                'status': trip.status,
                'status_display': trip.get_status_display(),
                'total_cost_mmk': trip.get_total_cost_in_mmk(),
                'travelers': trip.travelers,
                'days_until': (trip.start_date - timezone.now().date()).days if trip.start_date else None,
                'hotel': trip.selected_hotel.name if trip.selected_hotel else 'Not selected',
                'transport': trip.selected_transport.get('name', 'Not selected') if trip.selected_transport else 'Not selected',
            })
        
        context.update({
            'upcoming_trips': trip_data,
            'total_upcoming': upcoming_trips.count(),
            'total_cost_mmk': sum(trip.get_total_cost_in_mmk() for trip in upcoming_trips),
        })
        
        return context


class TripCostAnalysisView(LoginRequiredMixin, TemplateView):
    """View for showing detailed cost analysis when clicking 'Total Spent' card"""
    template_name = 'planner/trip_cost_analysis.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get all trips
        trips = TripPlan.objects.filter(user=user).order_by('-created_at')
        
        # Calculate cost breakdown by category and trip
        cost_breakdowns = []
        total_spent = 0
        total_estimated = 0
        
        for trip in trips:
            breakdown = trip.get_cost_breakdown()
            cost_data = {
                'trip': trip,
                'destination': trip.destination.name if trip.destination else 'Unknown',
                'dates': f"{trip.start_date.strftime('%b %d')} - {trip.end_date.strftime('%b %d, %Y')}",
                'total_days': trip.calculate_nights() + 1,
                'status': trip.status,
                'cost_breakdown': breakdown,
                'total_cost': breakdown['total'],
                'hotel_cost': breakdown.get('hotel', 0),
                'transport_cost': breakdown.get('transport', 0),
                'destination_cost': breakdown.get('destination', 0),
                'additional_travelers_cost': breakdown.get('additional_travelers', 0),
            }
            cost_breakdowns.append(cost_data)
            
            if trip.status in ['booked', 'completed']:
                total_spent += breakdown['total']
            total_estimated += breakdown['total']
        
        # Calculate category totals
        hotel_total = sum(item['hotel_cost'] for item in cost_breakdowns)
        transport_total = sum(item['transport_cost'] for item in cost_breakdowns)
        destination_total = sum(item['destination_cost'] for item in cost_breakdowns)
        additional_total = sum(item['additional_travelers_cost'] for item in cost_breakdowns)
        
        context.update({
            'cost_breakdowns': cost_breakdowns,
            'total_spent_mmk': total_spent,
            'total_estimated_mmk': total_estimated,
            'hotel_total_mmk': hotel_total,
            'transport_total_mmk': transport_total,
            'destination_total_mmk': destination_total,
            'additional_total_mmk': additional_total,
            'total_trips': trips.count(),
            'booked_completed_trips': trips.filter(status__in=['booked', 'completed']).count(),
        })
        
        return context


class VisitedDestinationsView(LoginRequiredMixin, TemplateView):
    """View for showing visited destinations when clicking 'Destinations Visited' card"""
    template_name = 'planner/visited_destinations.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get TODAY'S DATE (dynamic, not hardcoded)
        today = timezone.now().date()
        
        # Get trips that have been completed (status='completed') OR have ended (end_date < today)
        visited_trips = TripPlan.objects.filter(
            user=user
        ).filter(
            Q(status='completed') | Q(end_date__lt=today)
        ).exclude(
            status='cancelled'
        ).order_by('-end_date')
        
        print(f"DEBUG: Today's date: {today}")
        print(f"DEBUG: Found {visited_trips.count()} visited trips")
        
        # Group destinations by visit date
        visited_destinations_by_month = {}
        destination_stats = {}
        
        for trip in visited_trips:
            if trip.destination:
                dest_name = trip.destination.name
                dest_region = trip.destination.region
                visit_date = trip.end_date  # Last day of the trip
                
                print(f"DEBUG: {dest_name} - End: {visit_date}, Status: {trip.status}")
                
                # Group by year-month for timeline
                year_month = visit_date.strftime('%Y-%m')
                if year_month not in visited_destinations_by_month:
                    visited_destinations_by_month[year_month] = []
                
                visited_destinations_by_month[year_month].append({
                    'destination': trip.destination,
                    'visit_date': visit_date,
                    'trip': trip,
                    'duration_days': trip.calculate_nights() + 1,
                    'travelers': trip.travelers,
                    'total_cost_mmk': trip.get_total_cost_in_mmk(),
                    'status': trip.status,
                })
                
                # Initialize destination stats if first time
                if dest_name not in destination_stats:
                    destination_stats[dest_name] = {
                        'destination': trip.destination,
                        'destination_region': dest_region,
                        'visit_count': 0,
                        'last_visit': visit_date,  # Will be updated if newer
                        'total_days': 0,
                        'total_spent': 0,
                        'trips': []
                    }
                else:
                    # Update last_visit if this trip is more recent
                    if visit_date > destination_stats[dest_name]['last_visit']:
                        destination_stats[dest_name]['last_visit'] = visit_date
                
                # Update stats
                destination_stats[dest_name]['visit_count'] += 1
                destination_stats[dest_name]['total_days'] += (trip.calculate_nights() + 1)
                destination_stats[dest_name]['total_spent'] += trip.get_total_cost_in_mmk()
                destination_stats[dest_name]['trips'].append({
                    'date': visit_date,
                    'duration': trip.calculate_nights() + 1,
                    'cost': trip.get_total_cost_in_mmk(),
                    'status': trip.status
                })
        
        # Calculate average cost per day for each destination
        for dest_name, stats in destination_stats.items():
            if stats['total_days'] > 0:
                stats['avg_cost_per_day'] = int(stats['total_spent'] / stats['total_days'])
            else:
                stats['avg_cost_per_day'] = 0
        
        # Sort destinations by last visit date (most recent first)
        sorted_destinations = sorted(
            destination_stats.values(),
            key=lambda x: x['last_visit'],
            reverse=True
        )
        
        # Sort visited destinations by month (most recent first)
        sorted_visited_months = sorted(
            visited_destinations_by_month.items(),
            key=lambda x: x[0],
            reverse=True
        )
        
        context.update({
            'visited_destinations': dict(sorted_visited_months),
            'destination_stats': sorted_destinations,
            'total_destinations_visited': len(destination_stats),
            'total_visited_trips': visited_trips.count(),
            'total_days_traveled': sum(trip.calculate_nights() + 1 for trip in visited_trips),
            'total_spent_mmk': sum(trip.get_total_cost_in_mmk() for trip in visited_trips),
            'today': today,
        })
        
        return context