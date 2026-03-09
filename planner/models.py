# CORRECTED VERSION - WITH PROPER MODEL ORDERING
from django.core.validators import MinValueValidator, MaxValueValidator
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
        null=True,  # MUST have this
        blank=True, # MUST have this
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
    review_count = models.IntegerField(default=0, blank=True, null=True)
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
    
    # ===== NEW ROOM BOOKING METHODS =====
    
    def get_available_rooms(self, check_in_date, check_out_date, guests=1):
        """
        Get all available rooms for given dates.
        Returns rooms that are not booked during the period.
        """
        from .models_room import Room, RoomBooking
        
        # Get all active rooms in this hotel
        all_rooms = Room.objects.filter(hotel=self, is_active=True)
        
        # Get rooms that are booked during this period (including temporary bookings)
        booked_room_ids = RoomBooking.objects.filter(
            room__hotel=self,
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
            is_cancelled=False,
            status__in=['temporary', 'confirmed', 'checked_in']
        ).values_list('room_id', flat=True)
        
        # Available rooms are those not booked
        available_rooms = all_rooms.exclude(id__in=booked_room_ids)
        
        # Filter by occupancy if needed
        if guests:
            available_rooms = available_rooms.filter(room_type__max_occupancy__gte=guests)
        
        return available_rooms
    
    def check_room_availability(self, room_id, check_in_date, check_out_date):
        """
        Check if a specific room is available for given dates.
        Returns True if available, False if booked.
        """
        from .models_room import RoomBooking
        
        conflicting_bookings = RoomBooking.objects.filter(
            room_id=room_id,
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
            is_cancelled=False,
            status__in=['temporary', 'confirmed', 'checked_in']
        ).exists()
        
        return not conflicting_bookings
    
    def get_room_types_summary(self):
        """
        Get summary of room types available in this hotel.
        Returns list of dicts with room type info and counts.
        """
        from .models_room import Room, RoomType
        
        summary = []
        for room_type in RoomType.objects.all():
            total_rooms = Room.objects.filter(hotel=self, room_type=room_type, is_active=True).count()
            available_rooms = Room.objects.filter(
                hotel=self, 
                room_type=room_type, 
                is_active=True
            ).count()  # This doesn't check dates, just total rooms
            
            if total_rooms > 0:
                base_price = self.price_per_night
                room_price = int(float(base_price) * float(room_type.base_price_multiplier))
                
                summary.append({
                    'room_type': room_type,
                    'name': room_type.name,
                    'code': room_type.code,
                    'total': total_rooms,
                    'available': available_rooms,  # Will be filtered by date in view
                    'base_price': room_price,
                    'price_display': f"{room_price:,} MMK",
                    'max_occupancy': room_type.max_occupancy,
                    'description': room_type.description
                })
        
        return summary
    
    def calculate_room_price(self, room_type_code, nights=None):
        """
        Calculate price for a room type.
        If nights provided, returns total price, otherwise returns per night.
        """
        from .models_room import RoomType
        
        try:
            room_type = RoomType.objects.get(code=room_type_code)
            price_per_night = int(float(self.price_per_night) * float(room_type.base_price_multiplier))
            
            if nights:
                return price_per_night * nights
            return price_per_night
        except RoomType.DoesNotExist:
            # Fallback to default prices
            multipliers = {
                'SINGLE': 0.8,
                'DOUBLE': 1.0,
                'TRIPLE': 1.3,
                'SUITE': 2.0,
            }
            multiplier = multipliers.get(room_type_code, 1.0)
            price_per_night = int(float(self.price_per_night) * multiplier)
            
            if nights:
                return price_per_night * nights
            return price_per_night
    
    def get_total_rooms_count(self):
        """Get total number of rooms in this hotel"""
        from .models_room import Room
        return Room.objects.filter(hotel=self, is_active=True).count()
    
    def get_available_rooms_count(self, check_in_date=None, check_out_date=None):
        """
        Get count of available rooms.
        If dates provided, counts rooms available for those dates.
        """
        from .models_room import Room, RoomBooking
        
        if check_in_date and check_out_date:
            # Count rooms not booked during this period
            booked_room_ids = RoomBooking.objects.filter(
                room__hotel=self,
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date,
                is_cancelled=False,
                status__in=['temporary', 'confirmed', 'checked_in']
            ).values_list('room_id', flat=True)
            
            return Room.objects.filter(hotel=self, is_active=True).exclude(id__in=booked_room_ids).count()
        else:
            # Just count all rooms
            return Room.objects.filter(hotel=self, is_active=True).count()
    
    def get_booked_rooms_count(self, check_in_date=None, check_out_date=None):
        """
        Get count of booked rooms.
        If dates provided, counts rooms booked for those dates.
        """
        from .models_room import RoomBooking
        
        if check_in_date and check_out_date:
            return RoomBooking.objects.filter(
                room__hotel=self,
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date,
                is_cancelled=False,
                status__in=['temporary', 'confirmed', 'checked_in']
            ).count()
        else:
            # Count all bookings (not very useful)
            return RoomBooking.objects.filter(room__hotel=self, is_cancelled=False).count()
    
    def is_available(self, start_date, end_date, travelers=1):
        """
        Check if hotel has any available rooms for given dates.
        Overrides the placeholder method.
        """
        available_rooms = self.get_available_rooms(start_date, end_date, travelers)
        return available_rooms.exists()
    
    def calculate_total_price(self, nights, travelers=1):
        """
        Calculate total price for stay.
        This is a base calculation - actual price depends on room type.
        """
        if not nights or nights <= 0:
            nights = 1
        
        base_price = float(self.price_per_night)
        total = base_price * nights
        
        return int(total)
    
    def get_total_price_display(self, nights, travelers=1):
        """Get formatted total price"""
        total = self.calculate_total_price(nights, travelers)
        return f"{total:,} MMK"
    
    def get_room_types_for_dates(self, check_in_date, check_out_date, guests=1):
        """
        Get available room types with counts for specific dates.
        Returns list of dicts with room type info and available count.
        """
        from .models_room import Room, RoomType, RoomBooking
        
        # Get all rooms in this hotel
        all_rooms = Room.objects.filter(hotel=self, is_active=True)
        
        # Get booked room IDs for these dates
        booked_room_ids = RoomBooking.objects.filter(
            room__hotel=self,
            check_in_date__lt=check_out_date,
            check_out_date__gt=check_in_date,
            is_cancelled=False,
            status__in=['temporary', 'confirmed', 'checked_in']
        ).values_list('room_id', flat=True)
        
        # Available rooms are those not booked
        available_rooms = all_rooms.exclude(id__in=booked_room_ids)
        
        # Filter by occupancy if needed
        if guests:
            available_rooms = available_rooms.filter(room_type__max_occupancy__gte=guests)
        
        # Group by room type
        result = []
        for room_type in RoomType.objects.all():
            rooms_of_type = available_rooms.filter(room_type=room_type)
            count = rooms_of_type.count()
            
            if count > 0:
                price_per_night = self.calculate_room_price(room_type.code)
                result.append({
                    'room_type': room_type,
                    'name': room_type.name,
                    'code': room_type.code,
                    'available_count': count,
                    'max_occupancy': room_type.max_occupancy,
                    'price_per_night': price_per_night,
                    'price_display': f"{price_per_night:,} MMK",
                    'rooms': list(rooms_of_type.values('id', 'room_number', 'floor', 'bed_type', 'has_window', 'has_balcony'))
                })
        
        return result
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

# C:\Users\ASUS\MyanmarTravelPlanner\planner\models.py

# ========== TRIP PLAN MODEL ==========
# C:\Users\ASUS\MyanmarTravelPlanner\planner\models.py

# ========== TRIP PLAN MODEL ==========
# C:\Users\ASUS\MyanmarTravelPlanner\planner\models.py

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
    custom_itinerary = models.JSONField(default=dict, blank=True, help_text="Custom itinerary with selected attractions")
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
    
    # ADD THIS FIELD - For storing selected rooms
    selected_rooms = models.JSONField(default=dict, blank=True, help_text="Selected rooms with details")
    
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
        """Calculate total cost in MMK including rooms and transport ONLY"""
        total = 0
        nights = self.calculate_nights()
        
        # 1. Room costs ONLY
        if self.selected_rooms and self.selected_rooms.get('total_price'):
            total += float(self.selected_rooms.get('total_price', 0))
        
        # 2. Transport cost
        if self.selected_transport and 'price' in self.selected_transport:
            transport_price = self.selected_transport.get('price', 0)
            try:
                if isinstance(transport_price, str):
                    import re
                    clean_price = re.sub(r'[^\d.]', '', transport_price)
                    transport_cost = float(clean_price) if clean_price else 0
                else:
                    transport_cost = float(transport_price)
                total += transport_cost
            except (ValueError, TypeError):
                transport_cost = 0
        
        # REMOVED: destination cost
        
        return int(total)
    
    def get_cost_breakdown(self):
        """
        Get detailed cost breakdown (MMK)
        Total = Rooms + Transport ONLY
        """
        nights = self.calculate_nights()

        breakdown = {
            'rooms': 0,
            'transport': 0,
            'total': 0
        }

        # -----------------------
        # ROOMS COST ONLY
        # -----------------------
        if self.selected_rooms and self.selected_rooms.get('total_price'):
            breakdown['rooms'] = int(float(self.selected_rooms.get('total_price', 0)))

        # -----------------------
        # TRANSPORT COST
        # -----------------------
        if self.selected_transport:
            try:
                transport_data = self.selected_transport
                
                if hasattr(transport_data, 'price'):
                    breakdown['transport'] = float(transport_data.price)
                elif isinstance(transport_data, dict):
                    price = 0
                    if 'price' in transport_data:
                        price_val = transport_data['price']
                        if isinstance(price_val, (int, float)):
                            price = float(price_val)
                        elif isinstance(price_val, str):
                            import re
                            clean_price = re.sub(r'[^\d.]', '', price_val)
                            price = float(clean_price) if clean_price else 0
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
                    breakdown['transport'] = price
            except Exception as e:
                print(f"Transport cost error for trip {self.id}: {e}")
                breakdown['transport'] = 0

        # REMOVED: destination cost

        # -----------------------
        # TOTAL
        # -----------------------
        breakdown['total'] = int(
            breakdown['rooms'] +
            breakdown['transport']
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