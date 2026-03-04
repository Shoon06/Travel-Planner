# Save as: C:\Users\ASUS\MyanmarTravelPlanner\populate_complete_transport_network.py
import os
import django
import random
from datetime import datetime, timedelta, time
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models import Destination, Flight, BusService, CarRental, TransportSchedule, Airline

def create_complete_transport_network():
    """Create transport connections between ALL 37 destinations"""
    print("=" * 70)
    print("CREATING COMPLETE TRANSPORT NETWORK FOR 37 DESTINATIONS")
    print("=" * 70)
    
    # Get all 37 destinations
    destinations = Destination.objects.filter(is_active=True).order_by('name')
    print(f"Found {destinations.count()} destinations")
    
    # Create airlines if needed
    airlines_data = [
        {'name': 'Air KBZ', 'code': 'K7', 'is_default_for_domestic': True},
        {'name': 'Myanmar National Airlines', 'code': 'UB', 'is_default_for_domestic': True},
    ]
    
    airlines = {}
    for airline_data in airlines_data:
        airline, created = Airline.objects.get_or_create(
            code=airline_data['code'],
            defaults=airline_data
        )
        airlines[airline.code] = airline
    
    # ========== 1. CREATE FLIGHTS BETWEEN AIRPORT DESTINATIONS ==========
    print("\n1. Creating flights between airport destinations...")
    
    airport_cities = [
        'Yangon', 'Mandalay', 'Naypyidaw', 'Bagan', 'Heho', 'Thandwe',
        'Sittwe', 'Myitkyina', 'Tachileik', 'Kawthaung', 'Dawei', 'Myeik',
        'Mawlamyine', 'Pathein', 'Loikaw', 'Hakha', 'Kengtung'
    ]
    
    airport_destinations = []
    for city in airport_cities:
        dest = destinations.filter(name__icontains=city).first()
        if dest:
            airport_destinations.append(dest)
    
    print(f"Found {len(airport_destinations)} airport destinations")
    
    flight_count = 0
    for i, departure in enumerate(airport_destinations):
        for j, arrival in enumerate(airport_destinations):
            if departure != arrival:
                # Create 1-2 flights per route
                for flight_num in range(1, 3):
                    airline = random.choice(list(airlines.values()))
                    
                    # Flight times
                    departure_hour = random.choice([6, 9, 12, 15, 18])
                    departure_time_obj = time(departure_hour, random.choice([0, 30]))
                    
                    duration_hours = random.randint(1, 3)
                    arrival_hour = (departure_hour + duration_hours) % 24
                    arrival_time_obj = time(arrival_hour, random.choice([0, 30]))
                    
                    # Price: 50,000 - 300,000 MMK
                    price = Decimal(str(random.randint(50000, 300000)))
                    
                    flight_number = f"{airline.code}{random.randint(100, 999)}"
                    
                    flight, created = Flight.objects.get_or_create(
                        airline=airline,
                        flight_number=flight_number,
                        departure=departure,
                        arrival=arrival,
                        defaults={
                            'departure_time': departure_time_obj,
                            'arrival_time': arrival_time_obj,
                            'duration': timedelta(hours=duration_hours),
                            'price': price,
                            'category': random.choice(['low', 'medium', 'high']),
                            'total_seats': random.randint(100, 200),
                            'available_seats': random.randint(50, 180),
                            'description': f"Domestic flight from {departure.name} to {arrival.name}",
                            'is_active': True
                        }
                    )
                    
                    if created:
                        flight_count += 1
    
    print(f"Created {flight_count} flights")
    
    # ========== 2. CREATE BUS SERVICES BETWEEN ALL DESTINATIONS ==========
    print("\n2. Creating bus services between ALL destinations...")
    
    bus_companies = ['JJ Express', 'Elite Express', 'Shwe Mandalar', 'Mandalar Express', 'Lumbini Bus']
    
    bus_count = 0
    created_routes = set()  # Track created routes
    
    for i, departure in enumerate(destinations):
        for j, arrival in enumerate(destinations):
            if departure != arrival:
                route_key = f"{departure.id}-{arrival.id}"
                
                if route_key not in created_routes:
                    # Create 1-2 bus services per route
                    for bus_num in range(1, random.randint(2, 3)):
                        company = random.choice(bus_companies)
                        
                        # Bus type and price
                        bus_type = random.choice(['standard', 'vip', 'luxury'])
                        if bus_type == 'standard':
                            price = Decimal(str(random.randint(10000, 25000)))
                            total_seats = random.randint(40, 50)
                        elif bus_type == 'vip':
                            price = Decimal(str(random.randint(25000, 40000)))
                            total_seats = random.randint(30, 40)
                        else:
                            price = Decimal(str(random.randint(40000, 60000)))
                            total_seats = random.randint(20, 30)
                        
                        # Evening departure for overnight journeys
                        departure_hour = random.choice([18, 19, 20, 21])
                        departure_time_obj = time(departure_hour, random.choice([0, 15, 30, 45]))
                        
                        # Duration: 4-15 hours based on distance
                        duration_hours = random.randint(4, 15)
                        
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
                                'available_seats': random.randint(int(total_seats * 0.5), int(total_seats * 0.9)),
                                'bus_number': f"BUS{random.randint(1000, 9999)}",
                                'description': f"{bus_type.upper()} bus from {departure.name} to {arrival.name}",
                                'is_active': True
                            }
                        )
                        
                        if created:
                            bus_count += 1
                            created_routes.add(route_key)
    
    print(f"Created {bus_count} bus services")
    
    # ========== 3. CREATE CAR RENTALS IN ALL DESTINATIONS ==========
    print("\n3. Creating car rentals in all destinations...")
    
    car_companies = ['City Car Rental', 'Premium Rentals', 'Myanmar Rent-a-Car', 'Local Car Hire']
    car_models = [
        {'model': 'Toyota Vios', 'type': 'economy', 'seats': 4, 'base_price': 30000},
        {'model': 'Toyota Fortuner', 'type': 'suv', 'seats': 7, 'base_price': 70000},
        {'model': 'Suzuki Ertiga', 'type': 'suv', 'seats': 7, 'base_price': 55000},
        {'model': 'Honda City', 'type': 'economy', 'seats': 5, 'base_price': 35000},
    ]
    
    car_count = 0
    for destination in destinations:
        # Create 2-4 car rentals per destination
        for rental_num in range(random.randint(2, 5)):
            company = random.choice(car_companies)
            car_model_data = random.choice(car_models)
            
            price_per_day = Decimal(str(int(car_model_data['base_price'] * random.uniform(0.8, 1.2))))
            
            features = ['AC']
            if car_model_data['type'] == 'economy':
                features += ['Manual', 'Radio']
            else:  # suv
                features += ['Automatic', 'GPS']
            
            car, created = CarRental.objects.get_or_create(
                company=company,
                car_model=car_model_data['model'],
                location=destination,
                defaults={
                    'car_type': car_model_data['type'],
                    'seats': car_model_data['seats'],
                    'price_per_day': price_per_day,
                    'features': features,
                    'is_available': True,
                    'transmission': 'Automatic' if 'Automatic' in features else 'Manual',
                    'fuel_type': random.choice(['Petrol', 'Diesel']),
                    'description': f"{car_model_data['type'].title()} car rental in {destination.name}",
                }
            )
            
            if created:
                car_count += 1
    
    print(f"Created {car_count} car rentals")
    
    # ========== 4. CREATE SCHEDULES FOR NEXT 60 DAYS ==========
    print("\n4. Creating schedules for next 60 days...")
    
    today = datetime.now().date()
    schedule_dates = [today + timedelta(days=i) for i in range(60)]
    
    # Create schedules for flights
    flight_schedule_count = 0
    flights = Flight.objects.filter(is_active=True)
    for flight in flights:
        for schedule_date in schedule_dates:
            # Skip some flights on weekends (fewer flights)
            if schedule_date.weekday() >= 5 and random.random() > 0.3:
                continue
            
            # Price variation: +20% on weekends
            is_weekend = schedule_date.weekday() >= 5
            price_multiplier = 1.2 if is_weekend else 1.0
            schedule_price = Decimal(str(float(flight.price) * price_multiplier))
            
            # Availability: 60-90% of seats available
            available_seats = random.randint(
                int(flight.total_seats * 0.6),
                int(flight.total_seats * 0.9)
            )
            
            schedule, created = TransportSchedule.objects.get_or_create(
                transport_type='flight',
                transport_id=flight.id,
                travel_date=schedule_date,
                defaults={
                    'departure_time': flight.departure_time,
                    'arrival_time': flight.arrival_time,
                    'total_seats': flight.total_seats,
                    'available_seats': available_seats,
                    'price': schedule_price,
                    'is_active': True
                }
            )
            
            if created:
                flight_schedule_count += 1
    
    print(f"Created {flight_schedule_count} flight schedules")
    
    # Create schedules for buses
    bus_schedule_count = 0
    buses = BusService.objects.filter(is_active=True)
    for bus in buses:
        for schedule_date in schedule_dates:
            # More buses on weekends
            is_weekend = schedule_date.weekday() >= 5
            price_multiplier = 1.15 if is_weekend else 1.0
            schedule_price = Decimal(str(float(bus.price) * price_multiplier))
            
            available_seats = random.randint(
                int(bus.total_seats * 0.4),
                int(bus.total_seats * 0.8)
            )
            
            schedule, created = TransportSchedule.objects.get_or_create(
                transport_type='bus',
                transport_id=bus.id,
                travel_date=schedule_date,
                defaults={
                    'departure_time': bus.departure_time,
                    'total_seats': bus.total_seats,
                    'available_seats': available_seats,
                    'price': schedule_price,
                    'is_active': True
                }
            )
            
            if created:
                bus_schedule_count += 1
    
    print(f"Created {bus_schedule_count} bus schedules")
    
    # Create schedules for cars
    car_schedule_count = 0
    cars = CarRental.objects.filter(is_available=True)
    for car in cars:
        for schedule_date in schedule_dates:
            # Cars are less available on weekends
            is_weekend = schedule_date.weekday() >= 5
            price_multiplier = 1.25 if is_weekend else 1.0
            schedule_price = Decimal(str(float(car.price_per_day) * price_multiplier))
            
            # 80% chance of availability on weekdays, 50% on weekends
            if is_weekend:
                available_seats = random.choice([0, car.seats, 0])
            else:
                available_seats = random.choice([car.seats, car.seats, car.seats, 0])
            
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
    
    # ========== 5. SUMMARY ==========
    print("\n" + "=" * 70)
    print("TRANSPORT NETWORK CREATION COMPLETE")
    print("=" * 70)
    print(f"Total Flights: {Flight.objects.count()}")
    print(f"Total Bus Services: {BusService.objects.count()}")
    print(f"Total Car Rentals: {CarRental.objects.count()}")
    print(f"Total Transport Schedules: {TransportSchedule.objects.count()}")
    print(f"Transport connections created for {destinations.count()} destinations")
    print("=" * 70)
    
    return {
        'flights': Flight.objects.count(),
        'buses': BusService.objects.count(),
        'cars': CarRental.objects.count(),
        'schedules': TransportSchedule.objects.count(),
        'destinations': destinations.count()
    }

if __name__ == '__main__':
    create_complete_transport_network()