"""
COMPREHENSIVE TRANSPORT DATA POPULATION SCRIPT
This creates transport options for ALL city pairs in Myanmar
"""
import os
import django
import random
from datetime import datetime, timedelta, time
from decimal import Decimal
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models import Destination, Flight, BusService, CarRental, TransportSchedule, Airline

def create_transport_schedules():
    """Create schedules for next 30 days for all transport"""
    print("Creating transport schedules for all transport options...")
    
    # Get all destinations
    destinations = list(Destination.objects.filter(is_active=True))
    print(f"Found {len(destinations)} destinations")
    
    # Get all flights
    flights = Flight.objects.filter(is_active=True)
    print(f"Found {flights.count()} flights")
    
    # Create schedules for flights
    flight_schedule_count = 0
    for flight in flights:
        for day in range(30):  # Create schedules for next 30 days
            schedule_date = timezone.now().date() + timedelta(days=day)
            
            # Calculate dynamic price (higher on weekends)
            is_weekend = schedule_date.weekday() >= 5  # 5=Saturday, 6=Sunday
            price_multiplier = 1.2 if is_weekend else 1.0
            schedule_price = Decimal(str(float(flight.price) * price_multiplier))
            
            # Calculate dynamic availability (fewer seats on popular days)
            base_available = flight.available_seats
            if is_weekend:
                available_seats = max(5, int(base_available * 0.7))  # 30% fewer on weekends
            else:
                available_seats = max(10, int(base_available * 0.9))
            
            # Random booking simulation
            booked_seats = random.randint(0, int(available_seats * 0.3))
            final_available = available_seats - booked_seats
            
            schedule, created = TransportSchedule.objects.get_or_create(
                transport_type='flight',
                transport_id=flight.id,
                travel_date=schedule_date,
                defaults={
                    'departure_time': flight.departure_time,
                    'arrival_time': flight.arrival_time,
                    'total_seats': flight.total_seats,
                    'available_seats': final_available,
                    'price': schedule_price,
                    'is_active': True
                }
            )
            
            if created:
                flight_schedule_count += 1
    
    print(f"Created {flight_schedule_count} flight schedules")
    
    # Get all buses
    buses = BusService.objects.filter(is_active=True)
    print(f"Found {buses.count()} buses")
    
    # Create schedules for buses
    bus_schedule_count = 0
    for bus in buses:
        for day in range(30):  # Next 30 days
            schedule_date = timezone.now().date() + timedelta(days=day)
            
            # Dynamic pricing
            is_weekend = schedule_date.weekday() >= 5
            price_multiplier = 1.15 if is_weekend else 1.0
            schedule_price = Decimal(str(float(bus.price) * price_multiplier))
            
            # Dynamic availability
            base_available = bus.available_seats
            if is_weekend:
                available_seats = max(3, int(base_available * 0.6))
            else:
                available_seats = max(5, int(base_available * 0.8))
            
            # Random booking
            booked_seats = random.randint(0, int(available_seats * 0.4))
            final_available = available_seats - booked_seats
            
            schedule, created = TransportSchedule.objects.get_or_create(
                transport_type='bus',
                transport_id=bus.id,
                travel_date=schedule_date,
                defaults={
                    'departure_time': bus.departure_time,
                    'total_seats': bus.total_seats,
                    'available_seats': final_available,
                    'price': schedule_price,
                    'is_active': True
                }
            )
            
            if created:
                bus_schedule_count += 1
    
    print(f"Created {bus_schedule_count} bus schedules")
    
    # Get all cars
    cars = CarRental.objects.filter(is_available=True)
    print(f"Found {cars.count()} car rentals")
    
    # Create schedules for cars
    car_schedule_count = 0
    for car in cars:
        for day in range(30):  # Next 30 days
            schedule_date = timezone.now().date() + timedelta(days=day)
            
            # Dynamic pricing (higher on weekends)
            is_weekend = schedule_date.weekday() >= 5
            price_multiplier = 1.25 if is_weekend else 1.0
            schedule_price = Decimal(str(float(car.price_per_day) * price_multiplier))
            
            # Car availability (less available on weekends)
            if is_weekend:
                available_seats = random.choice([0, 1])  # 50% chance of availability
            else:
                available_seats = random.choice([1, 1, 1, 0])  # 75% chance of availability
            
            schedule, created = TransportSchedule.objects.get_or_create(
                transport_type='car',
                transport_id=car.id,
                travel_date=schedule_date,
                defaults={
                    'total_seats': car.seats,
                    'available_seats': available_seats,
                    'price': schedule_price,
                    'is_active': True
                }
            )
            
            if created:
                car_schedule_count += 1
    
    print(f"Created {car_schedule_count} car schedules")
    
    total_schedules = flight_schedule_count + bus_schedule_count + car_schedule_count
    print(f"TOTAL: Created {total_schedules} transport schedules")
    return total_schedules

def populate_all_transport_data():
    """Main function to populate ALL transport data for Myanmar"""
    print("=" * 60)
    print("POPULATING COMPLETE TRANSPORT DATABASE FOR MYANMAR")
    print("=" * 60)
    
    # Get all destinations
    destinations = Destination.objects.filter(is_active=True)
    print(f"Found {destinations.count()} destinations")
    
    # Create airlines if they don't exist
    airlines_data = [
        {'name': 'Air KBZ', 'code': 'K7', 'is_default_for_domestic': True},
        {'name': 'Myanmar National Airlines', 'code': 'UB', 'is_default_for_domestic': True},
        {'name': 'Golden Myanmar Airlines', 'code': 'Y5', 'is_default_for_domestic': False},
        {'name': 'Mann Yadanarpon Airlines', 'code': '7Y', 'is_default_for_domestic': False},
        {'name': 'Air Thanlwin', 'code': '9A', 'is_default_for_domestic': False},
    ]
    
    airlines = {}
    for airline_data in airlines_data:
        airline, created = Airline.objects.get_or_create(
            code=airline_data['code'],
            defaults=airline_data
        )
        airlines[airline.code] = airline
        print(f"{'Created' if created else 'Found'} airline: {airline.name}")
    
    # ========== POPULATE FLIGHTS ==========
    print("\n" + "=" * 60)
    print("POPULATING FLIGHTS")
    print("=" * 60)
    
    # Major airports in Myanmar
    airports = [
        'Yangon', 'Mandalay', 'Naypyidaw', 'Bagan', 'Heho', 'Thandwe',
        'Sittwe', 'Myitkyina', 'Tachileik', 'Kawthaung', 'Dawei', 'Myeik'
    ]
    
    airport_destinations = {}
    for airport_name in airports:
        try:
            dest = Destination.objects.get(name__icontains=airport_name)
            airport_destinations[airport_name] = dest
        except Destination.DoesNotExist:
            print(f"Warning: Airport destination '{airport_name}' not found")
            continue
    
    print(f"Found {len(airport_destinations)} airport destinations")
    
    # Create flights between all airport pairs
    flight_count = 0
    airport_list = list(airport_destinations.values())
    
    for i, departure in enumerate(airport_list):
        for j, arrival in enumerate(airport_list):
            if departure != arrival:
                # Create 1-3 flights per route
                for flight_num in range(1, random.randint(2, 4)):
                    airline = random.choice(list(airlines.values()))
                    
                    # Generate flight times
                    departure_hour = random.choice([6, 8, 10, 12, 14, 16, 18])
                    departure_time_obj = time(departure_hour, random.choice([0, 15, 30, 45]))
                    
                    # Flight duration based on distance (estimated)
                    duration_hours = random.randint(1, 3)
                    arrival_hour = (departure_hour + duration_hours) % 24
                    arrival_time_obj = time(arrival_hour, random.choice([0, 15, 30, 45]))
                    
                    # Price based on distance and class
                    base_price = random.randint(50000, 300000)
                    
                    flight_class = random.choice(['low', 'medium', 'high'])
                    if flight_class == 'low':
                        price = Decimal(str(base_price * 0.8))
                        total_seats = random.randint(150, 200)
                    elif flight_class == 'medium':
                        price = Decimal(str(base_price))
                        total_seats = random.randint(120, 180)
                    else:  # high
                        price = Decimal(str(base_price * 1.5))
                        total_seats = random.randint(80, 120)
                    
                    available_seats = int(total_seats * random.uniform(0.6, 0.9))
                    
                    flight_number = f"{airline.code} {random.randint(100, 999)}"
                    
                    flight, created = Flight.objects.get_or_create(
                        airline=airline,
                        flight_number=flight_number,
                        departure=departure,
                        arrival=arrival,
                        defaults={
                            'departure_time': departure_time_obj,
                            'arrival_time': arrival_time_obj,
                            'duration': timedelta(hours=duration_hours, minutes=random.randint(0, 45)),
                            'price': price,
                            'category': flight_class,
                            'total_seats': total_seats,
                            'available_seats': available_seats,
                            'description': f"Flight from {departure.name} to {arrival.name} operated by {airline.name}",
                            'is_active': True
                        }
                    )
                    
                    if created:
                        flight_count += 1
                        print(f"Created flight: {airline.name} {flight_number} - {departure.name} → {arrival.name}")
    
    print(f"Created {flight_count} flights total")
    
    # ========== POPULATE BUS SERVICES ==========
    print("\n" + "=" * 60)
    print("POPULATING BUS SERVICES")
    print("=" * 60)
    
    bus_companies = ['JJ Express', 'Elite Express', 'Shwe Mandalar', 'Lumbini Bus', 
                    'Mandalar Express', 'Asia Express', 'Shwe Pyi', 'Aung Gabar']
    
    # Major bus routes in Myanmar
    major_routes = [
        ('Yangon', 'Mandalay'),
        ('Yangon', 'Bagan'),
        ('Yangon', 'Naypyidaw'),
        ('Mandalay', 'Bagan'),
        ('Mandalay', 'Naypyidaw'),
        ('Yangon', 'Taunggyi'),
        ('Mandalay', 'Taunggyi'),
        ('Yangon', 'Hpa-An'),
        ('Yangon', 'Mawlamyine'),
        ('Mandalay', 'Monywa'),
    ]
    
    bus_count = 0
    for route in major_routes:
        from_city_name, to_city_name = route
        
        try:
            departure = Destination.objects.get(name__icontains=from_city_name)
            arrival = Destination.objects.get(name__icontains=to_city_name)
        except Destination.DoesNotExist:
            continue
        
        # Create 2-3 bus services per route
        for bus_num in range(1, random.randint(2, 4)):
            company = random.choice(bus_companies)
            
            # Bus types and corresponding prices
            bus_types = ['standard', 'vip', 'luxury']
            bus_type = random.choice(bus_types)
            
            if bus_type == 'standard':
                price = Decimal(str(random.randint(15000, 25000)))
                total_seats = random.randint(40, 50)
            elif bus_type == 'vip':
                price = Decimal(str(random.randint(25000, 40000)))
                total_seats = random.randint(30, 40)
            else:  # luxury
                price = Decimal(str(random.randint(40000, 60000)))
                total_seats = random.randint(20, 30)
            
            available_seats = int(total_seats * random.uniform(0.5, 0.8))
            
            # Departure time (evening buses for overnight journeys)
            departure_hour = random.choice([18, 19, 20, 21, 22])
            departure_time_obj = time(departure_hour, random.choice([0, 15, 30, 45]))
            
            # Duration (7-12 hours for most routes)
            duration_hours = random.randint(7, 12)
            
            bus, created = BusService.objects.get_or_create(
                company=company,
                departure=departure,
                arrival=arrival,
                bus_type=bus_type,
                defaults={
                    'departure_time': departure_time_obj,
                    'duration': timedelta(hours=duration_hours),
                    'price': price,
                    'total_seats': total_seats,
                    'available_seats': available_seats,
                    'bus_number': f"BUS{random.randint(1000, 9999)}",
                    'description': f"{bus_type.upper()} bus service from {departure.name} to {arrival.name}",
                    'is_active': True
                }
            )
            
            if created:
                bus_count += 1
                print(f"Created bus: {company} - {departure.name} → {arrival.name} ({bus_type})")
    
    print(f"Created {bus_count} bus services")
    
    # ========== POPULATE CAR RENTALS ==========
    print("\n" + "=" * 60)
    print("POPULATING CAR RENTALS")
    print("=" * 60)
    
    car_companies = ['City Car Rental', 'Premium Rentals', 'Luxury Wheels', 
                    'Myanmar Rent-a-Car', 'Avis Myanmar', 'Hertz Myanmar', 
                    'Local Car Hire', 'Express Rentals']
    
    car_models = [
        {'model': 'Toyota Vios', 'type': 'economy', 'seats': 4, 'base_price': 35000},
        {'model': 'Toyota Corolla', 'type': 'economy', 'seats': 5, 'base_price': 40000},
        {'model': 'Honda City', 'type': 'economy', 'seats': 5, 'base_price': 38000},
        {'model': 'Toyota Fortuner', 'type': 'suv', 'seats': 7, 'base_price': 70000},
        {'model': 'Mitsubishi Pajero', 'type': 'suv', 'seats': 7, 'base_price': 75000},
        {'model': 'Suzuki Ertiga', 'type': 'suv', 'seats': 7, 'base_price': 55000},
        {'model': 'Mercedes E-Class', 'type': 'luxury', 'seats': 5, 'base_price': 150000},
        {'model': 'BMW 5 Series', 'type': 'luxury', 'seats': 5, 'base_price': 160000},
        {'model': 'Toyota Hiace', 'type': 'van', 'seats': 12, 'base_price': 90000},
    ]
    
    # Major cities for car rentals
    car_cities = ['Yangon', 'Mandalay', 'Naypyidaw', 'Bagan', 'Taunggyi', 'Mawlamyine']
    
    car_count = 0
    for city_name in car_cities:
        try:
            location = Destination.objects.get(name__icontains=city_name)
        except Destination.DoesNotExist:
            continue
        
        # Create 3-5 car rentals per city
        for rental_num in range(random.randint(3, 6)):
            company = random.choice(car_companies)
            car_model_data = random.choice(car_models)
            
            # Price variation
            price_variation = random.uniform(0.8, 1.2)
            price_per_day = Decimal(str(int(car_model_data['base_price'] * price_variation)))
            
            # Features based on car type
            base_features = ['AC']
            if car_model_data['type'] == 'economy':
                features = base_features + ['Manual', 'Radio']
            elif car_model_data['type'] == 'suv':
                features = base_features + ['Automatic', 'GPS', 'Bluetooth']
            elif car_model_data['type'] == 'luxury':
                features = base_features + ['Automatic', 'GPS', 'Leather Seats', 'Sunroof', 'Premium Sound']
            else:  # van
                features = base_features + ['Manual', 'Spacious']
            
            transmission = 'Automatic' if 'Automatic' in features else 'Manual'
            
            car, created = CarRental.objects.get_or_create(
                company=company,
                car_model=car_model_data['model'],
                location=location,
                defaults={
                    'car_type': car_model_data['type'],
                    'seats': car_model_data['seats'],
                    'price_per_day': price_per_day,
                    'features': features,
                    'is_available': True,
                    'transmission': transmission,
                    'fuel_type': random.choice(['Petrol', 'Diesel']),
                    'year': random.randint(2018, 2023),
                    'description': f"{car_model_data['type'].title()} car rental in {location.name}",
                }
            )
            
            if created:
                car_count += 1
                print(f"Created car: {company} - {car_model_data['model']} in {location.name}")
    
    print(f"Created {car_count} car rentals")
    
    # ========== CREATE SCHEDULES ==========
    print("\n" + "=" * 60)
    print("CREATING TRANSPORT SCHEDULES")
    print("=" * 60)
    
    schedule_count = create_transport_schedules()
    
    # ========== SUMMARY ==========
    print("\n" + "=" * 60)
    print("POPULATION COMPLETE - SUMMARY")
    print("=" * 60)
    print(f"Flights created: {Flight.objects.count()}")
    print(f"Bus services created: {BusService.objects.count()}")
    print(f"Car rentals created: {CarRental.objects.count()}")
    print(f"Transport schedules created: {TransportSchedule.objects.count()}")
    print(f"Total transport options: {Flight.objects.count() + BusService.objects.count() + CarRental.objects.count()}")
    print("=" * 60)
    print("Transport data population completed successfully!")
    
    return {
        'flights': Flight.objects.count(),
        'buses': BusService.objects.count(),
        'cars': CarRental.objects.count(),
        'schedules': TransportSchedule.objects.count()
    }

if __name__ == '__main__':
    populate_all_transport_data()