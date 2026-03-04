from django.core.management.base import BaseCommand
from planner.models import Flight, BusService, CarRental, TransportSchedule
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Create transport schedules for the next 30 days'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Creating transport schedules...')
        
        # Get today and next 30 days
        today = timezone.now().date()
        dates = [today + timedelta(days=i) for i in range(30)]
        
        # Create schedules for flights
        flights = Flight.objects.filter(is_active=True)
        for flight in flights:
            for date in dates:
                # Skip weekends for some flights (optional)
                if date.weekday() >= 5 and random.random() > 0.7:
                    continue
                    
                # Check if schedule already exists
                schedule_exists = TransportSchedule.objects.filter(
                    transport_type='flight',
                    transport_id=flight.id,
                    travel_date=date
                ).exists()
                
                if not schedule_exists:
                    # Adjust available seats based on date (weekends are busier)
                    base_seats = flight.total_seats
                    if date.weekday() >= 5:  # Weekend
                        available_seats = random.randint(int(base_seats * 0.3), int(base_seats * 0.7))
                    else:  # Weekday
                        available_seats = random.randint(int(base_seats * 0.5), int(base_seats * 0.9))
                    
                    # Slight price variation based on date
                    price_variation = random.uniform(0.9, 1.2)
                    adjusted_price = int(float(flight.price) * price_variation)
                    
                    TransportSchedule.objects.create(
                        transport_type='flight',
                        transport_id=flight.id,
                        travel_date=date,
                        departure_time=flight.departure_time,
                        arrival_time=flight.arrival_time,
                        total_seats=flight.total_seats,
                        available_seats=available_seats,
                        price=adjusted_price,
                        is_active=True
                    )
        
        self.stdout.write(f'Created schedules for {flights.count()} flights')
        
        # Create schedules for buses
        buses = BusService.objects.filter(is_active=True)
        for bus in buses:
            for date in dates:
                schedule_exists = TransportSchedule.objects.filter(
                    transport_type='bus',
                    transport_id=bus.id,
                    travel_date=date
                ).exists()
                
                if not schedule_exists:
                    # Adjust availability
                    base_seats = bus.total_seats
                    if date.weekday() >= 5:  # Weekend
                        available_seats = random.randint(int(base_seats * 0.2), int(base_seats * 0.6))
                    else:
                        available_seats = random.randint(int(base_seats * 0.4), int(base_seats * 0.8))
                    
                    price_variation = random.uniform(0.8, 1.3)
                    adjusted_price = int(float(bus.price) * price_variation)
                    
                    TransportSchedule.objects.create(
                        transport_type='bus',
                        transport_id=bus.id,
                        travel_date=date,
                        departure_time=bus.departure_time,
                        total_seats=bus.total_seats,
                        available_seats=available_seats,
                        price=adjusted_price,
                        is_active=True
                    )
        
        self.stdout.write(f'Created schedules for {buses.count()} buses')
        
        # Create schedules for cars (available every day)
        cars = CarRental.objects.filter(is_available=True)
        for car in cars:
            for date in dates:
                schedule_exists = TransportSchedule.objects.filter(
                    transport_type='car',
                    transport_id=car.id,
                    travel_date=date
                ).exists()
                
                if not schedule_exists:
                    # Car availability - 90% chance of being available
                    is_available = random.random() > 0.1
                    
                    TransportSchedule.objects.create(
                        transport_type='car',
                        transport_id=car.id,
                        travel_date=date,
                        total_seats=car.seats,
                        available_seats=car.seats if is_available else 0,
                        price=car.price_per_day,
                        is_active=is_available
                    )
        
        self.stdout.write(f'Created schedules for {cars.count()} cars')
        
        total_schedules = TransportSchedule.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Total schedules created: {total_schedules}'))
        
        # Print statistics
        flights_today = TransportSchedule.objects.filter(
            transport_type='flight',
            travel_date=today,
            is_active=True
        ).count()
        
        buses_today = TransportSchedule.objects.filter(
            transport_type='bus',
            travel_date=today,
            is_active=True
        ).count()
        
        cars_today = TransportSchedule.objects.filter(
            transport_type='car',
            travel_date=today,
            is_active=True
        ).count()
        
        self.stdout.write(f'\nStatistics for {today}:')
        self.stdout.write(f'  Flights available: {flights_today}')
        self.stdout.write(f'  Buses available: {buses_today}')
        self.stdout.write(f'  Cars available: {cars_today}')