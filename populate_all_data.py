

import os
import sys
import django
from decimal import Decimal
from datetime import time, timedelta, date
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Destination, Hotel, Flight, BusService, CarRental
from users.models import CustomUser
from django.contrib.auth.hashers import make_password

def populate_all_data():
    print("=== POPULATING COMPREHENSIVE TRAVEL DATA ===")
    
    # 1. Create sample users
    print("\n1. Creating sample users...")
    users_data = [
        {
            'username': 'john_traveler',
            'email': 'john@example.com',
            'password': 'travel123',
            'user_type': 'user',
            'bio': 'Passionate traveler exploring Myanmar'
        },
        {
            'username': 'sarah_explorer',
            'email': 'sarah@example.com',
            'password': 'explore2024',
            'user_type': 'user',
            'bio': 'Adventure seeker in Southeast Asia'
        },
        {
            'username': 'mike_adventurer',
            'email': 'mike@example.com',
            'password': 'adventure!',
            'user_type': 'user',
            'bio': 'Cultural explorer and photographer'
        },
        {
            'username': 'lisa_wanderer',
            'email': 'lisa@example.com',
            'password': 'wanderlust',
            'user_type': 'user',
            'bio': 'Digital nomad exploring Myanmar'
        },
        {
            'username': 'admin_user',
            'email': 'admin@travel.mm',
            'password': 'admin123',
            'user_type': 'admin',
            'bio': 'System Administrator'
        }
    ]
    
    for user_data in users_data:
        if not CustomUser.objects.filter(email=user_data['email']).exists():
            user = CustomUser.objects.create(
                username=user_data['username'],
                email=user_data['email'],
                password=make_password(user_data['password']),
                user_type=user_data['user_type'],
                bio=user_data['bio'],
                is_active=True
            )
            print(f"  Created user: {user.username} ({user.email})")
    
    print(f"  Total users: {CustomUser.objects.count()}")
    
    # 2. Create destinations (if not already created)
    print("\n2. Creating/updating destinations...")
    
    destinations_data = [
        {
            'name': 'Yangon',
            'region': 'Lower Myanmar',
            'type': 'city',
            'description': 'Former capital and largest city of Myanmar, famous for Shwedagon Pagoda, colonial architecture, and vibrant street life.'
        },
        {
            'name': 'Mandalay',
            'region': 'Central Myanmar',
            'type': 'city',
            'description': 'Cultural capital and last royal capital, known for Mandalay Hill, ancient pagodas, and traditional crafts.'
        },
        {
            'name': 'Bagan',
            'region': 'Mandalay Region',
            'type': 'city',
            'description': 'Ancient city with over 2,000 Buddhist temples and pagodas dating from the 9th to 13th centuries.'
        },
        {
            'name': 'Inle Lake',
            'region': 'Shan State',
            'type': 'attraction',
            'description': 'Freshwater lake famous for floating villages, leg-rowing fishermen, and traditional handicrafts.'
        },
        {
            'name': 'Ngapali Beach',
            'region': 'Rakhine State',
            'type': 'attraction',
            'description': 'Pristine beach with white sand, clear water, and luxury resorts along the Bay of Bengal.'
        },
        {
            'name': 'Pyin Oo Lwin',
            'region': 'Mandalay Region',
            'type': 'town',
            'description': 'Hill station known for colonial architecture, botanical gardens, and cool climate.'
        },
        {
            'name': 'Hpa-An',
            'region': 'Kayin State',
            'type': 'town',
            'description': 'Scenic town surrounded by limestone mountains, caves, and the Thanlwin River.'
        },
        {
            'name': 'Kalaw',
            'region': 'Shan State',
            'type': 'town',
            'description': 'Hill station popular for trekking to Inle Lake through ethnic villages and tea plantations.'
        },
        {
            'name': 'Mawlamyine',
            'region': 'Mon State',
            'type': 'city',
            'description': 'Third largest city and former British colonial capital with historic pagodas.'
        },
        {
            'name': 'Naypyidaw',
            'region': 'Central Myanmar',
            'type': 'city',
            'description': 'Capital city of Myanmar since 2005, known for its wide boulevards and government buildings.'
        }
    ]
    
    for dest_data in destinations_data:
        dest, created = Destination.objects.get_or_create(
            name=dest_data['name'],
            defaults=dest_data
        )
        if created:
            print(f"  Created destination: {dest.name}")
        else:
            dest.region = dest_data['region']
            dest.type = dest_data['type']
            dest.description = dest_data['description']
            dest.save()
            print(f"  Updated destination: {dest.name}")
    
    print(f"  Total destinations: {Destination.objects.count()}")
    
    # Get destination objects
    yangon = Destination.objects.get(name='Yangon')
    mandalay = Destination.objects.get(name='Mandalay')
    bagan = Destination.objects.get(name='Bagan')
    inle_lake = Destination.objects.get(name='Inle Lake')
    ngapali = Destination.objects.get(name='Ngapali Beach')
    pyin_oo_lwin = Destination.objects.get(name='Pyin Oo Lwin')
    hpa_an = Destination.objects.get(name='Hpa-An')
    kalaw = Destination.objects.get(name='Kalaw')
    
    # 3. Create comprehensive hotels (at least 5 per destination)
    print("\n3. Creating comprehensive hotels...")
    
    hotels_data = [
        # Yangon Hotels (8 hotels)
        {
            'name': 'Sule Shangri-La Yangon',
            'destination': yangon,
            'address': '223 Sule Pagoda Road, Yangon 11182',
            'price_per_night': Decimal('180.00'),
            'category': 'luxury',
            'amenities': ['wifi', 'pool', 'spa', 'gym', 'restaurant', 'bar', 'concierge', 'business center'],
            'rating': Decimal('4.8'),
            'review_count': 1243,
            'description': '5-star luxury hotel in downtown Yangon with panoramic city views.'
        },
        {
            'name': 'Pan Pacific Yangon',
            'destination': yangon,
            'address': 'Pyay Road, Kamaryut Township, Yangon',
            'price_per_night': Decimal('150.00'),
            'category': 'luxury',
            'amenities': ['wifi', 'pool', 'spa', 'gym', 'restaurant', 'bar', 'airport shuttle'],
            'rating': Decimal('4.7'),
            'review_count': 892,
            'description': 'Modern luxury hotel with excellent facilities and service.'
        },
        {
            'name': 'The Strand Yangon',
            'destination': yangon,
            'address': '92 Strand Road, Yangon',
            'price_per_night': Decimal('250.00'),
            'category': 'luxury',
            'amenities': ['wifi', 'pool', 'spa', 'butler service', 'fine dining', 'historic building'],
            'rating': Decimal('4.9'),
            'review_count': 956,
            'description': 'Historic colonial-era luxury hotel with impeccable service.'
        },
        {
            'name': 'Hotel Grand United (21st Downtown)',
            'destination': yangon,
            'address': '21st Street, Downtown Yangon',
            'price_per_night': Decimal('50.00'),
            'category': 'budget',
            'amenities': ['wifi', 'restaurant', 'airport shuttle', '24-hour front desk'],
            'rating': Decimal('4.2'),
            'review_count': 567,
            'description': 'Clean, comfortable budget hotel in the heart of downtown.'
        },
        {
            'name': 'Excel River View Hotel',
            'destination': yangon,
            'address': 'Strand Road, Yangon',
            'price_per_night': Decimal('35.00'),
            'category': 'budget',
            'amenities': ['wifi', 'restaurant', 'river view', 'free breakfast'],
            'rating': Decimal('4.0'),
            'review_count': 432,
            'description': 'Affordable hotel with beautiful views of the Yangon River.'
        },
        {
            'name': 'Rose Garden Hotel Yangon',
            'destination': yangon,
            'address': '123 Upper Pazundaung Road, Yangon',
            'price_per_night': Decimal('75.00'),
            'category': 'medium',
            'amenities': ['wifi', 'pool', 'restaurant', 'garden', 'tour desk'],
            'rating': Decimal('4.4'),
            'review_count': 321,
            'description': 'Peaceful hotel with beautiful gardens and pool.'
        },
        {
            'name': 'Jasmine Palace Hotel',
            'destination': yangon,
            'address': '341 Bogyoke Aung San Road, Yangon',
            'price_per_night': Decimal('90.00'),
            'category': 'medium',
            'amenities': ['wifi', 'restaurant', 'spa', 'business center', 'concierge'],
            'rating': Decimal('4.3'),
            'review_count': 278,
            'description': 'Modern hotel with excellent location near major attractions.'
        },
        {
            'name': 'Orchid Hotel Yangon',
            'destination': yangon,
            'address': 'Seikkantha Street, Yangon',
            'price_per_night': Decimal('65.00'),
            'category': 'medium',
            'amenities': ['wifi', 'restaurant', 'rooftop bar', 'tour assistance'],
            'rating': Decimal('4.1'),
            'review_count': 189,
            'description': 'Comfortable mid-range hotel with friendly staff.'
        },
        
        # Mandalay Hotels (6 hotels)
        {
            'name': 'Mandalay Hill Resort',
            'destination': mandalay,
            'address': 'Near Mandalay Hill, Mandalay',
            'price_per_night': Decimal('120.00'),
            'category': 'luxury',
            'amenities': ['wifi', 'pool', 'spa', 'restaurant', 'hill view', 'gym'],
            'rating': Decimal('4.6'),
            'review_count': 789,
            'description': 'Luxury resort with stunning views of Mandalay Hill.'
        },
        {
            'name': 'Royal Mandalay Hotel',
            'destination': mandalay,
            'address': 'Corner of 26th & 68th Street, Mandalay',
            'price_per_night': Decimal('95.00'),
            'category': 'medium',
            'amenities': ['wifi', 'pool', 'restaurant', 'garden', 'tour desk'],
            'rating': Decimal('4.7'),
            'review_count': 1056,
            'description': 'Beautiful hotel with traditional Myanmar architecture.'
        },
        {
            'name': 'Mandalay City Hotel',
            'destination': mandalay,
            'address': '26th Street, Between 65th & 66th Street, Mandalay',
            'price_per_night': Decimal('45.00'),
            'category': 'budget',
            'amenities': ['wifi', 'restaurant', 'city center', 'air conditioning'],
            'rating': Decimal('4.1'),
            'review_count': 321,
            'description': 'Affordable hotel in central Mandalay.'
        },
        {
            'name': 'Ayarwaddy River View Hotel',
            'destination': mandalay,
            'address': '22nd Road, Between 64th & 65th Street, Mandalay',
            'price_per_night': Decimal('55.00'),
            'category': 'medium',
            'amenities': ['wifi', 'restaurant', 'river view', 'rooftop'],
            'rating': Decimal('4.3'),
            'review_count': 234,
            'description': 'Hotel with beautiful views of the Ayeyarwady River.'
        },
        {
            'name': 'The Hotel @ Thazin Garden',
            'destination': mandalay,
            'address': 'Corner of 68th & 28th Street, Mandalay',
            'price_per_night': Decimal('70.00'),
            'category': 'medium',
            'amenities': ['wifi', 'garden', 'restaurant', 'pool', 'spa'],
            'rating': Decimal('4.4'),
            'review_count': 456,
            'description': 'Peaceful hotel set in beautiful gardens.'
        },
        {
            'name': 'Mandalay Backpacker Hostel',
            'destination': mandalay,
            'address': '25th Street, Mandalay',
            'price_per_night': Decimal('15.00'),
            'category': 'budget',
            'amenities': ['wifi', 'shared kitchen', 'common room', 'tour booking'],
            'rating': Decimal('4.0'),
            'review_count': 567,
            'description': 'Friendly hostel for budget travelers and backpackers.'
        },
        
        # Bagan Hotels (6 hotels)
        {
            'name': 'Aureum Palace Hotel & Resort Bagan',
            'destination': bagan,
            'address': 'Bagan-Nyaung U Road, Bagan',
            'price_per_night': Decimal('200.00'),
            'category': 'luxury',
            'amenities': ['wifi', 'pool', 'spa', 'golf', 'restaurant', 'pagoda view', 'private balcony'],
            'rating': Decimal('4.8'),
            'review_count': 745,
            'description': 'Luxury resort with stunning views of ancient pagodas.'
        },
        {
            'name': 'Bagan Lodge',
            'destination': bagan,
            'address': 'Old Bagan, Bagan Archaeological Zone',
            'price_per_night': Decimal('120.00'),
            'category': 'medium',
            'amenities': ['wifi', 'pool', 'restaurant', 'garden', 'bicycle rental', 'tour desk'],
            'rating': Decimal('4.6'),
            'review_count': 892,
            'description': 'Beautiful lodge-style hotel in the heart of ancient Bagan.'
        },
        {
            'name': 'Bagan Thande Hotel',
            'destination': bagan,
            'address': 'Old Bagan, Near Bu Pagoda',
            'price_per_night': Decimal('60.00'),
            'category': 'budget',
            'amenities': ['wifi', 'garden', 'restaurant', 'river view', 'bicycle rental'],
            'rating': Decimal('4.3'),
            'review_count': 456,
            'description': 'Historic hotel with beautiful gardens and Irrawaddy River views.'
        },
        {
            'name': 'Heritage Bagan Hotel',
            'destination': bagan,
            'address': 'Nyaung U, Bagan',
            'price_per_night': Decimal('85.00'),
            'category': 'medium',
            'amenities': ['wifi', 'pool', 'restaurant', 'spa', 'cultural shows'],
            'rating': Decimal('4.5'),
            'review_count': 389,
            'description': 'Hotel showcasing traditional Bagan architecture and culture.'
        },
        {
            'name': 'Bagan Princess Hotel',
            'destination': bagan,
            'address': 'Khayee Road, Nyaung U',
            'price_per_night': Decimal('50.00'),
            'category': 'budget',
            'amenities': ['wifi', 'restaurant', 'tour assistance', 'airport transfer'],
            'rating': Decimal('4.2'),
            'review_count': 267,
            'description': 'Comfortable budget hotel with friendly service.'
        },
        {
            'name': 'Bagan Umbra Hotel',
            'destination': bagan,
            'address': 'Anawrahta Road, Nyaung U',
            'price_per_night': Decimal('75.00'),
            'category': 'medium',
            'amenities': ['wifi', 'pool', 'restaurant', 'rooftop bar', 'sunset view'],
            'rating': Decimal('4.4'),
            'review_count': 312,
            'description': 'Modern hotel with excellent sunset views over the temples.'
        },
        
        # Inle Lake Hotels (5 hotels)
        {
            'name': 'Novotel Inle Lake Myat Min',
            'destination': inle_lake,
            'address': 'Maing Thauk Village, Inle Lake',
            'price_per_night': Decimal('140.00'),
            'category': 'luxury',
            'amenities': ['wifi', 'pool', 'spa', 'lake view', 'restaurant', 'boat pier', 'fishing'],
            'rating': Decimal('4.7'),
            'review_count': 678,
            'description': 'Luxury hotel built on stilts over Inle Lake.'
        },
        {
            'name': 'Golden Island Cottages',
            'destination': inle_lake,
            'address': 'Nyaung Shwe, Inle Lake',
            'price_per_night': Decimal('80.00'),
            'category': 'medium',
            'amenities': ['wifi', 'lake view', 'restaurant', 'boat service', 'cultural tours'],
            'rating': Decimal('4.5'),
            'review_count': 543,
            'description': 'Traditional stilt cottages offering authentic lake experience.'
        },
        {
            'name': 'Paradise Inle Resort',
            'destination': inle_lake,
            'address': 'Maing Thauk Village, Inle Lake',
            'price_per_night': Decimal('110.00'),
            'category': 'luxury',
            'amenities': ['wifi', 'pool', 'spa', 'overwater bungalows', 'restaurant', 'kayaking'],
            'rating': Decimal('4.6'),
            'review_count': 432,
            'description': 'Luxury overwater bungalows with private decks.'
        },
        {
            'name': 'Inle Inn',
            'destination': inle_lake,
            'address': 'Yone Gyi Road, Nyaung Shwe',
            'price_per_night': Decimal('40.00'),
            'category': 'budget',
            'amenities': ['wifi', 'restaurant', 'bicycle rental', 'garden', 'tour booking'],
            'rating': Decimal('4.2'),
            'review_count': 234,
            'description': 'Charming budget inn in Nyaung Shwe town.'
        },
        {
            'name': 'Viewpoint Lodge',
            'destination': inle_lake,
            'address': 'Khaung Daing Village, Inle Lake',
            'price_per_night': Decimal('65.00'),
            'category': 'medium',
            'amenities': ['wifi', 'restaurant', 'mountain view', 'hot springs access', 'hiking'],
            'rating': Decimal('4.3'),
            'review_count': 189,
            'description': 'Lodge with stunning mountain and lake views.'
        },
        
        # Ngapali Beach Hotels (5 hotels)
        {
            'name': 'Amata Resort & Spa Ngapali',
            'destination': ngapali,
            'address': 'Ngapali Beach, Rakhine State',
            'price_per_night': Decimal('160.00'),
            'category': 'luxury',
            'amenities': ['wifi', 'pool', 'spa', 'beachfront', 'restaurant', 'water sports'],
            'rating': Decimal('4.7'),
            'review_count': 456,
            'description': 'Luxury beachfront resort with private beach access.'
        },
        {
            'name': 'Bayview Beach Resort',
            'destination': ngapali,
            'address': 'Ngapali Beach, Thandwe',
            'price_per_night': Decimal('130.00'),
            'category': 'luxury',
            'amenities': ['wifi', 'pool', 'spa', 'beachfront', 'multiple restaurants', 'kids club'],
            'rating': Decimal('4.6'),
            'review_count': 389,
            'description': 'Family-friendly resort with extensive facilities.'
        },
        {
            'name': 'Ngapali Bay Hotel',
            'destination': ngapali,
            'address': 'Main Road, Ngapali Beach',
            'price_per_night': Decimal('95.00'),
            'category': 'medium',
            'amenities': ['wifi', 'pool', 'beach access', 'restaurant', 'massage'],
            'rating': Decimal('4.4'),
            'review_count': 267,
            'description': 'Comfortable hotel just steps from the beach.'
        },
        {
            'name': 'Sea Sun Hotel',
            'destination': ngapali,
            'address': 'Ngapali Beach Road',
            'price_per_night': Decimal('55.00'),
            'category': 'budget',
            'amenities': ['wifi', 'restaurant', 'beach view', 'tour desk'],
            'rating': Decimal('4.1'),
            'review_count': 189,
            'description': 'Affordable beachfront accommodation.'
        },
        {
            'name': 'Sandoway Beach Resort',
            'destination': ngapali,
            'address': 'Ngapali Beach, Thandwe',
            'price_per_night': Decimal('75.00'),
            'category': 'medium',
            'amenities': ['wifi', 'pool', 'beachfront', 'restaurant', 'snorkeling gear'],
            'rating': Decimal('4.3'),
            'review_count': 234,
            'description': 'Relaxing resort with direct beach access.'
        },
    ]
    
    for hotel_data in hotels_data:
        hotel, created = Hotel.objects.get_or_create(
            name=hotel_data['name'],
            destination=hotel_data['destination'],
            defaults={
                'address': hotel_data['address'],
                'price_per_night': hotel_data['price_per_night'],
                'category': hotel_data['category'],
                'amenities': hotel_data['amenities'],
                'rating': hotel_data['rating'],
                'review_count': hotel_data['review_count'],
                'description': hotel_data.get('description', ''),
                'is_active': True
            }
        )
        if created:
            print(f"  Created hotel: {hotel.name} in {hotel.destination.name}")
        else:
            # Update existing hotel
            for key, value in hotel_data.items():
                if key != 'name' and key != 'destination':
                    setattr(hotel, key, value)
            hotel.save()
    
    print(f"  Total hotels: {Hotel.objects.count()}")
    
    # 4. Create comprehensive flights (at least 5 routes with multiple options)
    print("\n4. Creating comprehensive flights...")
    
    flights_data = [
        # Yangon to Mandalay flights (6 flights)
        {
            'airline': 'Air KBZ',
            'flight_number': 'K7 201',
            'departure': yangon,
            'arrival': mandalay,
            'departure_time': time(6, 0),
            'arrival_time': time(7, 30),
            'duration': timedelta(hours=1, minutes=30),
            'price': Decimal('50.00'),
            'category': 'low',
            'total_seats': 180,
            'available_seats': 150,
            'description': 'Early morning flight, breakfast served'
        },
        {
            'airline': 'Myanmar National Airlines',
            'flight_number': 'UB 301',
            'departure': yangon,
            'arrival': mandalay,
            'departure_time': time(10, 0),
            'arrival_time': time(11, 30),
            'duration': timedelta(hours=1, minutes=30),
            'price': Decimal('80.00'),
            'category': 'medium',
            'total_seats': 150,
            'available_seats': 120,
            'description': 'Mid-morning flight with snack service'
        },
        {
            'airline': 'Golden Myanmar Airlines',
            'flight_number': 'GY 101',
            'departure': yangon,
            'arrival': mandalay,
            'departure_time': time(14, 0),
            'arrival_time': time(15, 30),
            'duration': timedelta(hours=1, minutes=30),
            'price': Decimal('120.00'),
            'category': 'high',
            'total_seats': 120,
            'available_seats': 80,
            'description': 'Business class available, full meal service'
        },
        {
            'airline': 'Mann Yadanarpon Airlines',
            'flight_number': '7Y 701',
            'departure': yangon,
            'arrival': mandalay,
            'departure_time': time(8, 30),
            'arrival_time': time(10, 0),
            'duration': timedelta(hours=1, minutes=30),
            'price': Decimal('65.00'),
            'category': 'low',
            'total_seats': 180,
            'available_seats': 140,
            'description': 'Economy flight with complimentary drink'
        },
        {
            'airline': 'Air KBZ',
            'flight_number': 'K7 205',
            'departure': yangon,
            'arrival': mandalay,
            'departure_time': time(16, 0),
            'arrival_time': time(17, 30),
            'duration': timedelta(hours=1, minutes=30),
            'price': Decimal('70.00'),
            'category': 'medium',
            'total_seats': 180,
            'available_seats': 160,
            'description': 'Evening flight'
        },
        {
            'airline': 'Myanmar Airways International',
            'flight_number': '8M 401',
            'departure': yangon,
            'arrival': mandalay,
            'departure_time': time(19, 0),
            'arrival_time': time(20, 30),
            'duration': timedelta(hours=1, minutes=30),
            'price': Decimal('90.00'),
            'category': 'medium',
            'total_seats': 160,
            'available_seats': 130,
            'description': 'Last flight of the day'
        },
        
        # Yangon to Bagan flights (5 flights)
        {
            'airline': 'Air KBZ',
            'flight_number': 'K7 301',
            'departure': yangon,
            'arrival': bagan,
            'departure_time': time(7, 0),
            'arrival_time': time(8, 15),
            'duration': timedelta(hours=1, minutes=15),
            'price': Decimal('60.00'),
            'category': 'medium',
            'total_seats': 180,
            'available_seats': 140,
            'description': 'Direct flight to Bagan'
        },
        {
            'airline': 'Golden Myanmar Airlines',
            'flight_number': 'GY 201',
            'departure': yangon,
            'arrival': bagan,
            'departure_time': time(11, 0),
            'arrival_time': time(12, 15),
            'duration': timedelta(hours=1, minutes=15),
            'price': Decimal('85.00'),
            'category': 'medium',
            'total_seats': 120,
            'available_seats': 90,
            'description': 'Midday flight with meal'
        },
        {
            'airline': 'Myanmar National Airlines',
            'flight_number': 'UB 501',
            'departure': yangon,
            'arrival': bagan,
            'departure_time': time(15, 0),
            'arrival_time': time(16, 15),
            'duration': timedelta(hours=1, minutes=15),
            'price': Decimal('75.00'),
            'category': 'medium',
            'total_seats': 150,
            'available_seats': 110,
            'description': 'Afternoon flight'
        },
        {
            'airline': 'Mann Yadanarpon Airlines',
            'flight_number': '7Y 801',
            'departure': yangon,
            'arrival': bagan,
            'departure_time': time(9, 30),
            'arrival_time': time(10, 45),
            'duration': timedelta(hours=1, minutes=15),
            'price': Decimal('55.00'),
            'category': 'low',
            'total_seats': 180,
            'available_seats': 150,
            'description': 'Economy flight'
        },
        {
            'airline': 'Air KBZ',
            'flight_number': 'K7 305',
            'departure': yangon,
            'arrival': bagan,
            'departure_time': time(13, 30),
            'arrival_time': time(14, 45),
            'duration': timedelta(hours=1, minutes=15),
            'price': Decimal('70.00'),
            'category': 'medium',
            'total_seats': 180,
            'available_seats': 160,
            'description': 'Early afternoon flight'
        },
        
        # Yangon to Heho (Inle Lake) flights (5 flights)
        {
            'airline': 'Air KBZ',
            'flight_number': 'K7 401',
            'departure': yangon,
            'arrival': inle_lake,  # Note: Inle Lake uses Heho airport
            'departure_time': time(8, 0),
            'arrival_time': time(9, 30),
            'duration': timedelta(hours=1, minutes=30),
            'price': Decimal('70.00'),
            'category': 'medium',
            'total_seats': 180,
            'available_seats': 140,
            'description': 'Flight to Heho for Inle Lake'
        },
        {
            'airline': 'Myanmar National Airlines',
            'flight_number': 'UB 601',
            'departure': yangon,
            'arrival': inle_lake,
            'departure_time': time(12, 0),
            'arrival_time': time(13, 30),
            'duration': timedelta(hours=1, minutes=30),
            'price': Decimal('90.00'),
            'category': 'medium',
            'total_seats': 150,
            'available_seats': 100,
            'description': 'Direct to Heho airport'
        },
        {
            'airline': 'Golden Myanmar Airlines',
            'flight_number': 'GY 301',
            'departure': yangon,
            'arrival': inle_lake,
            'departure_time': time(16, 0),
            'arrival_time': time(17, 30),
            'duration': timedelta(hours=1, minutes=30),
            'price': Decimal('110.00'),
            'category': 'high',
            'total_seats': 120,
            'available_seats': 80,
            'description': 'Business class available'
        },
        {
            'airline': 'Mann Yadanarpon Airlines',
            'flight_number': '7Y 901',
            'departure': yangon,
            'arrival': inle_lake,
            'departure_time': time(10, 30),
            'arrival_time': time(12, 0),
            'duration': timedelta(hours=1, minutes=30),
            'price': Decimal('65.00'),
            'category': 'low',
            'total_seats': 180,
            'available_seats': 150,
            'description': 'Economy flight to Heho'
        },
        {
            'airline': 'Air KBZ',
            'flight_number': 'K7 405',
            'departure': yangon,
            'arrival': inle_lake,
            'departure_time': time(14, 30),
            'arrival_time': time(16, 0),
            'duration': timedelta(hours=1, minutes=30),
            'price': Decimal('80.00'),
            'category': 'medium',
            'total_seats': 180,
            'available_seats': 160,
            'description': 'Afternoon flight'
        },
        
        # Mandalay to Bagan flights (5 flights)
        {
            'airline': 'Air KBZ',
            'flight_number': 'K7 501',
            'departure': mandalay,
            'arrival': bagan,
            'departure_time': time(9, 0),
            'arrival_time': time(9, 45),
            'duration': timedelta(minutes=45),
            'price': Decimal('40.00'),
            'category': 'low',
            'total_seats': 180,
            'available_seats': 140,
            'description': 'Short flight from Mandalay to Bagan'
        },
        {
            'airline': 'Myanmar National Airlines',
            'flight_number': 'UB 701',
            'departure': mandalay,
            'arrival': bagan,
            'departure_time': time(13, 0),
            'arrival_time': time(13, 45),
            'duration': timedelta(minutes=45),
            'price': Decimal('50.00'),
            'category': 'medium',
            'total_seats': 150,
            'available_seats': 110,
            'description': 'Midday flight'
        },
        {
            'airline': 'Golden Myanmar Airlines',
            'flight_number': 'GY 401',
            'departure': mandalay,
            'arrival': bagan,
            'departure_time': time(17, 0),
            'arrival_time': time(17, 45),
            'duration': timedelta(minutes=45),
            'price': Decimal('60.00'),
            'category': 'high',
            'total_seats': 120,
            'available_seats': 90,
            'description': 'Evening flight'
        },
        {
            'airline': 'Mann Yadanarpon Airlines',
            'flight_number': '7Y 1001',
            'departure': mandalay,
            'arrival': bagan,
            'departure_time': time(11, 30),
            'arrival_time': time(12, 15),
            'duration': timedelta(minutes=45),
            'price': Decimal('35.00'),
            'category': 'low',
            'total_seats': 180,
            'available_seats': 160,
            'description': 'Economy flight'
        },
        {
            'airline': 'Air KBZ',
            'flight_number': 'K7 505',
            'departure': mandalay,
            'arrival': bagan,
            'departure_time': time(15, 30),
            'arrival_time': time(16, 15),
            'duration': timedelta(minutes=45),
            'price': Decimal('45.00'),
            'category': 'medium',
            'total_seats': 180,
            'available_seats': 170,
            'description': 'Late afternoon flight'
        },
    ]
    
    for flight_data in flights_data:
        flight, created = Flight.objects.get_or_create(
            airline=flight_data['airline'],
            flight_number=flight_data['flight_number'],
            departure=flight_data['departure'],
            arrival=flight_data['arrival'],
            defaults={
                'departure_time': flight_data['departure_time'],
                'arrival_time': flight_data['arrival_time'],
                'duration': flight_data['duration'],
                'price': flight_data['price'],
                'category': flight_data['category'],
                'total_seats': flight_data['total_seats'],
                'available_seats': flight_data['available_seats'],
                'description': flight_data.get('description', ''),
                'is_active': True
            }
        )
        if created:
            print(f"  Created flight: {flight.airline} {flight.flight_number} ({flight.departure.name} → {flight.arrival.name})")
    
    print(f"  Total flights: {Flight.objects.count()}")
    
    # 5. Create comprehensive bus services (at least 5 routes)
    print("\n5. Creating comprehensive bus services...")
    
    buses_data = [
        # Yangon to Mandalay buses (6 buses)
        {
            'company': 'JJ Express',
            'departure': yangon,
            'arrival': mandalay,
            'departure_time': time(20, 0),
            'duration': timedelta(hours=9),
            'price': Decimal('20.00'),
            'bus_type': 'standard',
            'total_seats': 40,
            'available_seats': 30,
            'amenities': ['AC', 'water', 'blanket', 'TV'],
            'description': 'Overnight bus with reclining seats'
        },
        {
            'company': 'Elite Bus',
            'departure': yangon,
            'arrival': mandalay,
            'departure_time': time(21, 0),
            'duration': timedelta(hours=8, minutes=30),
            'price': Decimal('40.00'),
            'bus_type': 'vip',
            'total_seats': 30,
            'available_seats': 25,
            'amenities': ['AC', 'meal', 'blanket', 'pillow', 'TV', 'WiFi'],
            'description': 'VIP bus with meal service'
        },
        {
            'company': 'Luxury Coach',
            'departure': yangon,
            'arrival': mandalay,
            'departure_time': time(22, 0),
            'duration': timedelta(hours=8),
            'price': Decimal('60.00'),
            'bus_type': 'luxury',
            'total_seats': 20,
            'available_seats': 15,
            'amenities': ['AC', 'meal', 'blanket', 'pillow', 'TV', 'WiFi', 'charging ports', 'toilet'],
            'description': 'Luxury bus with full amenities'
        },
        {
            'company': 'Mandalar Express',
            'departure': yangon,
            'arrival': mandalay,
            'departure_time': time(19, 30),
            'duration': timedelta(hours=9, minutes=30),
            'price': Decimal('25.00'),
            'bus_type': 'standard',
            'total_seats': 40,
            'available_seats': 35,
            'amenities': ['AC', 'water', 'snack'],
            'description': 'Standard overnight bus'
        },
        {
            'company': 'City Express',
            'departure': yangon,
            'arrival': mandalay,
            'departure_time': time(18, 0),
            'duration': timedelta(hours=10),
            'price': Decimal('15.00'),
            'bus_type': 'standard',
            'total_seats': 45,
            'available_seats': 40,
            'amenities': ['AC', 'water'],
            'description': 'Economy bus service'
        },
        {
            'company': 'Golden Harp',
            'departure': yangon,
            'arrival': mandalay,
            'departure_time': time(20, 30),
            'duration': timedelta(hours=8, minutes=45),
            'price': Decimal('35.00'),
            'bus_type': 'vip',
            'total_seats': 32,
            'available_seats': 28,
            'amenities': ['AC', 'snack', 'blanket', 'TV', 'charging ports'],
            'description': 'Premium bus service'
        },
        
        # Yangon to Bagan buses (5 buses)
        {
            'company': 'JJ Express',
            'departure': yangon,
            'arrival': bagan,
            'departure_time': time(19, 0),
            'duration': timedelta(hours=10),
            'price': Decimal('25.00'),
            'bus_type': 'standard',
            'total_seats': 40,
            'available_seats': 35,
            'amenities': ['AC', 'water', 'blanket'],
            'description': 'Overnight bus to Bagan'
        },
        {
            'company': 'Elite Bus',
            'departure': yangon,
            'arrival': bagan,
            'departure_time': time(20, 0),
            'duration': timedelta(hours=9, minutes=30),
            'price': Decimal('45.00'),
            'bus_type': 'vip',
            'total_seats': 30,
            'available_seats': 25,
            'amenities': ['AC', 'meal', 'blanket', 'pillow', 'TV'],
            'description': 'VIP bus to Bagan'
        },
        {
            'company': 'Bagan Express',
            'departure': yangon,
            'arrival': bagan,
            'departure_time': time(21, 0),
            'duration': timedelta(hours=9),
            'price': Decimal('30.00'),
            'bus_type': 'standard',
            'total_seats': 40,
            'available_seats': 30,
            'amenities': ['AC', 'water', 'snack', 'blanket'],
            'description': 'Direct bus to Bagan'
        },
        {
            'company': 'City Express',
            'departure': yangon,
            'arrival': bagan,
            'departure_time': time(18, 30),
            'duration': timedelta(hours=10, minutes=30),
            'price': Decimal('20.00'),
            'bus_type': 'standard',
            'total_seats': 45,
            'available_seats': 40,
            'amenities': ['AC', 'water'],
            'description': 'Economy bus to Bagan'
        },
        {
            'company': 'Luxury Coach',
            'departure': yangon,
            'arrival': bagan,
            'departure_time': time(22, 0),
            'duration': timedelta(hours=8, minutes=45),
            'price': Decimal('55.00'),
            'bus_type': 'luxury',
            'total_seats': 20,
            'available_seats': 15,
            'amenities': ['AC', 'meal', 'blanket', 'pillow', 'TV', 'WiFi', 'toilet'],
            'description': 'Luxury sleeper bus'
        },
        
        # Yangon to Kalaw buses (for Inle Lake) (5 buses)
        {
            'company': 'Shwe Mann Thu',
            'departure': yangon,
            'arrival': kalaw,
            'departure_time': time(19, 0),
            'duration': timedelta(hours=12),
            'price': Decimal('30.00'),
            'bus_type': 'standard',
            'total_seats': 40,
            'available_seats': 35,
            'amenities': ['AC', 'water', 'blanket'],
            'description': 'Overnight bus to Kalaw'
        },
        {
            'company': 'Elite Bus',
            'departure': yangon,
            'arrival': kalaw,
            'departure_time': time(20, 0),
            'duration': timedelta(hours=11, minutes=30),
            'price': Decimal('50.00'),
            'bus_type': 'vip',
            'total_seats': 30,
            'available_seats': 25,
            'amenities': ['AC', 'meal', 'blanket', 'pillow', 'TV'],
            'description': 'VIP bus to Kalaw'
        },
        {
            'company': 'Shan Express',
            'departure': yangon,
            'arrival': kalaw,
            'departure_time': time(18, 30),
            'duration': timedelta(hours=12, minutes=30),
            'price': Decimal('25.00'),
            'bus_type': 'standard',
            'total_seats': 40,
            'available_seats': 30,
            'amenities': ['AC', 'water', 'snack'],
            'description': 'Economy bus to Kalaw'
        },
        {
            'company': 'City Express',
            'departure': yangon,
            'arrival': kalaw,
            'departure_time': time(17, 0),
            'duration': timedelta(hours=13),
            'price': Decimal('20.00'),
            'bus_type': 'standard',
            'total_seats': 45,
            'available_seats': 40,
            'amenities': ['AC', 'water'],
            'description': 'Budget bus to Kalaw'
        },
        {
            'company': 'Luxury Coach',
            'departure': yangon,
            'arrival': kalaw,
            'departure_time': time(21, 0),
            'duration': timedelta(hours=11),
            'price': Decimal('60.00'),
            'bus_type': 'luxury',
            'total_seats': 20,
            'available_seats': 15,
            'amenities': ['AC', 'meal', 'blanket', 'pillow', 'TV', 'WiFi'],
            'description': 'Luxury bus to Kalaw'
        },
        
        # Mandalay to Bagan buses (5 buses)
        {
            'company': 'JJ Express',
            'departure': mandalay,
            'arrival': bagan,
            'departure_time': time(8, 0),
            'duration': timedelta(hours=4),
            'price': Decimal('10.00'),
            'bus_type': 'standard',
            'total_seats': 40,
            'available_seats': 35,
            'amenities': ['AC', 'water'],
            'description': 'Morning bus to Bagan'
        },
        {
            'company': 'Bagan Express',
            'departure': mandalay,
            'arrival': bagan,
            'departure_time': time(14, 0),
            'duration': timedelta(hours=4),
            'price': Decimal('12.00'),
            'bus_type': 'standard',
            'total_seats': 40,
            'available_seats': 30,
            'amenities': ['AC', 'water', 'snack'],
            'description': 'Afternoon bus to Bagan'
        },
        {
            'company': 'Elite Bus',
            'departure': mandalay,
            'arrival': bagan,
            'departure_time': time(10, 0),
            'duration': timedelta(hours=3, minutes=45),
            'price': Decimal('20.00'),
            'bus_type': 'vip',
            'total_seats': 30,
            'available_seats': 25,
            'amenities': ['AC', 'snack', 'TV'],
            'description': 'VIP bus to Bagan'
        },
        {
            'company': 'City Express',
            'departure': mandalay,
            'arrival': bagan,
            'departure_time': time(16, 0),
            'duration': timedelta(hours=4, minutes=30),
            'price': Decimal('8.00'),
            'bus_type': 'standard',
            'total_seats': 45,
            'available_seats': 40,
            'amenities': ['AC'],
            'description': 'Evening budget bus'
        },
        {
            'company': 'Luxury Coach',
            'departure': mandalay,
            'arrival': bagan,
            'departure_time': time(12, 0),
            'duration': timedelta(hours=3, minutes=30),
            'price': Decimal('25.00'),
            'bus_type': 'luxury',
            'total_seats': 20,
            'available_seats': 15,
            'amenities': ['AC', 'meal', 'TV', 'WiFi'],
            'description': 'Luxury express bus'
        },
    ]
    
    for bus_data in buses_data:
        bus, created = BusService.objects.get_or_create(
            company=bus_data['company'],
            departure=bus_data['departure'],
            arrival=bus_data['arrival'],
            departure_time=bus_data['departure_time'],
            defaults={
                'duration': bus_data['duration'],
                'price': bus_data['price'],
                'bus_type': bus_data['bus_type'],
                'total_seats': bus_data['total_seats'],
                'available_seats': bus_data['available_seats'],
                'amenities': bus_data.get('amenities', []),
                'description': bus_data.get('description', ''),
                'is_active': True
            }
        )
        if created:
            print(f"  Created bus: {bus.company} ({bus.departure.name} → {bus.arrival.name})")
    
    print(f"  Total buses: {BusService.objects.count()}")
    
    # 6. Create comprehensive car rentals (at least 5 per location)
    print("\n6. Creating comprehensive car rentals...")
    
    cars_data = [
        # Yangon car rentals (8 cars)
        {
            'company': 'City Car Rental',
            'car_model': 'Toyota Vios',
            'car_type': 'economy',
            'seats': 4,
            'price_per_day': Decimal('35.00'),
            'features': ['AC', 'GPS', 'Automatic', 'Bluetooth', 'Airbags'],
            'is_available': True,
            'location': yangon,
            'description': 'Fuel-efficient economy car, perfect for city driving'
        },
        {
            'company': 'Premium Rentals',
            'car_model': 'Toyota Fortuner',
            'car_type': 'suv',
            'seats': 7,
            'price_per_day': Decimal('65.00'),
            'features': ['AC', 'GPS', 'Automatic', 'Sunroof', '4WD', 'Leather Seats'],
            'is_available': True,
            'location': yangon,
            'description': 'Spacious SUV for family trips or rough roads'
        },
        {
            'company': 'Luxury Wheels',
            'car_model': 'Mercedes E-Class',
            'car_type': 'luxury',
            'seats': 4,
            'price_per_day': Decimal('120.00'),
            'features': ['AC', 'GPS', 'Automatic', 'Leather', 'Premium Sound', 'Sunroof', 'Heated Seats'],
            'is_available': True,
            'location': yangon,
            'description': 'Premium luxury sedan with all features'
        },
        {
            'company': 'Myanmar Rent-a-Car',
            'car_model': 'Honda City',
            'car_type': 'economy',
            'seats': 4,
            'price_per_day': Decimal('30.00'),
            'features': ['AC', 'Manual', 'Radio', 'Airbags'],
            'is_available': True,
            'location': yangon,
            'description': 'Reliable economy car with manual transmission'
        },
        {
            'company': 'City Car Rental',
            'car_model': 'Suzuki Ertiga',
            'car_type': 'suv',
            'seats': 7,
            'price_per_day': Decimal('55.00'),
            'features': ['AC', 'Manual', 'MPV', 'Roof Rack'],
            'is_available': True,
            'location': yangon,
            'description': 'Compact MPV, great for small groups'
        },
        {
            'company': 'Premium Rentals',
            'car_model': 'BMW 5 Series',
            'car_type': 'luxury',
            'seats': 4,
            'price_per_day': Decimal('150.00'),
            'features': ['AC', 'GPS', 'Automatic', 'Premium Sound', 'Parking Sensors', 'Heated Seats'],
            'is_available': True,
            'location': yangon,
            'description': 'German luxury with excellent performance'
        },
        {
            'company': 'Budget Rentals',
            'car_model': 'Kia Picanto',
            'car_type': 'economy',
            'seats': 4,
            'price_per_day': Decimal('25.00'),
            'features': ['AC', 'Manual', 'Compact', 'Fuel Efficient'],
            'is_available': True,
            'location': yangon,
            'description': 'Most economical option for city driving'
        },
        {
            'company': 'Adventure Rentals',
            'car_model': 'Toyota Hilux',
            'car_type': 'suv',
            'seats': 5,
            'price_per_day': Decimal('75.00'),
            'features': ['AC', 'Manual', '4WD', 'Pickup Truck', 'Off-road Capable'],
            'is_available': True,
            'location': yangon,
            'description': 'Rugged pickup for adventure and off-road trips'
        },
        
        # Mandalay car rentals (6 cars)
        {
            'company': 'Mandalay Rent-a-Car',
            'car_model': 'Toyota Vios',
            'car_type': 'economy',
            'seats': 4,
            'price_per_day': Decimal('32.00'),
            'features': ['AC', 'Automatic', 'GPS', 'Airbags'],
            'is_available': True,
            'location': mandalay,
            'description': 'Reliable automatic car for Mandalay exploration'
        },
        {
            'company': 'Royal Mandalay Rentals',
            'car_model': 'Toyota Fortuner',
            'car_type': 'suv',
            'seats': 7,
            'price_per_day': Decimal('60.00'),
            'features': ['AC', 'Automatic', '4WD', 'Sunroof'],
            'is_available': True,
            'location': mandalay,
            'description': 'Comfortable SUV for Mandalay region trips'
        },
        {
            'company': 'Mandalay Luxury Cars',
            'car_model': 'Lexus RX',
            'car_type': 'luxury',
            'seats': 5,
            'price_per_day': Decimal('110.00'),
            'features': ['AC', 'Automatic', 'Premium Sound', 'Leather', 'Sunroof'],
            'is_available': True,
            'location': mandalay,
            'description': 'Luxury SUV for comfortable travel'
        },
        {
            'company': 'Budget Mandalay',
            'car_model': 'Suzuki Swift',
            'car_type': 'economy',
            'seats': 4,
            'price_per_day': Decimal('28.00'),
            'features': ['AC', 'Manual', 'Compact', 'Fuel Efficient'],
            'is_available': True,
            'location': mandalay,
            'description': 'Compact car perfect for Mandalay city'
        },
        {
            'company': 'Mandalay Rent-a-Car',
            'car_model': 'Honda CR-V',
            'car_type': 'suv',
            'seats': 5,
            'price_per_day': Decimal('58.00'),
            'features': ['AC', 'Automatic', 'GPS', 'Spacious'],
            'is_available': True,
            'location': mandalay,
            'description': 'Comfortable crossover SUV'
        },
        {
            'company': 'Royal Mandalay Rentals',
            'car_model': 'Mercedes C-Class',
            'car_type': 'luxury',
            'seats': 4,
            'price_per_day': Decimal('95.00'),
            'features': ['AC', 'Automatic', 'Premium Features', 'Comfortable'],
            'is_available': True,
            'location': mandalay,
            'description': 'Luxury sedan for business or pleasure'
        },
        
        # Bagan car rentals (5 cars)
        {
            'company': 'Bagan Car Rental',
            'car_model': 'Suzuki Ertiga',
            'car_type': 'suv',
            'seats': 7,
            'price_per_day': Decimal('55.00'),
            'features': ['AC', 'Manual', 'Roof Rack', 'Temple Pass Included'],
            'is_available': True,
            'location': bagan,
            'description': 'Perfect for temple hopping in Bagan'
        },
        {
            'company': 'Bagan Rentals',
            'car_model': 'Toyota Vios',
            'car_type': 'economy',
            'seats': 4,
            'price_per_day': Decimal('40.00'),
            'features': ['AC', 'Automatic', 'GPS with Temple Locations'],
            'is_available': True,
            'location': bagan,
            'description': 'Economy car with temple guide GPS'
        },
        {
            'company': 'Bagan Adventure',
            'car_model': 'Toyota Hilux',
            'car_type': 'suv',
            'seats': 5,
            'price_per_day': Decimal('70.00'),
            'features': ['AC', 'Manual', '4WD', 'Off-road', 'Sunset View Roof'],
            'is_available': True,
            'location': bagan,
            'description': '4x4 for off-road temple exploration'
        },
        {
            'company': 'Bagan Budget Rentals',
            'car_model': 'Kia Picanto',
            'car_type': 'economy',
            'seats': 4,
            'price_per_day': Decimal('30.00'),
            'features': ['AC', 'Manual', 'Compact', 'Bagan Map Included'],
            'is_available': True,
            'location': bagan,
            'description': 'Most economical option for Bagan'
        },
        {
            'company': 'Bagan Luxury',
            'car_model': 'Toyota Alphard',
            'car_type': 'luxury',
            'seats': 7,
            'price_per_day': Decimal('120.00'),
            'features': ['AC', 'Automatic', 'Premium Van', 'TV', 'Refreshments'],
            'is_available': True,
            'location': bagan,
            'description': 'Luxury van with driver for temple tours'
        },
        
        # Inle Lake car rentals (5 cars)
        {
            'company': 'Inle Lake Rentals',
            'car_model': 'Toyota Fortuner',
            'car_type': 'suv',
            'seats': 7,
            'price_per_day': Decimal('65.00'),
            'features': ['AC', 'Automatic', '4WD', 'Mountain Ready'],
            'is_available': True,
            'location': inle_lake,
            'description': 'SUV perfect for Shan State mountains'
        },
        {
            'company': 'Shan State Rentals',
            'car_model': 'Suzuki Carry Van',
            'car_type': 'van',
            'seats': 8,
            'price_per_day': Decimal('50.00'),
            'features': ['AC', 'Manual', 'Spacious', 'Group Travel'],
            'is_available': True,
            'location': inle_lake,
            'description': 'Van for group travel around Inle Lake'
        },
        {
            'company': 'Inle Budget Rentals',
            'car_model': 'Toyota Vios',
            'car_type': 'economy',
            'seats': 4,
            'price_per_day': Decimal('38.00'),
            'features': ['AC', 'Automatic', 'Hill Climbing', 'Efficient'],
            'is_available': True,
            'location': inle_lake,
            'description': 'Economy car for Inle Lake area'
        },
        {
            'company': 'Inle Luxury',
            'car_model': 'Lexus NX',
            'car_type': 'luxury',
            'seats': 5,
            'price_per_day': Decimal('105.00'),
            'features': ['AC', 'Automatic', 'Premium SUV', 'Comfort Features'],
            'is_available': True,
            'location': inle_lake,
            'description': 'Luxury SUV for comfortable Shan State travel'
        },
        {
            'company': 'Inle Adventure',
            'car_model': 'Mitsubishi Pajero',
            'car_type': 'suv',
            'seats': 7,
            'price_per_day': Decimal('75.00'),
            'features': ['AC', 'Manual', '4WD', 'Off-road', 'Roof Rack'],
            'is_available': True,
            'location': inle_lake,
            'description': 'Rugged 4x4 for mountain adventures'
        },
    ]
    
    for car_data in cars_data:
        car, created = CarRental.objects.get_or_create(
            company=car_data['company'],
            car_model=car_data['car_model'],
            location=car_data['location'],
            defaults={
                'car_type': car_data['car_type'],
                'seats': car_data['seats'],
                'price_per_day': car_data['price_per_day'],
                'features': car_data['features'],
                'is_available': car_data['is_available'],
                'description': car_data.get('description', ''),
            }
        )
        if created:
            print(f"  Created car: {car.company} - {car.car_model} in {car.location.name}")
    
    print(f"  Total cars: {CarRental.objects.count()}")
    
    print("\n=== DATA POPULATION COMPLETE ===")
    print(f"Summary:")
    print(f"  Users: {CustomUser.objects.count()}")
    print(f"  Destinations: {Destination.objects.count()}")
    print(f"  Hotels: {Hotel.objects.count()}")
    print(f"  Flights: {Flight.objects.count()}")
    print(f"  Buses: {BusService.objects.count()}")
    print(f"  Cars: {CarRental.objects.count()}")

if __name__ == "__main__":
    populate_all_data()