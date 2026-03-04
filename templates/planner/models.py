from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Destination(models.Model):
    name = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=[
        ('city', 'City'),
        ('town', 'Town'),
        ('attraction', 'Attraction')
    ])
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='destinations/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name}, {self.region}"
    
    class Meta:
        ordering = ['name']

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='hotels')
    address = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=[
        ('budget', 'Budget ($-$$)'),
        ('medium', 'Medium ($$-$$$)'),
        ('luxury', 'Luxury ($$$+)'),
    ])
    amenities = models.JSONField(default=list)  # ['wifi', 'pool', 'spa', etc.]
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    review_count = models.IntegerField(default=0)
    image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.destination.name}"
    
    def price_in_mmk(self):
        return int(self.price_per_night * 2100)  # Approximate conversion rate

class Flight(models.Model):
    airline = models.CharField(max_length=100)
    flight_number = models.CharField(max_length=20)
    departure = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='departing_flights')
    arrival = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='arriving_flights')
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    duration = models.DurationField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=[
        ('low', 'Low Cost'),
        ('medium', 'Medium Cost'),
        ('high', 'High Cost'),
    ])
    total_seats = models.IntegerField(default=180)
    available_seats = models.IntegerField(default=180)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.airline} {self.flight_number}: {self.departure.name} → {self.arrival.name}"
    
    def price_in_mmk(self):
        return int(self.price * 2100)

class BusService(models.Model):
    company = models.CharField(max_length=100)
    departure = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='departing_buses')
    arrival = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='arriving_buses')
    departure_time = models.TimeField()
    duration = models.DurationField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bus_type = models.CharField(max_length=50, choices=[
        ('standard', 'Standard'),
        ('vip', 'VIP'),
        ('luxury', 'Luxury'),
    ])
    total_seats = models.IntegerField(default=40)
    available_seats = models.IntegerField(default=40)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.company}: {self.departure.name} → {self.arrival.name}"
    
    def price_in_mmk(self):
        return int(self.price * 2100)

class CarRental(models.Model):
    company = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    car_type = models.CharField(max_length=50, choices=[
        ('economy', 'Economy'),
        ('suv', 'SUV'),
        ('luxury', 'Luxury'),
        ('van', 'Van'),
    ])
    seats = models.IntegerField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    is_available = models.BooleanField(default=True)
    location = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='available_cars')
    image = models.ImageField(upload_to='cars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.company} - {self.car_model}"
    
    def price_in_mmk(self):
        return int(self.price_per_day * 2100)

class TripPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
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
    selected_transport = models.JSONField(default=dict, blank=True)  # Store selected transport details
    status = models.CharField(max_length=20, default='draft', choices=[
        ('draft', 'Draft'),
        ('planning', 'Planning'),
        ('booked', 'Booked'),
        ('completed', 'Completed'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s trip to {self.destination.name}"
    
    class Meta:
        ordering = ['-created_at']