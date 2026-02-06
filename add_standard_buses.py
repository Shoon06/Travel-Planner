# Save as: C:\Users\ASUS\MyanmarTravelPlanner\add_standard_buses.py
import os
import django
import random
from datetime import datetime, timedelta, time
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models import Destination, BusService, TransportSchedule

def add_missing_standard_buses():
    """Add standard class buses for any missing routes"""
    print("Adding standard class buses for missing routes...")
    
    # Get all destinations
    destinations = Destination.objects.filter(is_active=True)
    print(f"Found {destinations.count()} destinations")
    
    bus_companies = ['JJ Express', 'Elite Express', 'Shwe Mandalar', 'Mandalar Express', 'Lumbini Bus']
    
    bus_count = 0
    missing_routes = 0
    
    # Check all possible routes
    for departure in destinations:
        for arrival in destinations:
            if departure != arrival:
                # Check if standard bus already exists for this route
                standard_bus_exists = BusService.objects.filter(
                    departure=departure,
                    arrival=arrival,
                    bus_type='standard',
                    is_active=True
                ).exists()
                
                if not standard_bus_exists:
                    missing_routes += 1
                    
                    # Create a standard bus for this route
                    company = random.choice(bus_companies)
                    
                    # Standard bus pricing: 10,000 - 25,000 MMK
                    price = Decimal(str(random.randint(10000, 25000)))
                    total_seats = random.randint(40, 50)
                    available_seats = random.randint(int(total_seats * 0.6), total_seats)
                    
                    # Evening departure
                    departure_hour = random.choice([18, 19, 20])
                    departure_minute = random.choice([0, 15, 30, 45])
                    
                    departure_time_obj = time(departure_hour, departure_minute)
                    
                    # Duration based on typical Myanmar distances
                    duration_hours = random.randint(4, 12)
                    
                    bus = BusService.objects.create(
                        company=company,
                        departure=departure,
                        arrival=arrival,
                        departure_time=departure_time_obj,
                        duration=timedelta(hours=duration_hours),
                        price=price,
                        bus_type='standard',
                        total_seats=total_seats,
                        available_seats=available_seats,
                        bus_number=f"STD{random.randint(1000, 9999)}",
                        description=f"Standard bus service from {departure.name} to {arrival.name}",
                        is_active=True
                    )
                    
                    # Create schedules for next 60 days
                    today = datetime.now().date()
                    
                    for day in range(60):
                        schedule_date = today + timedelta(days=day)
                        
                        # Price variation: +15% on weekends
                        is_weekend = schedule_date.weekday() >= 5
                        price_multiplier = 1.15 if is_weekend else 1.0
                        schedule_price = Decimal(str(float(price) * price_multiplier))
                        
                        # Availability: 40-80% of seats
                        schedule_seats = random.randint(
                            int(total_seats * 0.4),
                            int(total_seats * 0.8)
                        )
                        
                        TransportSchedule.objects.create(
                            transport_type='bus',
                            transport_id=bus.id,
                            travel_date=schedule_date,
                            departure_time=departure_time_obj,
                            total_seats=total_seats,
                            available_seats=schedule_seats,
                            price=schedule_price,
                            is_active=True
                        )
                    
                    bus_count += 1
                    
                    # Print progress every 10 buses
                    if bus_count % 10 == 0:
                        print(f"Created {bus_count} standard buses...")
    
    print(f"\nAdded {bus_count} standard buses for {missing_routes} missing routes")
    print(f"Total buses now: {BusService.objects.count()}")
    
    return bus_count

if __name__ == '__main__':
    add_missing_standard_buses()