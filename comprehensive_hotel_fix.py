# C:\Users\ASUS\MyanmarTravelPlanner\comprehensive_hotel_fix.py
import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models import Hotel

def comprehensive_amenities_fix():
    """Comprehensive fix for all hotel amenities"""
    print("=" * 70)
    print("COMPREHENSIVE HOTEL AMENITIES FIX")
    print("=" * 70)
    
    hotels = Hotel.objects.all()
    total_hotels = hotels.count()
    fixed_count = 0
    
    # Common replacements
    replacements = {
        'air conditioning': 'air_conditioning',
        'air-conditioning': 'air_conditioning',
        'ac': 'air_conditioning',
        'a/c': 'air_conditioning',
        'room service': 'room_service',
        'room-service': 'room_service',
        'business center': 'business_center',
        'business-center': 'business_center',
        'fitness center': 'fitness',
        'fitness-center': 'fitness',
        'gym': 'fitness',
        'gym/fitness': 'fitness',
        'swimming pool': 'pool',
        'swimming-pool': 'pool',
        'pool swimming': 'pool',
        'spa': 'spa',
        'spa/massage': 'spa',
        'spa & massage': 'spa',
        'massage': 'spa',
        'wifi': 'wifi',
        'free wifi': 'wifi',
        'free-wifi': 'wifi',
        'wi-fi': 'wifi',
        'wi fi': 'wifi',
        'wifi/internet': 'wifi',
        'internet': 'wifi',
        'breakfast': 'breakfast',
        'breakfast included': 'breakfast',
        'free breakfast': 'breakfast',
        'breakfast-included': 'breakfast',
        'parking': 'parking',
        'free parking': 'parking',
        'car park': 'parking',
        'restaurant': 'restaurant',
        'dining': 'restaurant',
        'bar': 'bar',
        'lounge bar': 'bar',
        'laundry': 'laundry',
        'laundry service': 'laundry',
        'safe': 'safe',
        'safety deposit box': 'safe',
        'tv': 'tv',
        'television': 'tv',
        'flat screen tv': 'tv',
        'airport shuttle': 'airport_shuttle',
        'airport transfer': 'airport_shuttle',
        'concierge': 'concierge',
        '24-hour front desk': 'concierge',
    }
    
    for hotel in hotels:
        original_amenities = hotel.amenities
        new_amenities = []
        changed = False
        
        if original_amenities:
            # Convert to list if it's not already
            if isinstance(original_amenities, str):
                try:
                    # Try to parse JSON string
                    parsed = json.loads(original_amenities)
                    if isinstance(parsed, list):
                        amenity_list = parsed
                    else:
                        amenity_list = [original_amenities]
                except:
                    # If not JSON, treat as single amenity
                    amenity_list = [original_amenities]
            else:
                amenity_list = original_amenities
            
            # Process each amenity
            for amenity in amenity_list:
                if amenity:
                    # Convert to string
                    amenity_str = str(amenity).strip()
                    original_amenity = amenity_str
                    
                    # Convert to lowercase
                    amenity_str = amenity_str.lower()
                    
                    # Apply replacements
                    for old, new in replacements.items():
                        if amenity_str == old:
                            amenity_str = new
                            changed = True
                            break
                        elif old in amenity_str:
                            amenity_str = amenity_str.replace(old, new)
                            changed = True
                    
                    # Replace spaces with underscores
                    amenity_str = amenity_str.replace(' ', '_')
                    
                    # Remove multiple underscores
                    while '__' in amenity_str:
                        amenity_str = amenity_str.replace('__', '_')
                    
                    # Remove trailing/leading underscores
                    amenity_str = amenity_str.strip('_')
                    
                    # Add to new list if not empty and not duplicate
                    if amenity_str and amenity_str not in new_amenities:
                        new_amenities.append(amenity_str)
                    
                    if original_amenity != amenity_str:
                        changed = True
        
        # Update if changed
        if changed and new_amenities != original_amenities:
            hotel.amenities = new_amenities
            hotel.save()
            fixed_count += 1
            print(f"✅ Fixed: {hotel.name}")
            print(f"   Old: {original_amenities}")
            print(f"   New: {new_amenities}")
    
    print(f"\n✅ Fixed {fixed_count} out of {total_hotels} hotels")
    return fixed_count

def verify_fix():
    """Verify the fix worked"""
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    # Test a few hotels
    test_hotels = Hotel.objects.all()[:10]
    
    print("Sample of fixed hotels:")
    for hotel in test_hotels:
        print(f"\n🏨 {hotel.name}")
        print(f"   Amenities: {hotel.amenities}")
        
        if hotel.amenities and isinstance(hotel.amenities, list):
            print("   Contains 'wifi':", 'wifi' in hotel.amenities)
            print("   Contains 'pool':", 'pool' in hotel.amenities)
            print("   Contains 'air_conditioning':", 'air_conditioning' in hotel.amenities)
    
    # Count unique amenities
    all_amenities = set()
    for hotel in Hotel.objects.all():
        if hotel.amenities and isinstance(hotel.amenities, list):
            for amenity in hotel.amenities:
                all_amenities.add(amenity)
    
    print(f"\n📊 Total unique amenities: {len(all_amenities)}")
    print("Top 20 amenities:")
    for i, amenity in enumerate(sorted(list(all_amenities))[:20], 1):
        print(f"  {i:2}. {amenity}")

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("RUNNING COMPREHENSIVE HOTEL FIX")
    print("=" * 70)
    
    fixed = comprehensive_amenities_fix()
    verify_fix()
    
    print("\n" + "=" * 70)
    print(f"✅ FIX COMPLETED: {fixed} hotels updated")
    print("=" * 70)
    print("\n⚠ IMPORTANT: Restart your Django server after running this fix!")
    print("   Run: python manage.py runserver")