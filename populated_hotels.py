# C:\Users\ASUS\MyanmarTravelPlanner\populate_hotels.py
import os
import sys
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Destination, Hotel

def populate_hotels():
    print("Populating hotels...")
    
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
        {
            "name": "The Strand Yangon",
            "destination": yangon,
            "address": "92 Strand Road, Yangon",
            "price_per_night": Decimal("250.00"),
            "category": "luxury",
            "amenities": ["wifi", "pool", "spa", "fine dining", "butler service"],
            "rating": Decimal("4.9"),
            "review_count": 956
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
        {
            "name": "Mandalay City Hotel",
            "destination": mandalay,
            "address": "26th Street, Mandalay",
            "price_per_night": Decimal("45.00"),
            "category": "budget",
            "amenities": ["wifi", "restaurant", "city center"],
            "rating": Decimal("4.1"),
            "review_count": 321
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
        {
            "name": "Bagan Thande Hotel",
            "destination": bagan,
            "address": "Old Bagan, Near Bu Pagoda",
            "price_per_night": Decimal("60.00"),
            "category": "budget",
            "amenities": ["wifi", "garden", "restaurant", "river view"],
            "rating": Decimal("4.3"),
            "review_count": 456
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
        {
            "name": "Inle Inn",
            "destination": inle_lake,
            "address": "Yone Gyi Road, Nyaung Shwe",
            "price_per_night": Decimal("40.00"),
            "category": "budget",
            "amenities": ["wifi", "restaurant", "bicycle rental", "garden"],
            "rating": Decimal("4.2"),
            "review_count": 234
        }
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
            print(f"Created hotel: {hotel.name} in {hotel.destination.name}")
        else:
            print(f"Updated hotel: {hotel.name}")
    
    print(f"Total hotels: {Hotel.objects.count()}")

if __name__ == "__main__":
    populate_hotels()