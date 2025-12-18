from django.core.management.base import BaseCommand
from planner.models import Destination, Hotel, Flight, BusService, CarRental
from decimal import Decimal
from datetime import time, timedelta

class Command(BaseCommand):
    help = 'Populate database with sample data for Myanmar Travel Planner'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data population...')
        
        # Create destinations
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
             "description": "Former capital and largest city, known for Shwedagon Pagoda."},
            {"name": "Mandalay", "region": "Central Myanmar", "type": "region",
             "description": "Cultural capital and last royal capital of Myanmar."},
            {"name": "Bago", "region": "Lower Myanmar", "type": "region",
             "description": "Ancient capital with many pagodas and monasteries."},
            {"name": "Magway", "region": "Central Myanmar", "type": "region",
             "description": "Central region known for oil fields and Thanboddhay Pagoda."},
            {"name": "Sagaing", "region": "Northern Myanmar", "type": "region",
             "description": "Region with many monasteries and religious sites."},
            {"name": "Tanintharyi", "region": "Southern Myanmar", "type": "region",
             "description": "Southernmost region with beautiful islands and beaches."},
            {"name": "Ayeyarwady", "region": "Lower Myanmar", "type": "region",
             "description": "Delta region with riverine landscapes and fishing villages."},
            {"name": "Naypyidaw", "region": "Central Myanmar", "type": "union_territory",
             "description": "Capital city of Myanmar since 2005."},
            
            # Popular Cities/Towns
            {"name": "Bagan", "region": "Mandalay Region", "type": "city",
             "description": "Ancient city with over 2,000 Buddhist temples and pagodas."},
            {"name": "Inle Lake", "region": "Shan State", "type": "attraction",
             "description": "Freshwater lake known for floating villages and leg-rowing fishermen."},
            {"name": "Ngapali Beach", "region": "Rakhine State", "type": "attraction",
             "description": "Pristine beach with white sand and clear water."},
            {"name": "Ngwe Saung Beach", "region": "Ayeyarwady Region", "type": "attraction",
             "description": "Beautiful beach resort area near Yangon."},
            {"name": "Pyin Oo Lwin", "region": "Mandalay Region", "type": "town",
             "description": "Hill station known for colonial architecture and botanical gardens."},
            {"name": "Hsipaw", "region": "Shan State", "type": "town",
             "description": "Gateway to Shan State's hill tribe areas and trekking routes."},
            {"name": "Kalaw", "region": "Shan State", "type": "town",
             "description": "Hill station popular for trekking to Inle Lake."},
            {"name": "Mawlamyine", "region": "Mon State", "type": "city",
             "description": "Third largest city, former British colonial capital."},
            {"name": "Hpa-An", "region": "Kayin State", "type": "town",
             "description": "Capital of Kayin State with dramatic limestone mountains."},
            {"name": "Dawei", "region": "Tanintharyi Region", "type": "city",
             "description": "Southern city with beautiful beaches and islands."},
            {"name": "Myeik", "region": "Tanintharyi Region", "type": "city",
             "description": "Coastal city known for the Myeik Archipelago."},
            {"name": "Monywa", "region": "Sagaing Region", "type": "city",
             "description": "City known for Thanboddhay Pagoda and Bodhi Tataung."},
            {"name": "Taunggyi", "region": "Shan State", "type": "city",
             "description": "Capital of Shan State and famous for hot air balloon festival."},
            {"name": "Loikaw", "region": "Kayah State", "type": "city",
             "description": "Capital of Kayah State with traditional cultures."},
            {"name": "Hakha", "region": "Chin State", "type": "city",
             "description": "Capital of Chin State with cool climate and mountain views."},
            {"name": "Sittwe", "region": "Rakhine State", "type": "city",
             "description": "Capital of Rakhine State with colonial architecture."},
            {"name": "Pathein", "region": "Ayeyarwady Region", "type": "city",
             "description": "Capital of Ayeyarwady Region known for umbrella making."},
        ]
        
        for data in destinations_data:
            dest, created = Destination.objects.get_or_create(
                name=data["name"],
                defaults=data
            )
            if created:
                self.stdout.write(f"Created destination: {dest.name}")
            else:
                self.stdout.write(f"Updated destination: {dest.name}")
        
        self.stdout.write(self.style.SUCCESS('Destinations populated successfully!'))
        
        # Populate hotels
        self.populate_hotels()
        
        # Populate transport
        self.populate_transport()
        
        self.stdout.write(self.style.SUCCESS('All data populated successfully!'))
    
    def populate_hotels(self):
        """Populate hotel data"""
        self.stdout.write('Populating hotels...')
        
        # Get destinations
        yangon = Destination.objects.get(name="Yangon")
        mandalay = Destination.objects.get(name="Mandalay")
        bagan = Destination.objects.get(name="Bagan")
        inle_lake = Destination.objects.get(name="Inle Lake")
        
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
                "review_count": 1243
            },
            {
                "name": "Pan Pacific Yangon",
                "destination": yangon,
                "address": "Pyay Road, Yangon",
                "price_per_night": Decimal("150.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "restaurant", "gym", "spa"],
                "rating": Decimal("4.7"),
                "review_count": 892
            },
            {
                "name": "Hotel Grand United (21st Downtown)",
                "destination": yangon,
                "address": "21st Street, Downtown Yangon",
                "price_per_night": Decimal("50.00"),
                "category": "budget",
                "amenities": ["wifi", "restaurant", "airport shuttle"],
                "rating": Decimal("4.2"),
                "review_count": 567
            },
            {
                "name": "Excel River View Hotel",
                "destination": yangon,
                "address": "Strand Road, Yangon",
                "price_per_night": Decimal("35.00"),
                "category": "budget",
                "amenities": ["wifi", "restaurant", "river view"],
                "rating": Decimal("4.0"),
                "review_count": 432
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
                "review_count": 1056
            },
            {
                "name": "Mandalay Hill Resort",
                "destination": mandalay,
                "address": "Near Mandalay Hill, Mandalay",
                "price_per_night": Decimal("120.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "restaurant", "hill view"],
                "rating": Decimal("4.6"),
                "review_count": 789
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
                "review_count": 892
            },
            {
                "name": "Aureum Palace Hotel & Resort Bagan",
                "destination": bagan,
                "address": "Bagan-Nyaung U Road, Bagan",
                "price_per_night": Decimal("200.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "golf", "restaurant", "pagoda view"],
                "rating": Decimal("4.8"),
                "review_count": 745
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
                "review_count": 678
            },
            {
                "name": "Golden Island Cottages",
                "destination": inle_lake,
                "address": "Nyaung Shwe, Inle Lake",
                "price_per_night": Decimal("80.00"),
                "category": "medium",
                "amenities": ["wifi", "lake view", "restaurant", "boat service"],
                "rating": Decimal("4.5"),
                "review_count": 543
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
                    "is_active": True
                }
            )
            if created:
                self.stdout.write(f"Created hotel: {hotel.name} in {hotel.destination.name}")
            else:
                self.stdout.write(f"Updated hotel: {hotel.name}")
        
        self.stdout.write(self.style.SUCCESS(f'HOTELS populated: {Hotel.objects.count()} hotels'))
    
    def populate_transport(self):
        """Populate transport data"""
        self.stdout.write('Populating transport options...')
        
        # Get destinations
        yangon = Destination.objects.get(name="Yangon")
        mandalay = Destination.objects.get(name="Mandalay")
        bagan = Destination.objects.get(name="Bagan")
        
        # Flights
        FLIGHTS = [
            {
                "airline": "Air KBZ",
                "flight_number": "K7 201",
                "departure": yangon,
                "arrival": mandalay,
                "departure_time": time(6, 0),
                "arrival_time": time(7, 30),
                "duration": timedelta(hours=1, minutes=30),
                "price": Decimal("50.00"),
                "category": "low",
                "total_seats": 180,
                "available_seats": 150,
                "is_active": True
            },
            {
                "airline": "Myanmar National Airlines",
                "flight_number": "UB 301",
                "departure": yangon,
                "arrival": mandalay,
                "departure_time": time(10, 0),
                "arrival_time": time(11, 30),
                "duration": timedelta(hours=1, minutes=30),
                "price": Decimal("80.00"),
                "category": "medium",
                "total_seats": 150,
                "available_seats": 120,
                "is_active": True
            },
            {
                "airline": "Golden Myanmar Airlines",
                "flight_number": "GY 101",
                "departure": yangon,
                "arrival": mandalay,
                "departure_time": time(14, 0),
                "arrival_time": time(15, 30),
                "duration": timedelta(hours=1, minutes=30),
                "price": Decimal("120.00"),
                "category": "high",
                "total_seats": 120,
                "available_seats": 80,
                "is_active": True
            },
        ]
        
        for flight_data in FLIGHTS:
            flight, created = Flight.objects.get_or_create(
                airline=flight_data["airline"],
                flight_number=flight_data["flight_number"],
                departure=flight_data["departure"],
                arrival=flight_data["arrival"],
                defaults=flight_data
            )
            if created:
                self.stdout.write(f"Created flight: {flight.airline} {flight.flight_number}")
        
        # Bus Services
        BUSES = [
            {
                "company": "JJ Express",
                "departure": yangon,
                "arrival": mandalay,
                "departure_time": time(20, 0),
                "duration": timedelta(hours=9),
                "price": Decimal("20.00"),
                "bus_type": "standard",
                "total_seats": 40,
                "available_seats": 30,
                "is_active": True
            },
            {
                "company": "Elite Bus",
                "departure": yangon,
                "arrival": mandalay,
                "departure_time": time(21, 0),
                "duration": timedelta(hours=8, minutes=30),
                "price": Decimal("40.00"),
                "bus_type": "vip",
                "total_seats": 30,
                "available_seats": 25,
                "is_active": True
            },
            {
                "company": "Luxury Coach",
                "departure": yangon,
                "arrival": mandalay,
                "departure_time": time(22, 0),
                "duration": timedelta(hours=8),
                "price": Decimal("60.00"),
                "bus_type": "luxury",
                "total_seats": 20,
                "available_seats": 15,
                "is_active": True
            },
        ]
        
        for bus_data in BUSES:
            bus, created = BusService.objects.get_or_create(
                company=bus_data["company"],
                departure=bus_data["departure"],
                arrival=bus_data["arrival"],
                defaults=bus_data
            )
            if created:
                self.stdout.write(f"Created bus: {bus.company}")
        
        # Car Rentals
        CARS = [
            {
                "company": "City Car Rental",
                "car_model": "Toyota Vios",
                "car_type": "economy",
                "seats": 4,
                "price_per_day": Decimal("35.00"),
                "features": ["AC", "GPS", "Automatic"],
                "is_available": True,
                "location": yangon
            },
            {
                "company": "Premium Rentals",
                "car_model": "Toyota Fortuner",
                "car_type": "suv",
                "seats": 7,
                "price_per_day": Decimal("65.00"),
                "features": ["AC", "GPS", "Automatic", "Sunroof"],
                "is_available": True,
                "location": yangon
            },
            {
                "company": "Luxury Wheels",
                "car_model": "Mercedes E-Class",
                "car_type": "luxury",
                "seats": 4,
                "price_per_day": Decimal("120.00"),
                "features": ["AC", "GPS", "Automatic", "Leather", "Premium Sound"],
                "is_available": True,
                "location": yangon
            },
        ]
        
        for car_data in CARS:
            car, created = CarRental.objects.get_or_create(
                company=car_data["company"],
                car_model=car_data["car_model"],
                location=car_data["location"],
                defaults=car_data
            )
            if created:
                self.stdout.write(f"Created car: {car.company} - {car.car_model}")
        
        self.stdout.write(self.style.SUCCESS(f'Transport populated: {Flight.objects.count()} flights, {BusService.objects.count()} buses, {CarRental.objects.count()} cars'))