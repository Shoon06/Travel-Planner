from django.contrib import admin
from .models import Destination, Hotel, Flight, BusService, CarRental, TripPlan

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'type', 'created_at']
    search_fields = ['name', 'region']
    list_filter = ['type', 'region']
    ordering = ['name']

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'destination', 'category', 'price_per_night', 'rating', 'is_active']
    list_filter = ['category', 'is_active', 'destination']
    search_fields = ['name', 'destination__name']
    ordering = ['name']

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['airline', 'flight_number', 'departure', 'arrival', 'departure_time', 'price', 'category']
    list_filter = ['category', 'airline', 'is_active']
    search_fields = ['airline', 'flight_number', 'departure__name', 'arrival__name']

@admin.register(BusService)
class BusServiceAdmin(admin.ModelAdmin):
    list_display = ['company', 'departure', 'arrival', 'departure_time', 'bus_type', 'price']
    list_filter = ['bus_type', 'company', 'is_active']
    search_fields = ['company', 'departure__name', 'arrival__name']

@admin.register(CarRental)
class CarRentalAdmin(admin.ModelAdmin):
    list_display = ['company', 'car_model', 'car_type', 'seats', 'price_per_day', 'location', 'is_available']
    list_filter = ['car_type', 'company', 'is_available']
    search_fields = ['company', 'car_model', 'location__name']

@admin.register(TripPlan)
class TripPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'destination', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'budget_range']
    search_fields = ['user__username', 'destination__name']
    readonly_fields = ['created_at', 'updated_at']