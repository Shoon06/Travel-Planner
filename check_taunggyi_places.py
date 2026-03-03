# C:\Users\ASUS\MyanmarTravelPlanner\check_taunggyi_places.py

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Destination

def check_taunggyi_places():
    print("=" * 60)
    print("CHECKING TAUNGGYI AND ITS PLACES")
    print("=" * 60)
    
    # Check if Taunggyi exists
    try:
        taunggyi = Destination.objects.get(name='Taunggyi')
        print(f"\n✅ Taunggyi found:")
        print(f"   ID: {taunggyi.id}")
        print(f"   Name: {taunggyi.name}")
        print(f"   Type: {taunggyi.type}")
        print(f"   Region: {taunggyi.region}")
        print(f"   is_region: {taunggyi.is_region if hasattr(taunggyi, 'is_region') else 'Field missing'}")
        print(f"   Parent: {taunggyi.parent.name if taunggyi.parent else 'None'}")
    except Destination.DoesNotExist:
        print("\n❌ Taunggyi not found in database!")
        return
    
    # Check all places that should be in Taunggyi
    taunggyi_places = [
        'Kakku Pagodas',
        'Shwe Bone Pwint Pagoda',
        'Nga Phe Chaung Monastery',
        'Htem Sann Cave',
        'Kyaung Daw Pagoda',
        'Main Ma Ye Tha Khin Ma Mountain',
        'Sulamuni Lawka Chanthar Pagoda',
        'Floating Market',
        'Inle Lake',
        'Phaug Daw Oo Pagoda',
    ]
    
    print("\n" + "=" * 60)
    print("CHECKING PLACES THAT SHOULD BE IN TAUNGGYI")
    print("=" * 60)
    
    found_places = []
    missing_places = []
    
    for place_name in taunggyi_places:
        try:
            place = Destination.objects.get(name=place_name)
            found_places.append(place)
            print(f"\n📍 {place_name}:")
            print(f"   ID: {place.id}")
            print(f"   Type: {place.type}")
            print(f"   Current Parent: {place.parent.name if place.parent else 'None'}")
            print(f"   Region field: {place.region}")
        except Destination.DoesNotExist:
            missing_places.append(place_name)
            print(f"\n❌ {place_name}: NOT FOUND in database")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total places found: {len(found_places)}")
    print(f"Total places missing: {len(missing_places)}")
    
    if missing_places:
        print("\nMissing places you need to add to database:")
        for place in missing_places:
            print(f"  - {place}")

if __name__ == "__main__":
    check_taunggyi_places()