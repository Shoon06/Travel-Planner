# C:\Users\ASUS\MyanmarTravelPlanner\enable_extra_beds_final.py

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models_room import Room, RoomType

def enable_extra_beds_final():
    print("="*60)
    print("ENABLING EXTRA BEDS FOR ALL ROOMS (FINAL VERSION)")
    print("="*60)
    
    # Get all rooms
    all_rooms = Room.objects.all()
    print(f"Total rooms found: {all_rooms.count()}")
    
    updated_count = 0
    
    for room in all_rooms:
        # Enable extra beds for ALL rooms with appropriate pricing
        room.extra_bed_available = True
        
        # Set different prices based on room type
        if room.room_type.name == 'Suite':
            room.extra_bed_cost = 50000  # 50,000 MMK for suites
            room.max_extra_beds = 2
            print(f"✅ {room.room_number} (Suite) - Extra bed: 50,000 MMK (max 2)")
        
        elif room.room_type.name == 'Triple':
            room.extra_bed_cost = 40000  # 40,000 MMK for triple
            room.max_extra_beds = 1
            print(f"✅ {room.room_number} (Triple) - Extra bed: 40,000 MMK")
        
        elif room.room_type.name == 'Double':
            room.extra_bed_cost = 35000  # 35,000 MMK for double
            room.max_extra_beds = 1
            print(f"✅ {room.room_number} (Double) - Extra bed: 35,000 MMK")
        
        else:  # Single and others
            room.extra_bed_cost = 25000  # 25,000 MMK for single
            room.max_extra_beds = 1
            print(f"✅ {room.room_number} (Single) - Extra bed: 25,000 MMK")
        
        room.save()
        updated_count += 1
    
    print("\n" + "="*60)
    print(f"✅ Successfully enabled extra beds for ALL {updated_count} rooms")
    print("="*60)
    
    # Verify the updates
    print("\nVERIFYING UPDATES:")
    rooms_with_extra = Room.objects.filter(extra_bed_available=True)
    print(f"Rooms with extra beds now: {rooms_with_extra.count()}")
    
    # Show sample
    print("\nSample rooms:")
    for room in rooms_with_extra[:10]:
        print(f"  - {room.room_number} ({room.room_type.name}): {room.extra_bed_cost} MMK")

if __name__ == "__main__":
    enable_extra_beds_final()