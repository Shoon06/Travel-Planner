import os
import sys
import django
from decimal import Decimal
from datetime import time, timedelta, date
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Destination, Hotel, Flight, BusService, CarRental, TripPlan
from users.models import CustomUser
from django.contrib.auth.hashers import make_password

def create_destinations():
    """Create destinations with simplified approach"""
    print("\n1. Creating destinations...")
    
    destinations = [
        {'name': 'Yangon', 'region': 'Lower Myanmar', 'type': 'city'},
        {'name': 'Mandalay', 'region': 'Central Myanmar', 'type': 'city'},
        {'name': 'Bagan', 'region': 'Mandalay Region', 'type': 'city'},
        {'name': 'Inle Lake', 'region': 'Shan State', 'type': 'attraction'},
        {'name': 'Ngapali Beach', 'region': 'Rakhine State', 'type': 'attraction'},
        {'name': 'Pyin Oo Lwin', 'region': 'Mandalay Region', 'type': 'town'},
        {'name': 'Hpa-An', 'region': 'Kayin State', 'type': 'town'},
        {'name': 'Kalaw', 'region': 'Shan State', 'type': 'town'},
    ]
    
    created_count = 0
    for dest_data in destinations:
        # Check if destination exists
        if not Destination.objects.filter(name=dest_data['name']).exists():
            Destination.objects.create(
                name=dest_data['name'],
                region=dest_data['region'],
                type=dest_data['type'],
                description=f"Explore {dest_data['name']} in {dest_data['region']}",
                is_active=True
            )
            created_count += 1
            print(f"  Created: {dest_data['name']}")
    
    print(f"  Total destinations: {Destination.objects.count()} (Created: {created_count})")
    return Destination.objects.all()

def create_users():
    """Create sample users"""
    print("\n2. Creating sample users...")
    
    users_data = [
        {'username': 'john_traveler', 'email': 'john@example.com', 'password': 'travel123', 'user_type': 'user'},
        {'username': 'sarah_explorer', 'email': 'sarah@example.com', 'password': 'explore2024', 'user_type': 'user'},
        {'username': 'mike_adventurer', 'email': 'mike@example.com', 'password': 'adventure!', 'user_type': 'user'},
        {'username': 'lisa_wanderer', 'email': 'lisa@example.com', 'password': 'wanderlust', 'user_type': 'user'},
        {'username': 'admin_user', 'email': 'admin@travel.mm', 'password': 'admin123', 'user_type': 'admin'},
    ]
    
    for user_data in users_data:
        if not CustomUser.objects.filter(email=user_data['email']).exists():
            CustomUser.objects.create(
                username=user_data['username'],
                email=user_data['email'],
                password=make_password(user_data['password']),
                user_type=user_data['user_type'],
                is_active=True
            )
            print(f"  Created user: {user_data['username']}")
    
    print(f"  Total users: {CustomUser.objects.count()}")

def create_hotels(destinations):
    """Create hotels for destinations"""
    print("\n3. Creating hotels...")
    
    hotel_templates = [
        {
            'name': 'Luxury Resort',
            'category': 'luxury',
            'price_range': (120, 250),
            'amenities': ['wifi', 'pool', 'spa', 'gym', 'restaurant', 'bar'],
            'rating': (4.5, 4.9),
            'review_range': (500, 1500)
        },
        {
            'name': 'Mid-Range Hotel',
            'category': 'medium',
            'price_range': (60, 120),
            'amenities': ['wifi', 'restaurant', 'air conditioning', 'tv'],
            'rating': (4.0, 4.4),
            'review_range': (200, 800)
        },
        {
            'name': 'Budget Inn',
            'category': 'budget',
            'price_range': (25, 60),
            'amenities': ['wifi', 'breakfast', 'air conditioning'],
            'rating': (3.5, 4.2),
            'review_range': (100, 500)
        },
        {
            'name': 'Boutique Hotel',
            'category': 'medium',
            'price_range': (80, 150),
            'amenities': ['wifi', 'spa', 'restaurant', 'bar', 'concierge'],
            'rating': (4.2, 4.7),
            'review_range': (300, 900)
        },
        {
            'name': 'Business Hotel',
            'category': 'luxury',
            'price_range': (100, 200),
            'amenities': ['wifi', 'business center', 'gym', 'restaurant', 'conference rooms'],
            'rating': (4.3, 4.8),
            'review_range': (400, 1200)
        }
    ]
    
    created_count = 0
    for destination in destinations:
        for i, template in enumerate(hotel_templates):
            hotel_name = f"{template['name']} {destination.name}"
            
            if not Hotel.objects.filter(name=hotel_name).exists():
                Hotel.objects.create(
                    name=hotel_name,
                    destination=destination,
                    address=f"123 Main Street, {destination.name}",
                    price_per_night=Decimal(str(random.uniform(*template['price_range']))),
                    category=template['category'],
                    amenities=template['amenities'],
                    rating=Decimal(str(round(random.uniform(*template['rating']), 1))),
                    review_count=random.randint(*template['review_range']),
                    description=f"Beautiful {template['category']} hotel in {destination.name}",
                    is_active=True
                )
                created_count += 1
    
    print(f"  Total hotels: {Hotel.objects.count()} (Created: {created_count})")

def create_flights(destinations):
    """Create flight connections between destinations"""
    print("\n4. Creating flights...")
    
    airlines = ['Air KBZ', 'Myanmar National Airlines', 'Golden Myanmar Airlines', 'Mann Yadanarpon Airlines']
    
    created_count = 0
    # Create flights from Yangon to other destinations
    yangon = Destination.objects.get(name='Yangon')
    
    for destination in destinations.exclude(name='Yangon'):
        for i in range(3):  # 3 flights per route
            flight_number = f"{random.choice(['K7', 'UB', 'GY', '7Y'])} {random.randint(100, 999)}"
            
            if not Flight.objects.filter(flight_number=flight_number).exists():
                departure_hour = random.choice([6, 10, 14, 18, 22])
                duration_hours = 1.5 if destination.name in ['Mandalay', 'Bagan'] else 2.0
                
                Flight.objects.create(
                    airline=random.choice(airlines),
                    flight_number=flight_number,
                    departure=yangon,
                    arrival=destination,
                    departure_time=time(departure_hour, random.choice([0, 15, 30, 45])),
                    arrival_time=time((departure_hour + int(duration_hours)) % 24, random.choice([0, 15, 30, 45])),
                    duration=timedelta(hours=int(duration_hours), minutes=int((duration_hours % 1) * 60)),
                    price=Decimal(str(random.uniform(50, 150))),
                    category=random.choice(['low', 'medium', 'high']),
                    total_seats=random.choice([120, 150, 180]),
                    available_seats=random.randint(80, 150),
                    description=f"Flight from Yangon to {destination.name}",
                    is_active=True
                )
                created_count += 1
    
    print(f"  Total flights: {Flight.objects.count()} (Created: {created_count})")

def create_buses(destinations):
    """Create bus services between destinations"""
    print("\n5. Creating bus services...")
    
    bus_companies = ['JJ Express', 'Elite Bus', 'Luxury Coach', 'Mandalar Express', 'City Express']
    
    created_count = 0
    yangon = Destination.objects.get(name='Yangon')
    
    for destination in destinations.exclude(name='Yangon'):
        for i in range(2):  # 2 buses per route
            company = random.choice(bus_companies)
            
            if not BusService.objects.filter(company=company, departure=yangon, arrival=destination).exists():
                departure_hour = random.choice([18, 19, 20, 21, 22])
                duration_hours = random.choice([8, 9, 10, 11, 12])
                
                BusService.objects.create(
                    company=company,
                    departure=yangon,
                    arrival=destination,
                    departure_time=time(departure_hour, random.choice([0, 30])),
                    duration=timedelta(hours=duration_hours),
                    price=Decimal(str(random.uniform(15, 60))),
                    bus_type=random.choice(['standard', 'vip', 'luxury']),
                    total_seats=random.choice([30, 40, 45]),
                    available_seats=random.randint(20, 40),
                    bus_number=f"BUS{random.randint(100, 999)}",
                    description=f"Bus service from Yangon to {destination.name}",
                    is_active=True
                )
                created_count += 1
    
    print(f"  Total buses: {BusService.objects.count()} (Created: {created_count})")

def create_cars(destinations):
    """Create car rentals at each destination"""
    print("\n6. Creating car rentals...")
    
    car_types = [
        {'model': 'Toyota Vios', 'type': 'economy', 'seats': 4, 'price_range': (30, 50)},
        {'model': 'Toyota Fortuner', 'type': 'suv', 'seats': 7, 'price_range': (60, 90)},
        {'model': 'Mercedes E-Class', 'type': 'luxury', 'seats': 4, 'price_range': (100, 150)},
        {'model': 'Suzuki Ertiga', 'type': 'van', 'seats': 7, 'price_range': (45, 70)},
        {'model': 'Honda City', 'type': 'economy', 'seats': 4, 'price_range': (35, 55)},
    ]
    
    companies = ['City Car Rental', 'Premium Rentals', 'Luxury Wheels', 'Budget Rentals', 'Adventure Rentals']
    
    created_count = 0
    for destination in destinations:
        for i in range(3):  # 3 cars per destination
            car_type = random.choice(car_types)
            company = random.choice(companies)
            
            car_name = f"{car_type['model']} - {company}"
            
            if not CarRental.objects.filter(car_model=car_type['model'], company=company, location=destination).exists():
                CarRental.objects.create(
                    company=company,
                    car_model=car_type['model'],
                    car_type=car_type['type'],
                    seats=car_type['seats'],
                    price_per_day=Decimal(str(random.uniform(*car_type['price_range']))),
                    features=['AC', 'GPS', 'Automatic', 'Airbags', 'Bluetooth'][:random.randint(2, 5)],
                    is_available=random.choice([True, True, True, False]),  # 75% available
                    location=destination,
                    description=f"{car_type['type'].title()} car rental in {destination.name}",
                    transmission=random.choice(['automatic', 'manual']),
                    year=random.randint(2018, 2023)
                )
                created_count += 1
    
    print(f"  Total cars: {CarRental.objects.count()} (Created: {created_count})")

def create_sample_trips():
    """Create sample trip plans"""
    print("\n7. Creating sample trips...")
    
    users = CustomUser.objects.filter(user_type='user')[:3]
    destinations = Destination.objects.all()[:3]
    
    created_count = 0
    for user in users:
        for destination in destinations:
            if not TripPlan.objects.filter(user=user, destination=destination).exists():
                start_date = date.today() + timedelta(days=random.randint(30, 90))
                
                TripPlan.objects.create(
                    user=user,
                    destination=destination,
                    start_date=start_date,
                    end_date=start_date + timedelta(days=random.randint(3, 7)),
                    travelers=random.randint(1, 4),
                    budget_range=random.choice(['low', 'medium', 'high']),
                    status=random.choice(['draft', 'planning', 'booked', 'completed']),
                    notes=f"Trip to {destination.name} planned by {user.username}"
                )
                created_count += 1
    
    print(f"  Total trips: {TripPlan.objects.count()} (Created: {created_count})")

def main():
    print("=== POPULATING TRAVEL SYSTEM DATA ===")
    
    # Create destinations first
    destinations = create_destinations()
    
    # Create other data
    create_users()
    create_hotels(destinations)
    create_flights(destinations)
    create_buses(destinations)
    create_cars(destinations)
    create_sample_trips()
    
    print("\n=== DATA POPULATION COMPLETE ===")
    print("\nSummary:")
    print(f"  Users: {CustomUser.objects.count()}")
    print(f"  Destinations: {Destination.objects.count()}")
    print(f"  Hotels: {Hotel.objects.count()}")
    print(f"  Flights: {Flight.objects.count()}")
    print(f"  Buses: {BusService.objects.count()}")
    print(f"  Cars: {CarRental.objects.count()}")
    print(f"  Trips: {TripPlan.objects.count()}")
    
    print("\nAdmin Credentials:")
    print("  Email: admin@travel.mm")
    print("  Password: admin123")
    print("\nRegular User Credentials:")
    print("  Email: john@example.com")
    print("  Password: travel123")

if __name__ == "__main__":
    main()