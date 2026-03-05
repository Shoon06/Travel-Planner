# C:\Users\ASUS\MyanmarTravelPlanner\planner\models_room.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from .models import Hotel

class RoomType(models.Model):
    """Room type categories like Single, Double, Triple, Suite"""
    name = models.CharField(max_length=50)  # Single, Double, Triple, Suite
    code = models.CharField(max_length=20, unique=True)  # SINGLE, DOUBLE, TRIPLE
    description = models.TextField(blank=True)
    max_occupancy = models.IntegerField(default=2)
    base_price_multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Room(models.Model):
    """Individual rooms in hotels (like seats in transport)"""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, related_name='rooms')
    room_number = models.CharField(max_length=20)
    floor = models.IntegerField(default=1)
    
    # Room-specific price (override hotel base price)
    custom_price = models.DecimalField(
        max_digits=10, decimal_places=0, null=True, blank=True,
        help_text="Override hotel price per night for this room"
    )
    
    # Room features/amenities specific to this room
    features = models.JSONField(default=list, blank=True)
    
    # Status flags
    is_active = models.BooleanField(default=True)
    needs_maintenance = models.BooleanField(default=False)
    
    # Room details
    bed_type = models.CharField(max_length=50, blank=True)  # King, Queen, Twin, etc.
    has_window = models.BooleanField(default=True)
    has_balcony = models.BooleanField(default=False)
    square_feet = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['hotel', 'room_number']
        ordering = ['hotel', 'room_number']
        indexes = [
            models.Index(fields=['hotel', 'is_active']),
            models.Index(fields=['room_type']),
        ]
    
    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number} ({self.room_type.name})"
    
    def get_price_per_night(self):
        """Get effective price for this room"""
        if self.custom_price:
            return self.custom_price
        # Use hotel price multiplied by room type factor
        return int(float(self.hotel.price_per_night) * float(self.room_type.base_price_multiplier))
    
    def get_availability_for_dates(self, check_in, check_out):
        """Check if room is available for given dates"""
        from .models_room import RoomBooking, RoomAvailability
        
        # Check for bookings
        has_booking = RoomBooking.objects.filter(
            room=self,
            check_in_date__lt=check_out,
            check_out_date__gt=check_in,
            is_cancelled=False,
            status__in=['temporary', 'confirmed', 'checked_in']
        ).exists()
        
        if has_booking:
            return False
        
        # Check availability records
        date_range = [check_in + timedelta(days=x) for x in range((check_out - check_in).days)]
        for date in date_range:
            avail = RoomAvailability.objects.filter(
                room=self,
                date=date,
                is_available=False
            ).exists()
            if avail:
                return False
        
        return True

class RoomAvailability(models.Model):
    """Track room availability for specific dates (60 days in advance)"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    is_available = models.BooleanField(default=True)
    price_override = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    
    class Meta:
        unique_together = ['room', 'date']
        ordering = ['room', 'date']
        indexes = [
            models.Index(fields=['date', 'is_available']),
            models.Index(fields=['room', 'date']),
        ]
    
    def __str__(self):
        return f"{self.room} - {self.date} - {'Available' if self.is_available else 'Booked'}"

class RoomBooking(models.Model):
    """Booking for specific rooms (like BookedSeat for transport)"""
    BOOKING_STATUS = [
        ('temporary', 'Temporary (Not Confirmed)'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    trip = models.ForeignKey('TripPlan', on_delete=models.CASCADE, related_name='room_bookings')
    booked_by = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='room_bookings')
    
    # Booking details
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    guests = models.IntegerField(default=1)
    
    # Price at time of booking
    price_per_night = models.DecimalField(max_digits=10, decimal_places=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=0)
    
    # Status
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='temporary')
    is_cancelled = models.BooleanField(default=False)
    
    # Special requests
    special_requests = models.TextField(blank=True)
    
    # Timestamps
    booking_time = models.DateTimeField(auto_now_add=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-booking_time']
        indexes = [
            models.Index(fields=['room', 'check_in_date', 'check_out_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Booking for {self.room} ({self.check_in_date} to {self.check_out_date})"
    
    def calculate_nights(self):
        """Calculate number of nights"""
        return (self.check_out_date - self.check_in_date).days
    
    def is_active_booking(self):
        """Check if booking is active (not cancelled and dates valid)"""
        return not self.is_cancelled and self.status not in ['cancelled']
    
    def confirm_booking(self):
        """Confirm booking and lock rooms"""
        if self.status == 'temporary':
            self.status = 'confirmed'
            self.save()
            
            # Update availability records
            from .models_room import RoomAvailability
            date_range = [self.check_in_date + timedelta(days=x) for x in range(self.calculate_nights())]
            for date in date_range:
                RoomAvailability.objects.update_or_create(
                    room=self.room,
                    date=date,
                    defaults={'is_available': False}
                )
    
    def cancel_booking(self):
        """Cancel booking and release rooms"""
        if self.status in ['temporary', 'confirmed']:
            self.is_cancelled = True
            self.status = 'cancelled'
            self.save()
            
            # Update availability records
            from .models_room import RoomAvailability
            date_range = [self.check_in_date + timedelta(days=x) for x in range(self.calculate_nights())]
            for date in date_range:
                RoomAvailability.objects.update_or_create(
                    room=self.room,
                    date=date,
                    defaults={'is_available': True}
                )