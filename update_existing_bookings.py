# C:\Users\ASUS\MyanmarTravelPlanner\update_existing_bookings.py
import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models import BookedSeat

print("Setting schedule_date for existing bookings...")

# Count before
count = BookedSeat.objects.count()
print(f"Total bookings: {count}")

if count == 0:
    print("No existing bookings to update.")
else:
    # Update all existing bookings to today's date
    updated = BookedSeat.objects.update(schedule_date=timezone.now().date())
    print(f"Updated {updated} bookings to {timezone.now().date()}")
    
# Verify
null_count = BookedSeat.objects.filter(schedule_date__isnull=True).count()
print(f"Bookings still without date: {null_count}")