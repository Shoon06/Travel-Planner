# CORRECTED VERSION - WITH PROPER MODEL ORDERING

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from .airport_data import get_airport_info, destination_has_airport
User = get_user_model()

# ========== AIRLINE MODEL ==========
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


# ========== DESTINATION MODEL ==========
# ========== DESTINATION MODEL ==========
# ========== DESTINATION MODEL ==========
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
    image = models.ImageField(upload_to='destinations/', blank=True, null=True, help_text="Main profile photo for city/town")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = models.TextField(blank=True, null=True)
    attractions = models.TextField(blank=True, null=True)  # JSON or comma-separated
    activities = models.TextField(blank=True, null=True)
    cultural_info = models.TextField(blank=True, null=True)
    best_time_to_visit = models.CharField(max_length=200, blank=True, null=True)
    local_cuisine = models.TextField(blank=True, null=True)
    tips = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='children',
        help_text="Parent region/city that contains this place"
    )
    
    # Add is_region flag to distinguish between regions and attractions
    is_region = models.BooleanField(
        default=False,
        help_text="Is this a region/city (True) or a specific place/attraction (False)?")
    
    # Image fields - Main image (profile photo for cities/towns)
    main_image = models.ImageField(upload_to='destinations/', blank=True, null=True, help_text="Alternative main image field")
    
    # Gallery images for attractions (8 photos)
    gallery_image1 = models.ImageField(upload_to='destinations/gallery/', blank=True, null=True, help_text="Gallery photo 1 for attractions")
    gallery_image2 = models.ImageField(upload_to='destinations/gallery/', blank=True, null=True, help_text="Gallery photo 2 for attractions")
    gallery_image3 = models.ImageField(upload_to='destinations/gallery/', blank=True, null=True, help_text="Gallery photo 3 for attractions")
    gallery_image4 = models.ImageField(upload_to='destinations/gallery/', blank=True, null=True, help_text="Gallery photo 4 for attractions")
    gallery_image5 = models.ImageField(upload_to='destinations/gallery/', blank=True, null=True, help_text="Gallery photo 5 for attractions")
    gallery_image6 = models.ImageField(upload_to='destinations/gallery/', blank=True, null=True, help_text="Gallery photo 6 for attractions")
    gallery_image7 = models.ImageField(upload_to='destinations/gallery/', blank=True, null=True, help_text="Gallery photo 7 for attractions")
    gallery_image8 = models.ImageField(upload_to='destinations/gallery/', blank=True, null=True, help_text="Gallery photo 8 for attractions")
    
    # JSON field to store captions for gallery images
    gallery_captions = models.JSONField(default=dict, blank=True, help_text="JSON object storing captions for gallery images")
    
    default_airlines = models.ManyToManyField('Airline', blank=True, 
        help_text="Default airlines for this destination")
    
    def __str__(self):
        return f"{self.name}, {self.region}"
    
    def get_places_in_region(self):
        """Get all places/attractions in this region"""
        if self.is_region:
            return Destination.objects.filter(parent=self, is_active=True)
        return Destination.objects.none()
    
    def get_region_name(self):
        """Get the name of the parent region"""
        if self.parent:
            return self.parent.name
        return self.region
    
    def get_gallery_caption(self, image_number=None):
        """Get caption for gallery images"""
        if image_number and self.gallery_captions:
            return self.gallery_captions.get(f'caption_{image_number}', '')
        # If called without number, return a default or handle differently
        return ''
    
    def has_airport(self):
        """Check if this destination has an airport"""
        try:
            from .airport_data import destination_has_airport
            return destination_has_airport(self.name)
        except ImportError:
            # Fallback logic if airport_data.py doesn't exist
            airport_cities = [
                'Yangon', 'Mandalay', 'Naypyidaw', 'Bagan', 'Heho', 'Thandwe',
                'Sittwe', 'Myitkyina', 'Tachileik', 'Kawthaung', 'Dawei', 
                'Myeik', 'Mawlamyine', 'Pathein', 'Loikaw', 'Hakha'
            ]
            return any(airport_city in self.name for airport_city in airport_cities)
    
    def get_airport_info(self):
        """Get airport information for this destination"""
        try:
            from .airport_data import get_airport_info
            return get_airport_info(self.name)
        except ImportError:
            return {'has_airport': False, 'airport_name': 'Unknown'}
    
    def airport_available(self):
        """Alias for has_airport for template compatibility"""
        return self.has_airport()
    
    def get_gallery_images(self):
        """Return list of gallery images that exist"""
        images = []
        for i in range(1, 9):
            img = getattr(self, f'gallery_image{i}')
            if img:
                caption = self.gallery_captions.get(f'caption_{i}', '') if self.gallery_captions else ''
                images.append({
                    'url': img.url,
                    'caption': caption,
                    'number': i
                })
        return images
    
    class Meta:
        ordering = ['name']
# ========== FLIGHT MODEL ==========
class Flight(models.Model):
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
    
    def generate_seat_map(self):
        """Generate a default seat map for the flight"""
        seat_map = {
            'total_rows': 30,
            'seats_per_row': 6,
            'configuration': '3-3',
            'first_class_rows': 4,
            'business_class_rows': 0,
            'economy_class_rows': 26,
            'premium_seats': ['1A', '1B', '1C', '1D', '1E', '1F',
                             '2A', '2B', '2C', '2D', '2E', '2F'],
            'occupied_seats': self.get_real_occupied_seats(),
            'seat_prices': {
                'premium': float(self.price) * 1.5,
                'economy': float(self.price),
                'extra_legroom': float(self.price) * 1.2
            },
            'seat_layout': self.generate_seat_layout() 
        }
        return seat_map
    def generate_seat_layout(self):
        """Generate detailed seat layout with all seat numbers"""
        seat_layout = []
        rows = 30
        seats_per_row = 6
        seat_letters = ['A', 'B', 'C', 'D', 'E', 'F']
        
        for row in range(1, rows + 1):
            row_seats = []
            for col in range(seats_per_row):
                seat_number = f"{row}{seat_letters[col]}"
                seat_type = 'economy'
                
                # Determine seat type
                if seat_number in ['1A', '1B', '1C', '1D', '1E', '1F',
                                  '2A', '2B', '2C', '2D', '2E', '2F']:
                    seat_type = 'first'
                elif row <= 4:
                    seat_type = 'first'
                elif row <= 8:
                    seat_type = 'premium'
                
                row_seats.append({
                    'number': seat_number,
                    'type': seat_type,
                    'row': row,
                    'letter': seat_letters[col],
                    'is_window': col == 0 or col == seats_per_row - 1,
                    'is_aisle': col == 2 or col == 3,
                })
            
            seat_layout.append({
                'row_number': row,
                'seats': row_seats
            })
        
        return seat_layout
    def get_real_occupied_seats(self):
        """Get actually booked seats from database"""
        from .models import BookedSeat
        booked_seats = BookedSeat.objects.filter(
            transport_type='flight',
            transport_id=self.id,
            is_cancelled=False
        ).values_list('seat_number', flat=True)
        return list(booked_seats)


# ========== HOTEL MODEL ==========
# C:\Users\ASUS\MyanmarTravelPlanner\planner\models.py
# REPLACE ONLY the Hotel model section with this:

# ========== HOTEL MODEL ==========
class Hotel(models.Model):
    CATEGORY_CHOICES = [
        ('budget', 'Budget (Under 50,000 MMK)'),
        ('medium', 'Medium (50,000 - 150,000 MMK)'),
        ('luxury', 'Luxury (150,000+ MMK)'),
        ('high', 'High-End (Premium Luxury)'),
    ]
    
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
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='medium')
    amenities = models.JSONField(
        default=list,
        help_text="List of amenities (e.g., ['wifi', 'pool', 'spa'])"
    )
    rating = models.DecimalField(
        max_digits=2, 
        decimal_places=1, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review_count = models.IntegerField(default=0, blank=True, null=True)  # FIXED: Added blank=True, null=True
    image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    description = models.TextField(blank=True)
    gallery_images = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by_admin = models.BooleanField(default=False, help_text="Whether this hotel was created by admin")
    is_real_hotel = models.BooleanField(default=False, help_text="Is this a real hotel from Google Maps?")
    google_place_id = models.CharField(max_length=255, blank=True, null=True)
    
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    check_in_time = models.TimeField(default='14:00')
    check_out_time = models.TimeField(default='12:00')
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['destination', 'category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['price_per_night']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.destination.name}"
    
    def price_in_mmk(self):
        """Return price formatted in MMK"""
        if self.price_per_night:
            return f"{int(self.price_per_night):,} MMK"
        return "0 MMK"
    
    def get_category_display(self):
        """Get display name for category"""
        for code, name in self.CATEGORY_CHOICES:
            if code == self.category:
                return name.split(' (')[0]  # Remove price range from display
        return self.category.title()
    
    def get_category_color(self):
        """Get color for category badge"""
        colors = {
            'budget': 'success',
            'medium': 'warning',
            'luxury': 'danger',
            'high': 'danger',
        }
        return colors.get(self.category, 'secondary')
    
    def get_amenities_display(self):
        """Return formatted amenities string"""
        if not self.amenities:
            return ""
        
        if isinstance(self.amenities, list):
            return ', '.join([amenity.replace('_', ' ').title() for amenity in self.amenities])
        elif isinstance(self.amenities, str):
            return self.amenities
        return str(self.amenities)
    
    def get_amenities_list(self):
        """Return amenities as list"""
        if not self.amenities:
            return []
        
        if isinstance(self.amenities, list):
            return self.amenities
        elif isinstance(self.amenities, str):
            try:
                import json
                parsed = json.loads(self.amenities)
                if isinstance(parsed, list):
                    return parsed
            except:
                pass
            # If it's a comma-separated string
            if ',' in self.amenities:
                return [a.strip() for a in self.amenities.split(',')]
            return [self.amenities.strip()]
        return []
    
    def has_amenity(self, amenity_name):
        """Check if hotel has a specific amenity"""
        amenities_list = self.get_amenities_list()
        return amenity_name in amenities_list
    
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
            'category_color': self.get_category_color(),
            'amenities': self.get_amenities_list()[:5],
            'is_real': self.is_real_hotel,
            'is_our_hotel': self.created_by_admin,
            'image_url': self.image.url if self.image else '',
            'has_image': bool(self.image),
            'gallery_images': self.gallery_images if isinstance(self.gallery_images, list) else [],
            'description': self.description[:100] + '...' if self.description and len(self.description) > 100 else (self.description or '')
        }
    def get_booking_data(self):
        """Return data for booking"""
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price_per_night),
            'price_display': self.price_in_mmk(),
            'category': self.category,
            'category_display': self.get_category_display(),
            'address': self.address,
            'rating': float(self.rating),
            'review_count': self.review_count,
            'is_real_hotel': self.is_real_hotel,
            'amenities': self.get_amenities_list()[:3]
        }
    
    def get_maps_iframe_url(self):
        """Generate Google Maps iframe URL"""
        if not self.address:
            return ""
        
        maps_query = f"{self.name} {self.address} {self.destination.name} Myanmar"
        maps_query_encoded = urllib.parse.quote(maps_query)
        return f"https://maps.google.com/maps?width=100%&height=300&hl=en&q={maps_query_encoded}&t=&z=14&ie=UTF8&iwloc=B&output=embed"
    
    def get_maps_search_url(self):
        """Generate Google Maps search URL"""
        if not self.address:
            return ""
        
        maps_query = f"{self.name} {self.address} {self.destination.name} Myanmar"
        maps_query_encoded = urllib.parse.quote(maps_query)
        return f"https://www.google.com/maps/search/?api=1&query={maps_query_encoded}"
    
    def is_available(self, start_date, end_date, travelers=1):
        """Check if hotel is available for given dates"""
        # This is a simplified version - you might want to add real availability checking
        return self.is_active
    
    def calculate_total_price(self, nights, travelers=1):
        """Calculate total price for stay"""
        if not nights or nights <= 0:
            nights = 1
        
        base_price = float(self.price_per_night)
        total = base_price * nights
        
        # You could add logic for additional travelers here
        return total
    
    def get_total_price_display(self, nights, travelers=1):
        """Get formatted total price"""
        total = self.calculate_total_price(nights, travelers)
        return f"{int(total):,} MMK"


# ========== BUS SERVICE MODEL ==========
class BusService(models.Model):
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


# ========== CAR RENTAL MODEL ==========
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


# ========== TRIP PLAN MODEL ==========
# ========== TRIP PLAN MODEL ==========
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
    selected_plan = models.CharField(max_length=100, blank=True, null=True)
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
        """Calculate number of nights"""
        if self.start_date and self.end_date:
            days = (self.end_date - self.start_date).days
            return max(1, days)
        return 1
    
    def get_total_cost_in_mmk(self):
        """Calculate total cost in MMK including hotel, transport, and base destination cost"""
        total = 0
        nights = self.calculate_nights()
        
        # 1. Hotel cost
        if self.selected_hotel:
            hotel_cost = float(self.selected_hotel.price_per_night) * nights
            total += hotel_cost
        
        # 2. Transport cost
        if self.selected_transport and 'price' in self.selected_transport:
            transport_price = self.selected_transport.get('price', 0)
            # Handle both string and number formats
            try:
                if isinstance(transport_price, str):
                    # Remove any currency symbols and commas
                    import re
                    clean_price = re.sub(r'[^\d.]', '', transport_price)
                    transport_cost = float(clean_price) if clean_price else 0
                else:
                    transport_cost = float(transport_price)
                total += transport_cost
            except (ValueError, TypeError):
                transport_cost = 0
        
        # 3. Destination base cost (activities, food, etc.)
        # Calculate based on destination type, days, and travelers
        destination_cost = self.calculate_destination_base_cost()
        total += destination_cost
        
        return int(total)
    
    def calculate_destination_base_cost(self):
        """Calculate base cost for destination activities, food, etc."""
        nights = self.calculate_nights()
        days = nights + 1 if nights > 0 else 3
        
        # Base cost per traveler per day in MMK
        base_cost_per_day_per_person = {
            'low': 20000,      # Budget
            'medium': 40000,   # Medium
            'high': 70000,     # Luxury
        }
        
        base_rate = base_cost_per_day_per_person.get(self.budget_range, 40000)
        
        # Calculate: base rate × days × travelers
        return int(base_rate * days * self.travelers)
    
    def get_cost_breakdown(self):
        """
        Get detailed cost breakdown (MMK)
        Total = Hotel + Transport + Destination
        """

        nights = self.calculate_nights()

        breakdown = {
            'hotel': 0,
            'transport': 0,
            'destination': 0,
            'total': 0
        }

        # -----------------------
        # HOTEL COST
        # -----------------------
        if self.selected_hotel:
           breakdown['hotel'] = int(
               float(self.selected_hotel.price_per_night) * max(nights, 1)
           )

        # -----------------------
        # TRANSPORT COST (FIXED VERSION)
        # -----------------------
        if self.selected_transport:
            try:
                transport_data = self.selected_transport
                
                # CASE 1: Transport is a model object
                if hasattr(transport_data, 'price'):
                    breakdown['transport'] = float(transport_data.price)
                
                # CASE 2: Transport is a dict (JSON)
                elif isinstance(transport_data, dict):
                    # Try multiple possible locations for the price
                    price = 0
                    
                    # 1. Check direct 'price' key
                    if 'price' in transport_data:
                        price_val = transport_data['price']
                        if isinstance(price_val, (int, float)):
                            price = float(price_val)
                        elif isinstance(price_val, str):
                            import re
                            clean_price = re.sub(r'[^\d.]', '', price_val)
                            price = float(clean_price) if clean_price else 0
                    
                    # 2. Check booking_details.total_price
                    elif transport_data.get('booking_details'):
                        booking_details = transport_data['booking_details']
                        if 'total_price' in booking_details:
                            price_val = booking_details['total_price']
                            if isinstance(price_val, (int, float)):
                                price = float(price_val)
                            elif isinstance(price_val, str):
                                import re
                                clean_price = re.sub(r'[^\d.]', '', price_val)
                                price = float(clean_price) if clean_price else 0
                        
                        # 3. Check booking_details.price_per_seat * travelers
                        elif 'price_per_seat' in booking_details and self.travelers:
                            price_per_seat = booking_details['price_per_seat']
                            if isinstance(price_per_seat, (int, float)):
                                price = float(price_per_seat) * self.travelers
                    
                    breakdown['transport'] = price
                    
            except Exception as e:
                print(f"Transport cost error for trip {self.id}: {e}")
                breakdown['transport'] = 0

        # -----------------------
        # DESTINATION / ACTIVITIES
        # -----------------------
        breakdown['destination'] = int(self.calculate_destination_base_cost())

        # -----------------------
        # TOTAL (FINAL FIX)
        # -----------------------
        breakdown['total'] = int(
            breakdown['hotel'] +
            breakdown['transport'] +
            breakdown['destination']
        )

        return breakdown
    
    def get_total_spent(self):
        """Get total spent for completed/booked trips"""
        if self.status in ['booked', 'completed']:
            return self.get_total_cost_in_mmk()
        return 0
    
    def origin_has_airport(self):
        """Check if origin has airport"""
        return self.origin.has_airport() if self.origin else False
    
    def destination_has_airport(self):
        """Check if destination has airport"""
        return self.destination.has_airport() if self.destination else False
    
    class Meta:
        ordering = ['-created_at']

# ========== TRANSPORT SCHEDULE MODEL ==========
class TransportSchedule(models.Model):
    """Schedule for transportation on specific dates"""
    transport_type = models.CharField(max_length=10, choices=[
        ('flight', 'Flight'),
        ('bus', 'Bus'),
        ('car', 'Car'),
    ])
    transport_id = models.IntegerField()  # ID of Flight, BusService, or CarRental
    travel_date = models.DateField()
    departure_time = models.TimeField(null=True, blank=True)  # For flights/buses
    arrival_time = models.TimeField(null=True, blank=True)    # For flights
    total_seats = models.IntegerField()
    available_seats = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=0, help_text="Price in MMK")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['transport_type', 'transport_id', 'travel_date']
        ordering = ['travel_date', 'departure_time']
        indexes = [
            models.Index(fields=['transport_type', 'travel_date']),
            models.Index(fields=['travel_date', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_transport_type_display()} on {self.travel_date}"
    
    def get_transport_object(self):
        """Get the actual transport object"""
        if self.transport_type == 'flight':
            return Flight.objects.get(id=self.transport_id)
        elif self.transport_type == 'bus':
            return BusService.objects.get(id=self.transport_id)
        elif self.transport_type == 'car':
            return CarRental.objects.get(id=self.transport_id)
        return None
    
    def is_full(self):
        """Check if all seats are booked"""
        return self.available_seats <= 0
    
    def book_seats(self, number_of_seats):
        """Book seats and update availability"""
        if self.available_seats >= number_of_seats:
            self.available_seats -= number_of_seats
            self.save()
            return True
        return False
    
    def cancel_seats(self, number_of_seats):
        """Cancel seats and update availability"""
        self.available_seats += number_of_seats
        self.save()
        return True


# ========== BOOKED SEAT MODEL ==========
class BookedSeat(models.Model):
    """Model to track booked seats for flights and buses"""
    transport_type = models.CharField(max_length=10, choices=[
        ('flight', 'Flight'),
        ('bus', 'Bus'),
    ])
    transport_id = models.IntegerField()
    schedule_date = models.DateField()  # Date of travel
    seat_number = models.CharField(max_length=10)
    trip = models.ForeignKey(TripPlan, on_delete=models.CASCADE, related_name='booked_seats')
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booked_seats')
    booking_time = models.DateTimeField(auto_now_add=True)
    is_cancelled = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['transport_type', 'transport_id', 'schedule_date', 'seat_number']
        ordering = ['transport_type', 'transport_id', 'schedule_date', 'seat_number']
    
    def __str__(self):
        return f"{self.seat_number} on {self.transport_type} {self.transport_id} ({self.schedule_date})"
    
    def get_schedule(self):
        """Get the schedule for this booking"""
        try:
            return TransportSchedule.objects.get(
                transport_type=self.transport_type,
                transport_id=self.transport_id,
                travel_date=self.schedule_date
            )
        except TransportSchedule.DoesNotExist:
            return None