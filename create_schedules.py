# C:\Users\ASUS\MyanmarTravelPlanner\create_schedules.py
import os
import django
import sys
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models import BusService, TransportSchedule

def create_bus_schedules():
    """Create schedules for all buses for the next 90 days"""
    # Get all active buses
    buses = BusService.objects.filter(is_active=True)
    
    if not buses.exists():
        print("No active buses found!")
        return
    
    print(f"Found {buses.count()} active buses")
    
    # Date range: today to 90 days from now
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=90)
    
    schedules_created = 0
    
    for bus in buses:
        print(f"\nProcessing bus: {bus.company} ({bus.departure.name} → {bus.arrival.name})")
        
        current_date = start_date
        while current_date <= end_date:
            # Create schedule for this date
            schedule, created = TransportSchedule.objects.get_or_create(
                transport_type='bus',
                transport_id=bus.id,
                travel_date=current_date,
                defaults={
                    'departure_time': bus.departure_time,
                    'total_seats': bus.total_seats,
                    'available_seats': bus.available_seats,
                    'price': bus.price,
                    'is_active': bus.is_active,
                }
            )
            
            if created:
                schedules_created += 1
            
            current_date += timedelta(days=1)
        
        print(f"  Created schedules for {bus.company} from {start_date} to {end_date}")
    
    print(f"\n✅ Successfully created {schedules_created} bus schedules!")
    print(f"📅 Schedules are available from {start_date} to {end_date}")
    
    # Show some sample schedules
    sample_schedules = TransportSchedule.objects.filter(
        transport_type='bus'
    ).order_by('travel_date')[:5]
    
    print("\n📋 Sample schedules created:")
    for schedule in sample_schedules:
        bus = BusService.objects.get(id=schedule.transport_id)
        print(f"  - {bus.company}: {schedule.travel_date} - {schedule.available_seats} seats @ {schedule.price} MMK")

if __name__ == '__main__':
    create_bus_schedules()