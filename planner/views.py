
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
from .models import Destination, Hotel, Flight, BusService, CarRental, TripPlan
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
                items = items.filter(price__lt=50)
            elif budget_filter == 'medium':
                items = items.filter(price__gte=50, price__lt=120)
            elif budget_filter == 'high':
                items = items.filter(price__gte=120)
                
            transport_items = items.order_by('price')
            
        elif transport_type == 'bus':
            items = BusService.objects.filter(
                departure=trip.origin,
                arrival=trip.destination,
                is_active=True
            )
            
            if budget_filter == 'low':
                items = items.filter(price__lt=30)
            elif budget_filter == 'medium':
                items = items.filter(price__gte=30, price__lt=60)
            elif budget_filter == 'high':
                items = items.filter(price__gte=60)
                
            transport_items = items.order_by('price')
            
        elif transport_type == 'car':
            items = CarRental.objects.filter(
                location=trip.origin,
                is_available=True
            )
            
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

class PlanTripView(LoginRequiredMixin, View):
    template_name = 'planner/plan.html'
    
    def get(self, request):
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
        
        if existing_trip:
            context['origin_input'] = existing_trip.origin.name if existing_trip.origin else ''
            context['selected_origin_id'] = existing_trip.origin.id if existing_trip.origin else ''
            context['destination_input'] = existing_trip.destination.name if existing_trip.destination else ''
            context['selected_destination_id'] = existing_trip.destination.id if existing_trip.destination else ''
            context['selected_hotel_id'] = existing_trip.selected_hotel.id if existing_trip.selected_hotel else ''
            context['selected_transport_id'] = existing_trip.selected_transport.get('id', '') if existing_trip.selected_transport else ''
            context['selected_transport_type'] = existing_trip.selected_transport.get('type', '') if existing_trip.selected_transport else ''
            
            if existing_trip.selected_hotel:
                context['selected_hotel_name'] = existing_trip.selected_hotel.name
            
            if existing_trip.selected_transport:
                context['selected_transport_name'] = existing_trip.selected_transport.get('name', '')
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.handle_ajax(request)
        return self.handle_regular(request)
    
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
            
            if end_date <= start_date:
                return JsonResponse({'success': False, 'error': 'End date must be after start date'})
            
            existing_trip = TripPlan.objects.filter(
                user=request.user,
                status__in=['draft', 'planning']
            ).first()
            
            if existing_trip:
                trip = existing_trip
                trip.origin_id = origin_id
                trip.destination_id = destination_id
                trip.start_date = start_date
                trip.end_date = end_date
                trip.travelers = travelers
                trip.status = 'planning'
            else:
                trip = TripPlan.objects.create(
                    user=request.user,
                    origin_id=origin_id,
                    destination_id=destination_id,
                    start_date=start_date,
                    end_date=end_date,
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
            return JsonResponse({'success': False, 'error': str(e)})

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'planner/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get real data
        trips = TripPlan.objects.filter(user=user).order_by('-created_at')
        
        # Calculate real statistics
        total_trips = trips.count()
        upcoming_trips = trips.filter(
            status__in=['draft', 'planning', 'booked'],
            start_date__gte=timezone.now().date()
        ).count()
        
        # Calculate total spent
        total_spent = 0
        for trip in trips.filter(status__in=['booked', 'completed']):
            total_spent += trip.get_total_cost()
        
        # Get unique destinations visited
        destinations_visited = trips.values('destination__name').distinct().count()
        
        context.update({
            'trips': trips,
            'total_trips': total_trips,
            'upcoming_trips': upcoming_trips,
            'total_spent': total_spent,
            'destinations_visited': destinations_visited,
        })
        
        return context





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
    template_name = 'planner/transport_category.html'
    
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
            elif transport_type == 'bus':
                transport = BusService.objects.get(id=transport_id)
                transport_name = f"{transport.company} Bus"
            elif transport_type == 'car':
                transport = CarRental.objects.get(id=transport_id)
                transport_name = f"{transport.company} - {transport.car_model}"
            else:
                messages.error(request, 'Invalid transport type.')
                return redirect('planner:select_transport_category', trip_id=trip.id)
            
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




            
         
class SearchDestinationsView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip().lower()
        
        if not query:
            return JsonResponse({'results': []})
        
        try:
            # If query is single letter, get all destinations starting with that letter
            if len(query) == 1:
                destinations = Destination.objects.filter(
                    Q(name__istartswith=query) | Q(region__istartswith=query)
                ).order_by('name')[:20]
            else:
                # For longer queries, search more broadly
                destinations = Destination.objects.filter(
                    Q(name__icontains=query) | 
                    Q(region__icontains=query) |
                    Q(name__istartswith=query[:2]) |  # Match first 2 letters
                    Q(region__istartswith=query[:2])
                ).order_by('name')[:15]
            
            results = []
            for dest in destinations:
                results.append({
                    'id': dest.id,
                    'name': dest.name,
                    'region': dest.region,
                    'type': dest.get_type_display()
                })
            
            # If no results, suggest popular destinations
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
                        'type': dest.get_type_display()
                    })
            
            return JsonResponse({'results': results})
            
        except Exception as e:
            print(f"Error searching destinations: {e}")
            return JsonResponse({'results': [], 'error': str(e)})

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


# Helper function to calculate nights
def calculate_nights(start_date, end_date):
    if start_date and end_date:
        return (end_date - start_date).days
    return 1