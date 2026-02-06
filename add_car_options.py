# Save as: C:\Users\ASUS\MyanmarTravelPlanner\add_car_options.py
import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models import Destination, CarRental, TransportSchedule
from datetime import datetime, timedelta

def add_car_options_to_all_destinations():
    """Add 3 car options (Economy, SUV, Luxury) to all destinations"""
    print("Adding car rental options to all destinations...")
    
    # Get all destinations
    destinations = Destination.objects.filter(is_active=True)
    print(f"Found {destinations.count()} destinations")
    
    # Define 3 car options with different models and prices
    car_options = [
        {
            'type': 'economy',
            'models': ['Toyota Vios', 'Honda City', 'Suzuki Swift', 'Toyota Yaris'],
            'seats': 4,
            'price_range': (30000, 45000),  # MMK per day
            'companies': ['City Car Rental', 'Budget Rent-a-Car', 'Economy Car Hire'],
            'features': ['AC', 'Manual Transmission', 'Radio', 'Airbags'],
            'fuel_types': ['Petrol', 'Diesel']
        },
        {
            'type': 'suv',
            'models': ['Toyota Fortuner', 'Mitsubishi Pajero', 'Suzuki Ertiga', 'Honda CR-V'],
            'seats': 7,
            'price_range': (60000, 90000),  # MMK per day
            'companies': ['Premium Rentals', 'SUV Specialist', 'Family Car Rental'],
            'features': ['AC', 'Automatic Transmission', 'GPS', 'Sunroof', 'Bluetooth'],
            'fuel_types': ['Diesel', 'Petrol']
        },
        {
            'type': 'luxury',
            'models': ['Mercedes E-Class', 'BMW 5 Series', 'Lexus ES', 'Toyota Camry Hybrid'],
            'seats': 5,
            'price_range': (120000, 200000),  # MMK per day
            'companies': ['Luxury Wheels', 'Premium Car Rental', 'Executive Rentals'],
            'features': ['AC', 'Automatic Transmission', 'Leather Seats', 'Premium Sound', 'Sunroof', 'GPS', 'Parking Sensors'],
            'fuel_types': ['Petrol', 'Hybrid']
        }
    ]
    
    car_count = 0
    today = datetime.now().date()
    
    for destination in destinations:
        print(f"\nProcessing {destination.name}...")
        
        # Check how many cars already exist for this destination
        existing_cars = CarRental.objects.filter(location=destination, is_available=True).count()
        
        # We want 3 cars per destination, but don't duplicate if they already exist
        cars_to_add = 3 - existing_cars
        
        if cars_to_add <= 0:
            print(f"  ✓ Already has {existing_cars} cars")
            continue
        
        print(f"  Adding {cars_to_add} car(s)...")
        
        for i in range(cars_to_add):
            # Choose which type to add (prioritize missing types)
            available_types = [option['type'] for option in car_options]
            existing_types = CarRental.objects.filter(
                location=destination, 
                is_available=True
            ).values_list('car_type', flat=True)
            
            # Find a type that doesn't exist yet
            car_type_to_add = None
            for car_type in available_types:
                if car_type not in existing_types:
                    car_type_to_add = car_type
                    break
            
            # If all types exist, just pick one randomly
            if not car_type_to_add:
                car_type_to_add = random.choice(available_types)
            
            # Get the car option details
            car_option = next((opt for opt in car_options if opt['type'] == car_type_to_add), car_options[0])
            
            # Create the car rental
            company = random.choice(car_option['companies'])
            model = random.choice(car_option['models'])
            seats = car_option['seats']
            
            # Random price within range
            min_price, max_price = car_option['price_range']
            price_per_day = Decimal(str(random.randint(min_price, max_price)))
            
            # Random features (2-4 features from the list)
            features = random.sample(car_option['features'], random.randint(2, min(4, len(car_option['features']))))
            
            # Transmission based on features
            transmission = 'Automatic' if 'Automatic Transmission' in features else 'Manual'
            
            # Create car rental
            car = CarRental.objects.create(
                company=company,
                car_model=model,
                car_type=car_type_to_add,
                seats=seats,
                price_per_day=price_per_day,
                features=features,
                is_available=True,
                location=destination,
                transmission=transmission,
                fuel_type=random.choice(car_option['fuel_types']),
                year=random.randint(2018, 2023),
                description=f"{car_type_to_add.title()} car rental in {destination.name} - {model}",
            )
            
            # Create schedules for next 60 days
            create_car_schedules(car, today)
            
            car_count += 1
            print(f"    ✓ Added {company} - {model} ({car_type_to_add}) - {price_per_day:,} MMK/day")
    
    print(f"\n{'='*60}")
    print(f"CAR RENTAL POPULATION COMPLETE!")
    print(f"{'='*60}")
    print(f"Total cars added: {car_count}")
    print(f"Total cars in database: {CarRental.objects.count()}")
    print(f"Destinations with cars: {CarRental.objects.values('location').distinct().count()}")
    
    # Show summary by type
    print(f"\nCar type distribution:")
    for car_type in ['economy', 'suv', 'luxury']:
        count = CarRental.objects.filter(car_type=car_type).count()
        print(f"  {car_type.title()}: {count} cars")
    
    return car_count

def create_car_schedules(car, today):
    """Create schedules for a car for next 60 days"""
    schedule_count = 0
    
    for day in range(60):
        schedule_date = today + timedelta(days=day)
        
        # Price variation: +25% on weekends
        is_weekend = schedule_date.weekday() >= 5
        price_multiplier = 1.25 if is_weekend else 1.0
        schedule_price = Decimal(str(float(car.price_per_day) * price_multiplier))
        
        # Availability: 80% chance on weekdays, 50% on weekends
        if is_weekend:
            available_seats = random.choice([car.seats, 0, car.seats])
        else:
            available_seats = random.choice([car.seats, car.seats, car.seats, 0])
        
        # Check if schedule already exists
        schedule_exists = TransportSchedule.objects.filter(
            transport_type='car',
            transport_id=car.id,
            travel_date=schedule_date
        ).exists()
        
        if not schedule_exists:
            TransportSchedule.objects.create(
                transport_type='car',
                transport_id=car.id,
                travel_date=schedule_date,
                total_seats=car.seats,
                available_seats=available_seats,
                price=schedule_price,
                is_active=True
            )
            schedule_count += 1
    
    return schedule_count

def check_car_coverage():
    """Check which destinations have cars and which don't"""
    print("\nChecking car rental coverage...")
    
    destinations = Destination.objects.filter(is_active=True).order_by('name')
    
    print(f"\n{'Destination':<30} {'Cars Available':<15} {'Types Available'}")
    print("-" * 70)
    
    for destination in destinations:
        cars = CarRental.objects.filter(location=destination, is_available=True)
        car_count = cars.count()
        car_types = ", ".join(sorted(set(cars.values_list('car_type', flat=True))))
        
        status = "✓" if car_count >= 2 else "⚠" if car_count == 1 else "✗"
        
        print(f"{destination.name:<30} {f'{status} {car_count} cars':<15} {car_types}")
    
    # Summary
    destinations_with_cars = CarRental.objects.values('location').distinct().count()
    total_destinations = destinations.count()
    
    print(f"\nSummary:")
    print(f"  Total destinations: {total_destinations}")
    print(f"  Destinations with cars: {destinations_with_cars}")
    print(f"  Coverage: {(destinations_with_cars/total_destinations*100):.1f}%")

if __name__ == '__main__':
    # First, add car options
    cars_added = add_car_options_to_all_destinations()
    
    # Then, check coverage
    check_car_coverage()
    
    # Optional: Fix any destinations still missing cars
    print("\nWould you like to ensure ALL destinations have at least 3 cars? (y/n)")
    response = input().strip().lower()
    
if response == 'y':
    print("\nRe-running car population to ensure minimum cars...")
    add_car_options_to_all_destinations()
    check_car_coverage()