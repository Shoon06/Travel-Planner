# C:\Users\ASUS\MyanmarTravelPlanner\link_taunggyi_places.py

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Destination

def link_taunggyi_places():
    print("=" * 60)
    print("LINKING PLACES TO TAUNGGYI")
    print("=" * 60)
    
    # Get Taunggyi
    try:
        taunggyi = Destination.objects.get(name='Taunggyi')
        print(f"\n✅ Found Taunggyi (ID: {taunggyi.id})")
    except Destination.DoesNotExist:
        print("\n❌ Taunggyi not found! Please add Taunggyi to database first.")
        return
    
    # Mark Taunggyi as a region
    if hasattr(taunggyi, 'is_region'):
        taunggyi.is_region = True
        taunggyi.save()
        print(f"✅ Marked Taunggyi as region")
    
    # List of places that should be in Taunggyi
    places_to_link = [
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
    print("LINKING PLACES")
    print("=" * 60)
    
    linked = 0
    not_found = 0
    
    for place_name in places_to_link:
        try:
            place = Destination.objects.get(name=place_name)
            place.parent = taunggyi
            place.save()
            print(f"✅ Linked: {place_name} → Taunggyi")
            linked += 1
        except Destination.DoesNotExist:
            print(f"❌ Not found: {place_name}")
            not_found += 1
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {linked} places linked, {not_found} not found")
    print("=" * 60)
    
    # Show what's now linked to Taunggyi
    print("\n" + "=" * 60)
    print("PLACES NOW IN TAUNGGYI")
    print("=" * 60)
    
    places_in_taunggyi = Destination.objects.filter(parent=taunggyi)
    for place in places_in_taunggyi:
        print(f"📍 {place.name}")

if __name__ == "__main__":
    link_taunggyi_places()