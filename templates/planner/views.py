from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import json
from .models import Destination, Hotel, Flight, BusService, CarRental, TripPlan

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'planner/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trips'] = TripPlan.objects.filter(user=self.request.user).order_by('-created_at')
        return context





class PlanTripView(LoginRequiredMixin, View):
    template_name = 'planner/plan.html'
    
    def get(self, request):
        # Get dates
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Check URL parameters for clearing selections
        clear_hotel = request.GET.get('clear_hotel') == 'true'
        clear_transport = request.GET.get('clear_transport') == 'true'
        
        # Get any existing planning trip
        existing_trip = TripPlan.objects.filter(
            user=request.user,
            status__in=['draft', 'planning']
        ).first()
        
        context = {
            'today': today,
            'tomorrow': tomorrow,
            'existing_trip': existing_trip,
        }
        
        # If we have an existing trip, populate the form with its data
        if existing_trip:
            context['destination_input'] = existing_trip.destination.name if existing_trip.destination else ''
            context['selected_destination_id'] = existing_trip.destination.id if existing_trip.destination else ''
            context['selected_hotel_id'] = existing_trip.selected_hotel.id if existing_trip.selected_hotel else ''
            context['selected_transport_id'] = existing_trip.selected_transport.get('id', '') if existing_trip.selected_transport else ''
            context['selected_transport_type'] = existing_trip.selected_transport.get('type', '') if existing_trip.selected_transport else ''
            
            if existing_trip.selected_hotel:
                context['selected_hotel_name'] = existing_trip.selected_hotel.name
            
            if existing_trip.selected_transport:
                context['selected_transport_name'] = existing_trip.selected_transport.get('name', '')
        
        # Handle clearing selections
        if clear_hotel and existing_trip:
            existing_trip.selected_hotel = None
            existing_trip.accommodation_type = ''
            existing_trip.save()
            return redirect('planner:plan')
        
        if clear_transport and existing_trip:
            existing_trip.selected_transport = {}
            existing_trip.transportation_preference = ''
            existing_trip.save()
            return redirect('planner:plan')
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.handle_ajax(request)
        return self.handle_regular(request)
    
    def handle_ajax(self, request):
        """Handle AJAX request for saving basic trip info"""
        try:
            destination_id = request.POST.get('destination_id')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            travelers = request.POST.get('travelers', 1)
            selected_hotel_id = request.POST.get('selected_hotel_id')
            
            if not all([destination_id, start_date, end_date]):
                return JsonResponse({'success': False, 'error': 'Missing required fields'})
            
            # Validate dates
            if end_date <= start_date:
                return JsonResponse({'success': False, 'error': 'End date must be after start date'})
            
            # Get or create trip
            existing_trip = TripPlan.objects.filter(
                user=request.user,
                status__in=['draft', 'planning']
            ).first()
            
            if existing_trip:
                trip = existing_trip
                trip.destination_id = destination_id
                trip.start_date = start_date
                trip.end_date = end_date
                trip.travelers = travelers
                trip.status = 'planning'
            else:
                trip = TripPlan.objects.create(
                    user=request.user,
                    destination_id=destination_id,
                    start_date=start_date,
                    end_date=end_date,
                    travelers=travelers,
                    budget_range='medium',  # Default
                    status='planning'
                )
            
            # Update hotel if provided
            if selected_hotel_id:
                try:
                    hotel = Hotel.objects.get(id=selected_hotel_id)
                    trip.selected_hotel = hotel
                    trip.accommodation_type = hotel.category
                except Hotel.DoesNotExist:
                    pass
            
            trip.save()
            
            return JsonResponse({
                'success': True,
                'trip_id': trip.id,
                'message': 'Trip saved successfully'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    def handle_regular(self, request):
        """Handle regular form submission (final submission)"""
        destination_id = request.POST.get('destination_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        travelers = request.POST.get('travelers', 1)
        selected_hotel_id = request.POST.get('selected_hotel_id')
        selected_transport_type = request.POST.get('selected_transport_type')
        selected_transport_id = request.POST.get('selected_transport_id')
        
        # Validate dates
        if end_date <= start_date:
            messages.error(request, 'End date must be after start date.')
            return redirect('planner:plan')
        
        # Get or create trip
        trip = TripPlan.objects.filter(
            user=request.user,
            status__in=['draft', 'planning']
        ).first()
        
        if not trip:
            trip = TripPlan.objects.create(
                user=request.user,
                destination_id=destination_id,
                start_date=start_date,
                end_date=end_date,
                travelers=travelers,
                budget_range='medium',
                status='planning'
            )
        else:
            trip.destination_id = destination_id
            trip.start_date = start_date
            trip.end_date = end_date
            trip.travelers = travelers
        
        # Save selected hotel if provided
        if selected_hotel_id:
            try:
                hotel = Hotel.objects.get(id=selected_hotel_id)
                trip.selected_hotel = hotel
                trip.accommodation_type = hotel.category
            except Hotel.DoesNotExist:
                messages.error(request, 'Selected hotel not found.')
        
        # Save selected transport if provided
        if selected_transport_id and selected_transport_type:
            trip.transportation_preference = selected_transport_type
            try:
                if selected_transport_type == 'flight':
                    transport = Flight.objects.get(id=selected_transport_id)
                    transport_name = transport.airline
                elif selected_transport_type == 'bus':
                    transport = BusService.objects.get(id=selected_transport_id)
                    transport_name = transport.company
                elif selected_transport_type == 'car':
                    transport = CarRental.objects.get(id=selected_transport_id)
                    transport_name = f"{transport.company} - {transport.car_model}"
                else:
                    transport_name = "Unknown"
                
                trip.selected_transport = {
                    'type': selected_transport_type,
                    'id': selected_transport_id,
                    'name': transport_name,
                }
            except Exception as e:
                print(f"Error saving transport: {e}")
                messages.error(request, 'Error saving transport selection.')
        
        trip.save()
        
        # Check if all required selections are made
        if not trip.selected_hotel:
            messages.error(request, 'Please select a hotel first.')
            return redirect('planner:select_hotel', trip_id=trip.id)
        
        if not trip.selected_transport:
            messages.error(request, 'Please select transportation first.')
            return redirect('planner:select_transport_category', trip_id=trip.id)
        
        # If everything is selected, mark trip as completed
        trip.status = 'booked'
        trip.save()
        
        messages.success(request, 'Trip plan completed successfully!')
        return redirect('planner:dashboard')

class SelectHotelView(LoginRequiredMixin, View):
    template_name = 'planner/select_hotel.html'
    
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
        
        context = {
            'trip': trip,
            'hotels': hotels,
            'nights': nights,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        hotel_id = request.POST.get('hotel_id')
        
        if hotel_id:
            hotel = get_object_or_404(Hotel, id=hotel_id)
            trip.selected_hotel = hotel
            trip.accommodation_type = hotel.category
            trip.save()
            
            # Redirect back to plan page with hotel selected
            return redirect(f'{reverse("planner:plan")}?hotel_id={hotel_id}')
        
        messages.error(request, 'Please select a hotel')
        return redirect('planner:select_hotel', trip_id=trip.id)

class SelectTransportCategoryView(LoginRequiredMixin, View):
    template_name = 'planner/select_transport_category.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        context = {'trip': trip}
        return render(request, self.template_name, context)

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
            # For car rental, no seat selection needed
            transport = get_object_or_404(CarRental, id=transport_id)
            # Save directly and redirect back
            trip.transportation_preference = 'car'
            trip.selected_transport = {
                'type': 'car',
                'id': transport_id,
                'name': f"{transport.company} - {transport.car_model}",
            }
            trip.save()
            return redirect(f'{reverse("planner:plan")}?transport_id={transport_id}&transport_type=car')
        
        context = {
            'trip': trip,
            'transport': transport,
            'transport_type': transport_type,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, trip_id, transport_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.POST.get('transport_type', 'flight')
        selected_seats = request.POST.get('selected_seats', '[]')
        
        # Save transport selection
        try:
            if transport_type == 'flight':
                transport = Flight.objects.get(id=transport_id)
                transport_name = transport.airline
            elif transport_type == 'bus':
                transport = BusService.objects.get(id=transport_id)
                transport_name = transport.company
            else:
                return redirect('planner:plan')
            
            trip.transportation_preference = transport_type
            trip.selected_transport = {
                'type': transport_type,
                'id': transport_id,
                'name': transport_name,
                'seats': json.loads(selected_seats),
            }
            trip.save()
            
            # Redirect back to plan page with transport selected
            return redirect(f'{reverse("planner:plan")}?transport_id={transport_id}&transport_type={transport_type}')
            
        except Exception as e:
            messages.error(request, f'Error saving selection: {str(e)}')
            return redirect('planner:select_seats', trip_id=trip_id, transport_id=transport_id)

class GetTransportOptionsView(View):
    def get(self, request):
        trip_id = request.GET.get('trip_id')
        transport_type = request.GET.get('type')
        
        try:
            trip = TripPlan.objects.get(id=trip_id)
            
            if transport_type == 'flight':
                options = Flight.objects.filter(
                    Q(departure__name='Yangon') | Q(departure=trip.destination),
                    arrival=trip.destination,
                    is_active=True
                ).order_by('price')[:15]
                
                data = [{
                    'id': f.id,
                    'name': f.airline,
                    'category': f.category,
                    'price': f.price_in_mmk(),
                    'departure_time': f.departure_time.strftime('%I:%M %p'),
                    'duration': str(f.duration),
                    'route': f"{f.departure.name} → {f.arrival.name}",
                    'flight_number': f.flight_number,
                } for f in options]
                
            elif transport_type == 'bus':
                options = BusService.objects.filter(
                    Q(departure__name='Yangon') | Q(departure=trip.destination),
                    arrival=trip.destination,
                    is_active=True
                ).order_by('price')[:15]
                
                data = [{
                    'id': b.id,
                    'name': b.company,
                    'category': 'low' if b.price < 50 else 'medium' if b.price < 100 else 'high',
                    'price': b.price_in_mmk(),
                    'departure_time': b.departure_time.strftime('%I:%M %p'),
                    'duration': str(b.duration),
                    'bus_type': b.get_bus_type_display(),
                    'route': f"{b.departure.name} → {b.arrival.name}",
                } for b in options]
                
            elif transport_type == 'car':
                options = CarRental.objects.filter(
                    location=trip.destination,
                    is_available=True
                ).order_by('price_per_day')[:15]
                
                data = [{
                    'id': c.id,
                    'name': c.company,
                    'category': 'low' if c.price_per_day < 50 else 'medium' if c.price_per_day < 100 else 'high',
                    'price': c.price_in_mmk(),
                    'car_model': c.car_model,
                    'seats': c.seats,
                    'car_type': c.get_car_type_display(),
                } for c in options]
                
            else:
                data = []
            
            return JsonResponse({'success': True, 'options': data})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

class SaveTransportView(LoginRequiredMixin, View):
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_id = request.POST.get('transport_id')
        transport_type = request.POST.get('transport_type')
        
        try:
            trip.transportation_preference = transport_type
            
            if transport_type == 'flight':
                transport = Flight.objects.get(id=transport_id)
                transport_name = transport.airline
            elif transport_type == 'bus':
                transport = BusService.objects.get(id=transport_id)
                transport_name = transport.company
            elif transport_type == 'car':
                transport = CarRental.objects.get(id=transport_id)
                transport_name = f"{transport.company} - {transport.car_model}"
            else:
                return JsonResponse({'success': False, 'error': 'Invalid transport type'})
            
            trip.selected_transport = {
                'type': transport_type,
                'id': transport_id,
                'name': transport_name,
            }
            
            trip.save()
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

class SearchDestinationsView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip().lower()
        
        if not query or len(query) < 1:
            return JsonResponse({'results': []})
        
        try:
            # Search destinations by name or region
            destinations = Destination.objects.filter(
                Q(name__icontains=query) | Q(region__icontains=query)
            ).order_by('name')[:10]
            
            results = []
            for dest in destinations:
                results.append({
                    'id': dest.id,
                    'name': dest.name,
                    'region': dest.region,
                    'type': dest.get_type_display() if dest.type else 'Destination'
                })
            
            return JsonResponse({'results': results})
            
        except Exception as e:
            print(f"Error searching destinations: {e}")
            # Return empty results with error message
            return JsonResponse({'results': [], 'error': str(e)})

# Helper function to calculate nights
def calculate_nights(start_date, end_date):
    if start_date and end_date:
        return (end_date - start_date).days
    return 1
class SearchDestinationsView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip().lower()
        
        if not query:
            return JsonResponse({'results': []})
        
        try:
            # Search destinations by name or region
            destinations = Destination.objects.filter(
                Q(name__icontains=query) | Q(region__icontains=query)
            ).order_by('name')[:10]
            
            results = []
            for dest in destinations:
                results.append({
                    'id': dest.id,
                    'name': dest.name,
                    'region': dest.region,
                    'type': dest.get_type_display() if dest.type else 'Destination'
                })
            
            # If no results found, try fuzzy matching
            if not results and len(query) >= 2:
                destinations = Destination.objects.filter(
                    Q(name__icontains=query[:2]) | Q(region__icontains=query[:2])
                ).order_by('name')[:5]
                
                for dest in destinations:
                    results.append({
                        'id': dest.id,
                        'name': dest.name,
                        'region': dest.region,
                        'type': dest.get_type_display() if dest.type else 'Destination'
                    })
            
            return JsonResponse({'results': results})
            
        except Exception as e:
            print(f"Error searching destinations: {e}")
            return JsonResponse({'results': [], 'error': str(e)})
class SelectHotelView(LoginRequiredMixin, View):
    template_name = 'planner/hotels.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        
        # Get filter parameters
        budget_filter = request.GET.get('budget', 'all')
        category_filter = request.GET.get('category', None)
        
        # Get hotels for the destination
        hotels = Hotel.objects.filter(
            destination=trip.destination,
            is_active=True
        )
        
        # Apply budget filter
        if budget_filter == 'low':
            hotels = hotels.filter(price_per_night__lt=50)
        elif budget_filter == 'medium':
            hotels = hotels.filter(price_per_night__gte=50, price_per_night__lt=150)
        elif budget_filter == 'high':
            hotels = hotels.filter(price_per_night__gte=150)
        
        # Apply category filter
        if category_filter:
            hotels = hotels.filter(category=category_filter)
        
        context = {
            'trip': trip,
            'hotels': hotels.order_by('price_per_night'),
            'destination': trip.destination,
            'start_date': trip.start_date,
            'end_date': trip.end_date,
            'travelers': trip.travelers,
            'budget_filter': budget_filter,
            'category': category_filter,
        }
        return render(request, self.template_name, context)

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
                
                # Redirect back to plan page with hotel selected
                return redirect(f'{reverse("planner:plan")}?hotel_id={hotel_id}&hotel_name={hotel.name}')
                
            except Hotel.DoesNotExist:
                messages.error(request, 'Hotel not found.')
        
        return redirect('planner:select_hotel', trip_id=trip.id)

class SelectTransportCategoryView(LoginRequiredMixin, View):
    template_name = 'planner/transport_category.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        context = {'trip': trip}
        return render(request, self.template_name, context)

class SelectTransportView(LoginRequiredMixin, View):
    template_name = 'planner/transport_list.html'
    
    def get(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.GET.get('type', 'flight')
        budget_filter = request.GET.get('budget', 'all')
        
        transport_items = []
        
        if transport_type == 'flight':
            items = Flight.objects.filter(
                departure__name='Yangon',  # Default departure
                arrival=trip.destination,
                is_active=True
            )
            
            # Apply budget filter
            if budget_filter == 'low':
                items = items.filter(price__lt=50)
            elif budget_filter == 'medium':
                items = items.filter(price__gte=50, price__lt=120)
            elif budget_filter == 'high':
                items = items.filter(price__gte=120)
                
            transport_items = items.order_by('price')
            
        elif transport_type == 'bus':
            items = BusService.objects.filter(
                departure__name='Yangon',  # Default departure
                arrival=trip.destination,
                is_active=True
            )
            
            # Apply budget filter
            if budget_filter == 'low':
                items = items.filter(price__lt=30)
            elif budget_filter == 'medium':
                items = items.filter(price__gte=30, price__lt=60)
            elif budget_filter == 'high':
                items = items.filter(price__gte=60)
                
            transport_items = items.order_by('price')
            
        elif transport_type == 'car':
            items = CarRental.objects.filter(
                location=trip.destination,
                is_available=True
            )
            
            # Apply budget filter
            if budget_filter == 'low':
                items = items.filter(price_per_day__lt=50)
            elif budget_filter == 'medium':
                items = items.filter(price_per_day__gte=50, price_per_day__lt=100)
            elif budget_filter == 'high':
                items = items.filter(price_per_day__gte=100)
                
            transport_items = items.order_by('price_per_day')
        
        context = {
            'trip': trip,
            'transport_type': transport_type,
            'transport_items': transport_items,
            'budget_filter': budget_filter,
        }
        return render(request, self.template_name, context)

class SaveTransportView(LoginRequiredMixin, View):
    def post(self, request, trip_id):
        trip = get_object_or_404(TripPlan, id=trip_id, user=request.user)
        transport_type = request.POST.get('transport_type')
        transport_id = request.POST.get('transport_id')
        
        try:
            if transport_type == 'flight':
                transport = Flight.objects.get(id=transport_id)
                transport_name = f"{transport.airline} Flight {transport.flight_number}"
            elif transport_type == 'bus':
                transport = BusService.objects.get(id=transport_id)
                transport_name = f"{transport.company} Bus"
            elif transport_type == 'car':
                transport = CarRental.objects.get(id=transport_id)
                transport_name = f"{transport.company} - {transport.car_model}"
            else:
                messages.error(request, 'Invalid transport type.')
                return redirect('planner:select_transport_category', trip_id=trip.id)
            
            trip.transportation_preference = transport_type
            trip.selected_transport = {
                'type': transport_type,
                'id': transport_id,
                'name': transport_name,
                'price': transport.price_in_mmk() if hasattr(transport, 'price_in_mmk') else transport.price_per_day * 2100
            }
            trip.save()
            
            # Redirect back to plan page
            return redirect(f'{reverse("planner:plan")}?transport_id={transport_id}&transport_type={transport_type}&transport_name={transport_name}')
            
        except Exception as e:
            messages.error(request, f'Error saving transport: {str(e)}')
            return redirect('planner:select_transport_category', trip_id=trip.id)