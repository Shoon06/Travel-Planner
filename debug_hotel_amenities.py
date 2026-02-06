# C:\Users\ASUS\MyanmarTravelPlanner\debug_hotel_amenities.py
import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models import Hotel, Destination
from django.db.models import Q

def debug_amenities_in_database():
    """Debug what amenities are actually in the database"""
    print("=" * 70)
    print("DEBUG: AMENITIES IN DATABASE")
    print("=" * 70)
    
    # Test with Yangon first
    destination = Destination.objects.filter(name='Yangon').first()
    if not destination:
        print("❌ No Yangon destination found")
        return
    
    hotels = Hotel.objects.filter(destination=destination, is_active=True)[:5]
    
    for hotel in hotels:
        print(f"\n🏨 {hotel.name}")
        print(f"   Amenities: {hotel.amenities}")
        print(f"   Type: {type(hotel.amenities)}")
        
        if hotel.amenities and isinstance(hotel.amenities, list):
            print("   Individual amenities:")
            for i, amenity in enumerate(hotel.amenities):
                print(f"     {i+1}. '{amenity}' (type: {type(amenity)})")

def test_amenities_filtering():
    """Test if amenities filtering works with Q queries"""
    print("\n" + "=" * 70)
    print("TESTING AMENITIES FILTERING WITH Q QUERIES")
    print("=" * 70)
    
    destination = Destination.objects.filter(name='Yangon').first()
    
    # Test different amenity formats
    test_amenities = [
        'wifi',
        'pool',
        'restaurant',
        'air_conditioning',
        'air conditioning',
        'Air Conditioning'
    ]
    
    for amenity in test_amenities:
        print(f"\n🔍 Testing amenity: '{amenity}'")
        
        hotels = Hotel.objects.filter(
            destination=destination,
            is_active=True
        )
        
        # Try different query methods
        count1 = hotels.filter(amenities__contains=amenity).count()
        count2 = hotels.filter(amenities__contains=[amenity]).count()
        count3 = hotels.filter(amenities__contains=amenity.lower()).count()
        count4 = hotels.filter(amenities__contains=[amenity.lower()]).count()
        count5 = hotels.filter(amenities__contains=amenity.replace(' ', '_')).count()
        
        print(f"   contains='{amenity}': {count1}")
        print(f"   contains=['{amenity}']: {count2}")
        print(f"   contains='{amenity.lower()}': {count3}")
        print(f"   contains=['{amenity.lower()}']: {count4}")
        print(f"   contains='{amenity.replace(' ', '_')}': {count5}")

def check_hotel_search():
    """Test hotel search functionality"""
    print("\n" + "=" * 70)
    print("TESTING HOTEL SEARCH")
    print("=" * 70)
    
    destination = Destination.objects.filter(name='Yangon').first()
    
    search_terms = ['hotel', 'royal', 's', 'yangon', 'HOTEL']
    
    for term in search_terms:
        print(f"\n🔍 Searching for: '{term}'")
        
        hotels = Hotel.objects.filter(
            destination=destination,
            is_active=True
        ).filter(
            Q(name__icontains=term) |
            Q(address__icontains=term)
        )
        
        print(f"   Found: {hotels.count()} hotels")
        if hotels.exists():
            for hotel in hotels[:3]:
                print(f"   - {hotel.name}")

if __name__ == '__main__':
    debug_amenities_in_database()
    test_amenities_filtering()
    check_hotel_search()