from django.core.management.base import BaseCommand
from planner.models import Destination, Hotel, Flight, BusService, CarRental, Airline, TransportSchedule
from decimal import Decimal
from datetime import time, timedelta, datetime
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate database with sample data for Myanmar Travel Planner'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting comprehensive data population...')
        
        # Create destinations
        self.populate_destinations()
        
        # Populate hotels
        self.populate_hotels()
        
        # Populate COMPREHENSIVE transport data
        self.populate_comprehensive_transport()
        
        # Create transport schedules
        self.create_transport_schedules()
        
        self.stdout.write(self.style.SUCCESS('All data populated successfully!'))
    
    def populate_destinations(self):
        """Populate destination data"""
        self.stdout.write('Populating destinations...')
        
        destinations_data = [
            # States
            {"name": "Kachin", "region": "Northern Myanmar", "type": "state", 
             "description": "Northernmost state known for jade mines and Hkakabo Razi mountain."},
            {"name": "Kayah", "region": "Eastern Myanmar", "type": "state",
             "description": "Eastern state known for traditional long-necked women and scenic mountains."},
            {"name": "Kayin", "region": "Southeastern Myanmar", "type": "state",
             "description": "State bordering Thailand known for waterfalls and Karen culture."},
            {"name": "Chin", "region": "Western Myanmar", "type": "state",
             "description": "Western state with mountainous terrain and unique tribal cultures."},
            {"name": "Mon", "region": "Southern Myanmar", "type": "state",
             "description": "Southern state with ancient Mon civilization and beaches."},
            {"name": "Rakhine", "region": "Western Myanmar", "type": "state",
             "description": "Western coastal state with Ngapali Beach and ancient Mrauk U."},
            {"name": "Shan", "region": "Eastern Myanmar", "type": "state",
             "description": "Largest state known for Inle Lake, hill tribes, and tea plantations."},
            
            # Regions
            {"name": "Yangon", "region": "Lower Myanmar", "type": "region",
             "description": "Former capital and largest city, known for Shwedagon Pagoda.",
             "latitude": 16.8409, "longitude": 96.1735},
            {"name": "Mandalay", "region": "Central Myanmar", "type": "region",
             "description": "Cultural capital and last royal capital of Myanmar.",
             "latitude": 21.9588, "longitude": 96.0891},
            {"name": "Bago", "region": "Lower Myanmar", "type": "region",
             "description": "Ancient capital with many pagodas and monasteries.",
             "latitude": 17.3375, "longitude": 96.4819},
            {"name": "Magway", "region": "Central Myanmar", "type": "region",
             "description": "Central region known for oil fields and Thanboddhay Pagoda.",
             "latitude": 20.1496, "longitude": 94.9320},
            {"name": "Sagaing", "region": "Northern Myanmar", "type": "region",
             "description": "Region with many monasteries and religious sites.",
             "latitude": 21.8831, "longitude": 95.9782},
            {"name": "Tanintharyi", "region": "Southern Myanmar", "type": "region",
             "description": "Southernmost region with beautiful islands and beaches.",
             "latitude": 12.4560, "longitude": 99.0214},
            {"name": "Ayeyarwady", "region": "Lower Myanmar", "type": "region",
             "description": "Delta region with riverine landscapes and fishing villages.",
             "latitude": 16.8349, "longitude": 94.3647},
            {"name": "Naypyidaw", "region": "Central Myanmar", "type": "union_territory",
             "description": "Capital city of Myanmar since 2005.",
             "latitude": 19.7460, "longitude": 96.1270},
            
            # Popular Cities/Towns with AIRPORTS
            {"name": "Bagan", "region": "Mandalay Region", "type": "city",
             "description": "Ancient city with over 2,000 Buddhist temples and pagodas.",
             "latitude": 21.1722, "longitude": 94.8603},
            {"name": "Inle Lake", "region": "Shan State", "type": "attraction",
             "description": "Freshwater lake known for floating villages and leg-rowing fishermen.",
             "latitude": 20.5550, "longitude": 96.9150},
            {"name": "Ngapali Beach", "region": "Rakhine State", "type": "attraction",
             "description": "Pristine beach with white sand and clear water.",
             "latitude": 18.4159, "longitude": 94.2977},
            {"name": "Ngwe Saung Beach", "region": "Ayeyarwady Region", "type": "attraction",
             "description": "Beautiful beach resort area near Yangon.",
             "latitude": 16.8533, "longitude": 94.3589},
            {"name": "Pyin Oo Lwin", "region": "Mandalay Region", "type": "town",
             "description": "Hill station known for colonial architecture and botanical gardens.",
             "latitude": 22.0339, "longitude": 96.4561},
            {"name": "Hsipaw", "region": "Shan State", "type": "town",
             "description": "Gateway to Shan State's hill tribe areas and trekking routes.",
             "latitude": 22.6286, "longitude": 97.3375},
            {"name": "Kalaw", "region": "Shan State", "type": "town",
             "description": "Hill station popular for trekking to Inle Lake.",
             "latitude": 20.6260, "longitude": 96.5623},
            {"name": "Mawlamyine", "region": "Mon State", "type": "city",
             "description": "Third largest city, former British colonial capital.",
             "latitude": 16.4802, "longitude": 97.6212},
            {"name": "Hpa-An", "region": "Kayin State", "type": "town",
             "description": "Capital of Kayin State with dramatic limestone mountains.",
             "latitude": 16.8894, "longitude": 97.6343},
            {"name": "Dawei", "region": "Tanintharyi Region", "type": "city",
             "description": "Southern city with beautiful beaches and islands.",
             "latitude": 14.0833, "longitude": 98.1944},
            {"name": "Myeik", "region": "Tanintharyi Region", "type": "city",
             "description": "Coastal city known for the Myeik Archipelago.",
             "latitude": 12.4377, "longitude": 98.6007},
            {"name": "Monywa", "region": "Sagaing Region", "type": "city",
             "description": "City known for Thanboddhay Pagoda and Bodhi Tataung.",
             "latitude": 22.1167, "longitude": 95.1333},
            {"name": "Taunggyi", "region": "Shan State", "type": "city",
             "description": "Capital of Shan State and famous for hot air balloon festival.",
             "latitude": 20.7853, "longitude": 97.0374},
            {"name": "Loikaw", "region": "Kayah State", "type": "city",
             "description": "Capital of Kayah State with traditional cultures.",
             "latitude": 19.6742, "longitude": 97.2094},
            {"name": "Hakha", "region": "Chin State", "type": "city",
             "description": "Capital of Chin State with cool climate and mountain views.",
             "latitude": 22.6455, "longitude": 93.6103},
            {"name": "Sittwe", "region": "Rakhine State", "type": "city",
             "description": "Capital of Rakhine State with colonial architecture.",
             "latitude": 20.1400, "longitude": 92.8997},
            {"name": "Pathein", "region": "Ayeyarwady Region", "type": "city",
             "description": "Capital of Ayeyarwady Region known for umbrella making.",
             "latitude": 16.7770, "longitude": 94.7279},
            
            # ADDITIONAL IMPORTANT CITIES WITH AIRPORTS
            {"name": "Heho", "region": "Shan State", "type": "town",
             "description": "Gateway airport for Inle Lake and surrounding areas.",
             "latitude": 20.7431, "longitude": 96.7919},
            {"name": "Thandwe", "region": "Rakhine State", "type": "town",
             "description": "Airport serving Ngapali Beach area.",
             "latitude": 18.4608, "longitude": 94.2997},
            {"name": "Myitkyina", "region": "Kachin State", "type": "city",
             "description": "Capital of Kachin State in northern Myanmar.",
             "latitude": 25.3833, "longitude": 97.4000},
            {"name": "Tachileik", "region": "Shan State", "type": "city",
             "description": "Border town near Thailand in eastern Myanmar.",
             "latitude": 20.4481, "longitude": 99.8808},
            {"name": "Kawthaung", "region": "Tanintharyi Region", "type": "city",
             "description": "Southernmost city bordering Thailand.",
             "latitude": 9.9825, "longitude": 98.5503},
        ]
        
        for data in destinations_data:
            dest, created = Destination.objects.get_or_create(
                name=data["name"],
                defaults=data
            )
            if created:
                self.stdout.write(f"Created destination: {dest.name}")
        
        self.stdout.write(self.style.SUCCESS(f'Destinations populated: {Destination.objects.count()} destinations'))
    
    def populate_hotels(self):
        """Populate hotel data"""
        self.stdout.write('Populating hotels...')
        
        # Get destinations
        yangon = Destination.objects.get(name="Yangon")
        mandalay = Destination.objects.get(name="Mandalay")
        bagan = Destination.objects.get(name="Bagan")
        inle_lake = Destination.objects.get(name="Inle Lake")
        naypyidaw = Destination.objects.get(name="Naypyidaw")
        ngapali = Destination.objects.get(name="Ngapali Beach")
        pyin_oo_lwin = Destination.objects.get(name="Pyin Oo Lwin")
        
        HOTELS = [
            # Yangon Hotels
            {
                "name": "Sule Shangri-La",
                "destination": yangon,
                "address": "223 Sule Pagoda Road, Yangon 11182",
                "price_per_night": Decimal("180.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "restaurant", "gym", "bar"],
                "rating": Decimal("4.8"),
                "review_count": 1243,
                "latitude": 16.7785, "longitude": 96.1592
            },
            {
                "name": "Pan Pacific Yangon",
                "destination": yangon,
                "address": "Pyay Road, Yangon",
                "price_per_night": Decimal("150.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "restaurant", "gym", "spa"],
                "rating": Decimal("4.7"),
                "review_count": 892,
                "latitude": 16.8047, "longitude": 96.1353
            },
            {
                "name": "Hotel Grand United (21st Downtown)",
                "destination": yangon,
                "address": "21st Street, Downtown Yangon",
                "price_per_night": Decimal("50.00"),
                "category": "budget",
                "amenities": ["wifi", "restaurant", "airport shuttle"],
                "rating": Decimal("4.2"),
                "review_count": 567,
                "latitude": 16.7801, "longitude": 96.1603
            },
            
            # Mandalay Hotels
            {
                "name": "Royal Mandalay Hotel",
                "destination": mandalay,
                "address": "Mandalay City, Mandalay Region",
                "price_per_night": Decimal("95.00"),
                "category": "medium",
                "amenities": ["wifi", "pool", "restaurant", "garden"],
                "rating": Decimal("4.7"),
                "review_count": 1056,
                "latitude": 21.9811, "longitude": 96.0839
            },
            {
                "name": "Mandalay Hill Resort",
                "destination": mandalay,
                "address": "Near Mandalay Hill, Mandalay",
                "price_per_night": Decimal("120.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "restaurant", "hill view"],
                "rating": Decimal("4.6"),
                "review_count": 789,
                "latitude": 21.9542, "longitude": 96.1125
            },
            
            # Bagan Hotels
            {
                "name": "Bagan Lodge",
                "destination": bagan,
                "address": "Old Bagan, Bagan Archaeological Zone",
                "price_per_night": Decimal("120.00"),
                "category": "medium",
                "amenities": ["wifi", "pool", "restaurant", "garden", "bicycle rental"],
                "rating": Decimal("4.6"),
                "review_count": 892,
                "latitude": 21.1692, "longitude": 94.8594
            },
            {
                "name": "Aureum Palace Hotel & Resort Bagan",
                "destination": bagan,
                "address": "Bagan-Nyaung U Road, Bagan",
                "price_per_night": Decimal("200.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "golf", "restaurant", "pagoda view"],
                "rating": Decimal("4.8"),
                "review_count": 745,
                "latitude": 21.1558, "longitude": 94.8747
            },
            
            # Inle Lake Hotels
            {
                "name": "Novotel Inle Lake Myat Min",
                "destination": inle_lake,
                "address": "Maing Thauk Village, Inle Lake",
                "price_per_night": Decimal("140.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "lake view", "restaurant"],
                "rating": Decimal("4.7"),
                "review_count": 678,
                "latitude": 20.5601, "longitude": 96.9102
            },
            {
                "name": "Golden Island Cottages",
                "destination": inle_lake,
                "address": "Nyaung Shwe, Inle Lake",
                "price_per_night": Decimal("80.00"),
                "category": "medium",
                "amenities": ["wifi", "lake view", "restaurant", "boat service"],
                "rating": Decimal("4.5"),
                "review_count": 543,
                "latitude": 20.5512, "longitude": 96.9087
            },
            
            # Naypyidaw Hotels
            {
                "name": "Kempinski Hotel Naypyidaw",
                "destination": naypyidaw,
                "address": "Ottarathiri Township, Naypyidaw",
                "price_per_night": Decimal("160.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "golf", "restaurant", "conference"],
                "rating": Decimal("4.7"),
                "review_count": 432,
                "latitude": 19.7481, "longitude": 96.1158
            },
            
            # Ngapali Beach Hotels
            {
                "name": "Amata Resort & Spa",
                "destination": ngapali,
                "address": "Ngapali Beach, Rakhine State",
                "price_per_night": Decimal("130.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "beachfront", "restaurant"],
                "rating": Decimal("4.6"),
                "review_count": 389,
                "latitude": 18.4189, "longitude": 94.3012
            },
            
            # Pyin Oo Lwin Hotels
            {
                "name": "Kandawgyi Hill Resort",
                "destination": pyin_oo_lwin,
                "address": "Pyin Oo Lwin, Mandalay Region",
                "price_per_night": Decimal("75.00"),
                "category": "medium",
                "amenities": ["wifi", "garden", "restaurant", "mountain view"],
                "rating": Decimal("4.4"),
                "review_count": 267,
                "latitude": 22.0289, "longitude": 96.4583
            },
        ]
        
        for hotel_data in HOTELS:
            hotel, created = Hotel.objects.get_or_create(
                name=hotel_data["name"],
                destination=hotel_data["destination"],
                defaults={
                    "address": hotel_data["address"],
                    "price_per_night": hotel_data["price_per_night"],
                    "category": hotel_data["category"],
                    "amenities": hotel_data["amenities"],
                    "rating": hotel_data["rating"],
                    "review_count": hotel_data["review_count"],
                    "latitude": hotel_data.get("latitude"),
                    "longitude": hotel_data.get("longitude"),
                    "is_active": True
                }
            )
            if created:
                self.stdout.write(f"Created hotel: {hotel.name} in {hotel.destination.name}")
        
        self.stdout.write(self.style.SUCCESS(f'Hotels populated: {Hotel.objects.count()} hotels'))
    
    def populate_comprehensive_transport(self):
        """Populate COMPREHENSIVE transport data for ALL destinations"""
        self.stdout.write('=' * 60)
        self.stdout.write('POPULATING COMPREHENSIVE TRANSPORT DATA')
        self.stdout.write('=' * 60)
        
        # Create airlines
        airlines_data = [
            {'name': 'Air KBZ', 'code': 'K7', 'is_default_for_domestic': True},
            {'name': 'Myanmar National Airlines', 'code': 'UB', 'is_default_for_domestic': True},
            {'name': 'Golden Myanmar Airlines', 'code': 'Y5', 'is_default_for_domestic': False},
            {'name': 'Mann Yadanarpon Airlines', 'code': '7Y', 'is_default_for_domestic': False},
        ]
        
        airlines = {}
        for airline_data in airlines_data:
            airline, created = Airline.objects.get_or_create(
                code=airline_data['code'],
                defaults=airline_data
            )
            airlines[airline.code] = airline
            self.stdout.write(f"{'Created' if created else 'Found'} airline: {airline.name}")
        
        # Get major destinations with airports
        airport_destinations = [
            'Yangon', 'Mandalay', 'Naypyidaw', 'Bagan', 'Heho', 'Thandwe',
            'Sittwe', 'Myitkyina', 'Tachileik', 'Kawthaung', 'Dawei', 'Myeik'
        ]
        
        destinations_map = {}
        for dest_name in airport_destinations:
            try:
                dest = Destination.objects.get(name__icontains=dest_name)
                destinations_map[dest_name] = dest
            except Destination.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Destination '{dest_name}' not found, skipping..."))
                continue
        
        self.stdout.write(f"Found {len(destinations_map)} airport destinations")
        
        # ========== POPULATE FLIGHTS BETWEEN ALL AIRPORT CITIES ==========
        self.stdout.write('\nCreating flights between all airport cities...')
        flight_count = 0
        dest_list = list(destinations_map.values())
        
        for i, departure in enumerate(dest_list):
            for j, arrival in enumerate(dest_list):
                if departure != arrival:
                    # Create 1-2 flights per route
                    for flight_num in range(1, random.randint(2, 3)):
                        airline = random.choice(list(airlines.values()))
                        
                        # Generate flight times
                        departure_hour = random.choice([6, 8, 10, 12, 14, 16, 18])
                        departure_time_obj = time(departure_hour, random.choice([0, 15, 30, 45]))
                        
                        # Flight duration (1-3 hours)
                        duration_hours = random.randint(1, 3)
                        arrival_hour = (departure_hour + duration_hours) % 24
                        arrival_time_obj = time(arrival_hour, random.choice([0, 15, 30, 45]))
                        
                        # Price based on distance and class
                        base_price = random.randint(50000, 250000)
                        
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
                            if flight_count % 10 == 0:
                                self.stdout.write(f"  Created {flight_count} flights...")
        
        self.stdout.write(self.style.SUCCESS(f'Created {flight_count} flights total'))
        
        # ========== POPULATE BUS SERVICES ON MAJOR ROUTES ==========
        self.stdout.write('\nCreating bus services on major routes...')
        
        bus_companies = ['JJ Express', 'Elite Express', 'Shwe Mandalar', 'Lumbini Bus', 
                        'Mandalar Express', 'Asia Express', 'Shwe Pyi', 'Aung Gabar']
        
        # Major bus routes in Myanmar
        major_bus_routes = [
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
            ('Yangon', 'Pyin Oo Lwin'),
            ('Mandalay', 'Pyin Oo Lwin'),
            ('Yangon', 'Pathein'),
            ('Yangon', 'Sittwe'),
            ('Mandalay', 'Loikaw'),
        ]
        
        bus_count = 0
        for route in major_bus_routes:
            from_city_name, to_city_name = route
            
            try:
                departure = Destination.objects.get(name__icontains=from_city_name)
                arrival = Destination.objects.get(name__icontains=to_city_name)
            except Destination.DoesNotExist:
                continue
            
            # Create 1-2 bus services per route
            for bus_num in range(1, random.randint(2, 3)):
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
                    if bus_count % 5 == 0:
                        self.stdout.write(f"  Created {bus_count} buses...")
        
        self.stdout.write(self.style.SUCCESS(f'Created {bus_count} bus services'))
        
        # ========== POPULATE CAR RENTALS IN MAJOR CITIES ==========
        self.stdout.write('\nCreating car rentals in major cities...')
        
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
        car_cities = ['Yangon', 'Mandalay', 'Naypyidaw', 'Bagan', 'Taunggyi', 
                     'Mawlamyine', 'Pyin Oo Lwin', 'Ngapali Beach']
        
        car_count = 0
        for city_name in car_cities:
            try:
                location = Destination.objects.get(name__icontains=city_name)
            except Destination.DoesNotExist:
                continue
            
            # Create 2-4 car rentals per city
            for rental_num in range(random.randint(2, 5)):
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
                    if car_count % 5 == 0:
                        self.stdout.write(f"  Created {car_count} cars...")
        
        self.stdout.write(self.style.SUCCESS(f'Created {car_count} car rentals'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Transport Summary: {flight_count} flights, {bus_count} buses, {car_count} cars'
        ))
    
    def create_transport_schedules(self):
        """Create schedules for next 30 days for all transport"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('CREATING TRANSPORT SCHEDULES FOR NEXT 30 DAYS')
        self.stdout.write('=' * 60)
        
        # Get all transport
        flights = Flight.objects.filter(is_active=True)
        buses = BusService.objects.filter(is_active=True)
        cars = CarRental.objects.filter(is_available=True)
        
        self.stdout.write(f"Found: {flights.count()} flights, {buses.count()} buses, {cars.count()} cars")
        
        # Create schedules for next 30 days
        today = timezone.now().date()
        schedule_count = 0
        
        # Flights schedules
        self.stdout.write('Creating flight schedules...')
        for flight in flights:
            for day in range(30):
                schedule_date = today + timedelta(days=day)
                
                # Calculate dynamic price (higher on weekends)
                is_weekend = schedule_date.weekday() >= 5
                price_multiplier = 1.2 if is_weekend else 1.0
                schedule_price = Decimal(str(float(flight.price) * price_multiplier))
                
                # Calculate dynamic availability
                base_available = flight.available_seats
                if is_weekend:
                    available_seats = max(5, int(base_available * 0.7))
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
                    schedule_count += 1
        
        self.stdout.write(f"Created {schedule_count} flight schedules")
        total_schedules = schedule_count
        
        # Bus schedules
        self.stdout.write('Creating bus schedules...')
        bus_schedule_count = 0
        for bus in buses:
            for day in range(30):
                schedule_date = today + timedelta(days=day)
                
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
        
        self.stdout.write(f"Created {bus_schedule_count} bus schedules")
        total_schedules += bus_schedule_count
        
        # Car schedules
        self.stdout.write('Creating car schedules...')
        car_schedule_count = 0
        for car in cars:
            for day in range(30):
                schedule_date = today + timedelta(days=day)
                
                # Dynamic pricing (higher on weekends)
                is_weekend = schedule_date.weekday() >= 5
                price_multiplier = 1.25 if is_weekend else 1.0
                schedule_price = Decimal(str(float(car.price_per_day) * price_multiplier))
                
                # Car availability (less available on weekends)
                if is_weekend:
                    available_seats = random.choice([0, 1])
                else:
                    available_seats = random.choice([1, 1, 1, 0])
                
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
        
        self.stdout.write(f"Created {car_schedule_count} car schedules")
        total_schedules += car_schedule_count
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Schedules created: {total_schedules} total schedules for next 30 days'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   - Flight schedules: {schedule_count}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   - Bus schedules: {bus_schedule_count}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   - Car schedules: {car_schedule_count}'
        ))