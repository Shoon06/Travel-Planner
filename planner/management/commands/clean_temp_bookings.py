# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\clean_temp_bookings.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from planner.models_room import RoomBooking, RoomAvailability

class Command(BaseCommand):
    help = 'Clean up old temporary bookings and reset availability'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=1,
            help='Number of hours to consider as "old" (default: 1)',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        cutoff = timezone.now() - timedelta(hours=hours)
        
        # FIXED: Use 'booking_time' instead of 'created_at'
        old_temps = RoomBooking.objects.filter(
            status='temporary',
            booking_time__lt=cutoff  # Changed from created_at to booking_time
        )
        
        count = old_temps.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No old temporary bookings found'))
            return
        
        self.stdout.write(f'Found {count} old temporary bookings')
        
        # For each old temporary booking, we need to reset room availability
        for booking in old_temps:
            room = booking.room
            check_in = booking.check_in_date
            check_out = booking.check_out_date
            
            # Calculate date range
            date_range = [check_in + timedelta(days=x) for x in range((check_out - check_in).days)]
            
            # Reset availability for these dates
            for date in date_range:
                RoomAvailability.objects.update_or_create(
                    room=room,
                    date=date,
                    defaults={'is_available': True}
                )
            
            self.stdout.write(f"  - Reset availability for Room {room.room_number} ({check_in} to {check_out})")
        
        # Delete the old temporary bookings
        old_temps.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} old temporary bookings and reset availability')
        )