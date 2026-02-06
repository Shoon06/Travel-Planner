# C:\Users\ASUS\MyanmarTravelPlanner\fix_hotel_amenities.py
import os
import sys
import django
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models import Hotel

def normalize_amenities():
    """Convert amenities to lowercase with underscores for consistent filtering"""
    print("=" * 70)
    print("NORMALIZING HOTEL AMENITIES FOR FILTERING")
    print("=" * 70)
    
    hotels = Hotel.objects.all()
    updated_count = 0
    
    for hotel in hotels:
        if hotel.amenities:
            normalized = []
            needs_update = False
            
            # Debug current state
            current_amenities = hotel.amenities
            
            if isinstance(current_amenities, list):
                for amenity in current_amenities:
                    if amenity:
                        # Convert to string, trim whitespace
                        amenity_str = str(amenity).strip()
                        
                        # Store original for comparison
                        original = amenity_str
                        
                        # Convert to lowercase
                        amenity_str = amenity_str.lower()
                        
                        # Replace spaces with underscores
                        amenity_str = amenity_str.replace(' ', '_')
                        
                        # Replace multiple underscores with single
                        while '__' in amenity_str:
                            amenity_str = amenity_str.replace('__', '_')
                        
                        # Remove any trailing/leading underscores
                        amenity_str = amenity_str.strip('_')
                        
                        normalized.append(amenity_str)
                        
                        # Check if we need to update
                        if original != amenity_str:
                            needs_update = True
            
            # Update only if changed
            if normalized and needs_update:
                hotel.amenities = normalized
                hotel.save()
                updated_count += 1
                print(f"✅ Updated: {hotel.name}")
                print(f"   Old: {current_amenities}")
                print(f"   New: {normalized}")
            elif not hotel.amenities or not isinstance(hotel.amenities, list):
                # Handle non-list or empty amenities
                hotel.amenities = []
                hotel.save()
                updated_count += 1
                print(f"⚠ Fixed: {hotel.name} (was {type(current_amenities)})")
    
    print(f"\n✅ Normalized {updated_count} hotels' amenities")
    return updated_count

def create_amenities_lookup():
    """Create a lookup table of all unique amenities for debugging"""
    print("\n" + "=" * 70)
    print("CREATING AMENITIES LOOKUP TABLE")
    print("=" * 70)
    
    all_amenities = set()
    hotels = Hotel.objects.all()
    
    for hotel in hotels:
        if hotel.amenities and isinstance(hotel.amenities, list):
            for amenity in hotel.amenities:
                if amenity and isinstance(amenity, str):
                    all_amenities.add(amenity)
    
    # Sort and save to file
    sorted_amenities = sorted(list(all_amenities))
    
    with open('amenities_lookup.txt', 'w', encoding='utf-8') as f:
        f.write("ALL UNIQUE AMENITIES IN DATABASE:\n")
        f.write("=" * 50 + "\n")
        for i, amenity in enumerate(sorted_amenities, 1):
            f.write(f"{i:3}. {amenity}\n")
        
        # Also group by first letter for easier reading
        f.write("\n\nAMENITIES GROUPED BY FIRST LETTER:\n")
        f.write("=" * 50 + "\n")
        
        amenities_by_letter = {}
        for amenity in sorted_amenities:
            first_letter = amenity[0].upper() if amenity else '?'
            if first_letter not in amenities_by_letter:
                amenities_by_letter[first_letter] = []
            amenities_by_letter[first_letter].append(amenity)
        
        for letter in sorted(amenities_by_letter.keys()):
            f.write(f"\n{letter}:\n")
            f.write("-" * 20 + "\n")
            for amenity in sorted(amenities_by_letter[letter]):
                f.write(f"  • {amenity}\n")
    
    print(f"✅ Found {len(sorted_amenities)} unique amenities")
    print(f"✅ Saved to 'amenities_lookup.txt'")
    return sorted_amenities

def check_amenities_statistics():
    """Show statistics about amenities"""
    print("\n" + "=" * 70)
    print("AMENITIES STATISTICS")
    print("=" * 70)
    
    hotels = Hotel.objects.all()
    total_hotels = hotels.count()
    hotels_with_amenities = hotels.exclude(amenities=[]).count()
    
    print(f"Total hotels: {total_hotels}")
    print(f"Hotels with amenities: {hotels_with_amenities}")
    print(f"Hotels without amenities: {total_hotels - hotels_with_amenities}")
    
    # Count amenities per hotel
    amenities_counts = []
    for hotel in hotels:
        if hotel.amenities and isinstance(hotel.amenities, list):
            amenities_counts.append(len(hotel.amenities))
    
    if amenities_counts:
        print(f"\nAmenities per hotel:")
        print(f"  Average: {sum(amenities_counts)/len(amenities_counts):.1f}")
        print(f"  Min: {min(amenities_counts)}")
        print(f"  Max: {max(amenities_counts)}")
        
        # Show most common amenities
        all_amenities_list = []
        for hotel in hotels:
            if hotel.amenities and isinstance(hotel.amenities, list):
                all_amenities_list.extend(hotel.amenities)
        
        from collections import Counter
        most_common = Counter(all_amenities_list).most_common(10)
        
        print(f"\nTop 10 most common amenities:")
        for amenity, count in most_common:
            percentage = (count / hotels_with_amenities) * 100
            print(f"  {amenity}: {count} hotels ({percentage:.1f}%)")

def fix_specific_amenities():
    """Fix specific common amenity names"""
    print("\n" + "=" * 70)
    print("FIXING SPECIFIC AMENITY NAMES")
    print("=" * 70)
    
    # Common fixes
    replacements = {
        'air conditioning': 'air_conditioning',
        'air-conditioning': 'air_conditioning',
        'ac': 'air_conditioning',
        'room service': 'room_service',
        'room-service': 'room_service',
        'business center': 'business_center',
        'business-center': 'business_center',
        'fitness center': 'fitness_center',
        'fitness-center': 'fitness_center',
        'gym/fitness': 'fitness_center',
        'swimming pool': 'pool',
        'swimming-pool': 'pool',
        'spa/massage': 'spa',
        'spa & massage': 'spa',
        'free wifi': 'wifi',
        'free-wifi': 'wifi',
        'wi-fi': 'wifi',
        'wi fi': 'wifi',
        'wifi/internet': 'wifi',
        'breakfast included': 'breakfast',
        'free breakfast': 'breakfast',
        'breakfast-included': 'breakfast',
    }
    
    hotels = Hotel.objects.all()
    updated_count = 0
    
    for hotel in hotels:
        if hotel.amenities and isinstance(hotel.amenities, list):
            updated_amenities = []
            changed = False
            
            for amenity in hotel.amenities:
                if amenity and isinstance(amenity, str):
                    original = amenity
                    
                    # Apply replacements
                    for old, new in replacements.items():
                        if amenity == old:
                            amenity = new
                            changed = True
                        elif amenity.startswith(old + ' ') or amenity.endswith(' ' + old):
                            amenity = amenity.replace(old, new)
                            changed = True
                    
                    updated_amenities.append(amenity)
                    
                    if original != amenity:
                        print(f"   Fixed '{original}' -> '{amenity}' in {hotel.name}")
            
            if changed:
                hotel.amenities = updated_amenities
                hotel.save()
                updated_count += 1
    
    print(f"\n✅ Fixed {updated_count} hotels' specific amenities")
    return updated_count

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("HOTEL AMENITIES FIXER")
    print("=" * 70)
    
    # Run all fixes
    fix_specific_amenities()
    normalize_amenities()
    check_amenities_statistics()
    create_amenities_lookup()
    
    print("\n" + "=" * 70)
    print("✅ ALL FIXES COMPLETED SUCCESSFULLY!")
    print("=" * 70)