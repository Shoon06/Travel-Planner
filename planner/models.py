# C:\Users\ASUS\MyanmarTravelPlanner\planner\models.py
# CORRECTED VERSION - Fix indentation error

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from .airport_data import get_airport_info, destination_has_airport
User = get_user_model()

# ========== ADD THIS NEW MODEL ==========
class Airline(models.Model):
    """Model for airlines operating in Myanmar"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, help_text="IATA airline code")
    logo = models.ImageField(upload_to='airlines/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_default_for_domestic = models.BooleanField(default=False, 
        help_text="Whether this airline is default for domestic flights")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        ordering = ['name']


class Destination(models.Model):
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=[
        ('city', 'City'),
        ('town', 'Town'),
        ('attraction', 'Attraction'),
        ('state', 'State'),
        ('region', 'Region'),
        ('union_territory', 'Union Territory')
    ])
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='destinations/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ADD THIS FIELD FOR DEFAULT AIRLINES
    default_airlines = models.ManyToManyField(Airline, blank=True, 
        help_text="Default airlines for this destination")
    
    def __str__(self):
        return f"{self.name}, {self.region}"
    
    def has_airport(self):
        """Check if this destination has an airport"""
        airport_info = get_airport_info(self.name)
        return airport_info is not None and airport_info.get('has_airport', False)
    
    def get_airport_info(self):
        """Get airport information for this destination"""
        return get_airport_info(self.name)
    
    def airport_available(self):
        """Alias for has_airport for template compatibility"""
        return self.has_airport()
    
    class Meta:
        ordering = ['name']


class Flight(models.Model):
    # ... update the airline field to use the Airline model
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, related_name='flights')
    flight_number = models.CharField(max_length=20)
    departure = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='departing_flights')
    arrival = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='arriving_flights')
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    duration = models.DurationField()
    price = models.DecimalField(max_digits=10, decimal_places=0, help_text="Price in MMK")
    category = models.CharField(max_length=20, choices=[
        ('low', 'Low Cost'),
        ('medium', 'Medium Cost'),
        ('high', 'High Cost'),
    ])
    total_seats = models.IntegerField(default=180)
    available_seats = models.IntegerField(default=180)
    
    # ADD SEAT MAP FIELD
    seat_map = models.JSONField(default=dict, help_text="JSON representation of seat layout and availability")
    
    description = models.TextField(blank=True)
    flight_image = models.ImageField(upload_to='flights/', blank=True, null=True)
    amenities = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.airline.name} {self.flight_number}: {self.departure.name} → {self.arrival.name}"
    
    def price_in_mmk(self):
        return int(self.price)
    
    def get_duration_display(self):
        total_seconds = int(self.duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    
    # ADD THIS METHOD TO GENERATE DEFAULT SEAT MAP
    def generate_seat_map(self):
        """Generate a default seat map for the flight"""
        seat_map = {
            'total_rows': 30,
            'seats_per_row': 6,
            'configuration': '3-3',  # 3 seats on left, aisle, 3 seats on right
            'first_class_rows': 4,
            'business_class_rows': 0,
            'economy_class_rows': 26,
            'premium_seats': ['1A', '1B', '1C', '1D', '1E', '1F',
                             '2A', '2B', '2C', '2D', '2E', '2F'],
            'occupied_seats': self.get_real_occupied_seats(),  # CHANGED THIS LINE
            'seat_prices': {
                'premium': float(self.price) * 1.5,
                'economy': float(self.price),
                'extra_legroom': float(self.price) * 1.2
            }
        }
        return seat_map
    
    def get_real_occupied_seats(self):
        """Get actually booked seats from database"""
        from .models import BookedSeat  # Import here to avoid circular import
        booked_seats = BookedSeat.objects.filter(
            transport_type='flight',
            transport_id=self.id,
            is_cancelled=False
        ).values_list('seat_number', flat=True)
        return list(booked_seats)
    
    # REMOVE OR COMMENT OUT THE get_random_occupied_seats METHOD
    # def get_random_occupied_seats(self):
    #     """Generate random occupied seats for demo"""
    #     import random
    #     total_seats = 180
    #     occupied_count = random.randint(20, 80)  # 20-80 seats occupied
    #     occupied_seats = set()
    #     
    #     seats = []
    #     for row in range(1, 31):
    #         for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
    #             seats.append(f"{row}{letter}")
    #     
    #     occupied_seats = random.sample(seats, occupied_count)
    #     return occupied_seats


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='hotels')
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    price_per_night = models.DecimalField(
        max_digits=10, 
        decimal_places=0,
        validators=[MinValueValidator(0)],
        help_text="Price in MMK (Myanmar Kyat)"
    )
    category = models.CharField(max_length=20, choices=[
        ('budget', 'Budget (Under 50,000 MMK)'),
        ('medium', 'Medium (50,000 - 150,000 MMK)'),
        ('luxury', 'Luxury (150,000+ MMK)'),
    ])
    amenities = models.JSONField(default=list)
    rating = models.DecimalField(
        max_digits=2, 
        decimal_places=1, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review_count = models.IntegerField(default=0)
    image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    description = models.TextField(blank=True)
    gallery_images = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by_admin = models.BooleanField(default=False, help_text="Whether this hotel was created by admin")
    is_real_hotel = models.BooleanField(default=False, help_text="Is this a real hotel from Google Maps?")
    google_place_id = models.CharField(max_length=255, blank=True, null=True)
    
    # ADD THESE NEW FIELDS:
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    check_in_time = models.TimeField(default='14:00')
    check_out_time = models.TimeField(default='12:00')
    
    def __str__(self):
        return f"{self.name} - {self.destination.name}"
    
    def price_in_mmk(self):
        """Return price formatted in MMK"""
        return f"{int(self.price_per_night):,}"
    
    def get_amenities_display(self):
        return ', '.join([amenity.title() for amenity in self.amenities])
    
    def has_coordinates(self):
        return self.latitude is not None and self.longitude is not None
    
    def get_map_marker_data(self):
        """Return data for map markers"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'latitude': float(self.latitude) if self.latitude else 0,
            'longitude': float(self.longitude) if self.longitude else 0,
            'price': float(self.price_per_night),
            'price_display': self.price_in_mmk(),
            'rating': float(self.rating),
            'review_count': self.review_count,
            'category': self.category,
            'category_display': self.get_category_display(),
            'amenities': self.amenities[:5],  # First 5 amenities
            'is_real': self.is_real_hotel,
            'is_our_hotel': self.created_by_admin,
            'image_url': self.image.url if self.image else '',
            'has_image': bool(self.image),
            'gallery_images': self.gallery_images,
            'description': self.description[:100] + '...' if len(self.description) > 100 else self.description
        }
    
    def get_booking_data(self):
        """Return data for booking"""
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price_per_night),
            'category': self.category,
            'address': self.address,
            'rating': float(self.rating),
            'is_real_hotel': self.is_real_hotel
        }


class BusService(models.Model):
    # ... keep your existing BusService model code ...
    company = models.CharField(max_length=100)
    departure = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='departing_buses')
    arrival = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='arriving_buses')
    departure_time = models.TimeField()
    duration = models.DurationField()
    price = models.DecimalField(max_digits=10, decimal_places=0, help_text="Price in MMK")
    bus_type = models.CharField(max_length=50, choices=[
        ('standard', 'Standard'),
        ('vip', 'VIP'),
        ('luxury', 'Luxury'),
    ])
    total_seats = models.IntegerField(default=40)
    available_seats = models.IntegerField(default=40)
    bus_number = models.CharField(max_length=20, blank=True)
    bus_image = models.ImageField(upload_to='buses/', blank=True, null=True)
    amenities = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.company}: {self.departure.name} → {self.arrival.name}"
    
    def price_in_mmk(self):
        return int(self.price)
    
    def get_duration_display(self):
        total_seconds = int(self.duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"


class CarRental(models.Model):
    # ... keep your existing CarRental model code ...
    company = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    car_type = models.CharField(max_length=50, choices=[
        ('economy', 'Economy'),
        ('suv', 'SUV'),
        ('luxury', 'Luxury'),
        ('van', 'Van'),
    ])
    seats = models.IntegerField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=0, help_text="Price in MMK per day")
    features = models.JSONField(default=list)
    is_available = models.BooleanField(default=True)
    location = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='available_cars')
    car_image = models.ImageField(upload_to='cars/', blank=True, null=True)
    interior_images = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    year = models.IntegerField(blank=True, null=True)
    fuel_type = models.CharField(max_length=20, blank=True)
    transmission = models.CharField(max_length=20, choices=[
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
    ], default='automatic')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.company} - {self.car_model}"
    
    def price_in_mmk(self):
        return int(self.price_per_day)
    
    def get_features_display(self):
        return ', '.join([feature.title() for feature in self.features])


class TripPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    origin = models.ForeignKey(
        Destination, 
        on_delete=models.CASCADE, 
        related_name='departing_trips', 
        verbose_name='From',
        default=1
    )
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='arriving_trips', verbose_name='To')
    start_date = models.DateField()
    end_date = models.DateField()
    travelers = models.IntegerField(default=1)
    budget_range = models.CharField(max_length=20, choices=[
        ('low', 'Budget'),
        ('medium', 'Medium'),
        ('high', 'Luxury'),
    ])
    accommodation_type = models.CharField(max_length=20, blank=True)
    selected_hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, blank=True)
    transportation_preference = models.CharField(max_length=20, blank=True)
    selected_transport = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, default='draft', choices=[
        ('draft', 'Draft'),
        ('planning', 'Planning'),
        ('booked', 'Booked'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s trip from {self.origin.name} to {self.destination.name}"
    
    def calculate_nights(self):
        days = (self.end_date - self.start_date).days
        return max(1, days)
    
    def get_total_cost(self):
        total = 0
        nights = self.calculate_nights()
        
        if self.selected_hotel:
            total += float(self.selected_hotel.price_per_night) * nights
        
        if self.selected_transport and 'price' in self.selected_transport:
            total += float(self.selected_transport['price'])
        
        return int(total)
    
    def origin_has_airport(self):
        """Check if origin has airport"""
        return self.origin.has_airport() if self.origin else False
    
    def destination_has_airport(self):
        """Check if destination has airport"""
        return self.destination.has_airport() if self.destination else False
    
    class Meta:
        ordering = ['-created_at']


class BookedSeat(models.Model):
    """Model to track booked seats for flights and buses"""
    transport_type = models.CharField(max_length=10, choices=[
        ('flight', 'Flight'),
        ('bus', 'Bus'),
    ])
    transport_id = models.IntegerField()  # ID of Flight or BusService
    seat_number = models.CharField(max_length=10)  # e.g., "1A", "2B"
    trip = models.ForeignKey(TripPlan, on_delete=models.CASCADE, related_name='booked_seats')
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booked_seats')
    booking_time = models.DateTimeField(auto_now_add=True)
    is_cancelled = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['transport_type', 'transport_id', 'seat_number']
        ordering = ['transport_type', 'transport_id', 'seat_number']
    
    def __str__(self):
        return f"{self.seat_number} on {self.transport_type} {self.transport_id}"