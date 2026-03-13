# C:\Users\ASUS\MyanmarTravelPlanner\enable_extra_beds.py

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models_room import Room, RoomType

def enable_extra_beds():
    print("="*60)
    print("ENABLING EXTRA BEDS FOR ALL ROOMS")
    print("="*60)
    
    # Get all rooms
    all_rooms = Room.objects.all()
    print(f"Total rooms found: {all_rooms.count()}")
    
    # Set extra bed prices based on room type and size
    updated_count = 0
    
    for room in all_rooms:
        # Determine if room can have extra bed based on room type
        if room.room_type.max_occupancy >= 3:
            # Larger rooms (Triple, Suite) can have extra beds
            room.extra_bed_available = True
            room.extra_bed_cost = 30000  # 30,000 MMK per night
            room.max_extra_beds = 1
            updated_count += 1
            print(f"✅ {room.room_number} ({room.room_type.name}) - Extra bed ENABLED: 30,000 MMK")
        
        elif room.room_type.max_occupancy == 2 and room.square_feet and room.square_feet > 350:
            # Larger double rooms can have extra beds
            room.extra_bed_available = True
            room.extra_bed_cost = 25000  # 25,000 MMK per night
            room.max_extra_beds = 1
            updated_count += 1
            print(f"✅ {room.room_number} ({room.room_type.name}) - Extra bed ENABLED: 25,000 MMK")
        
        elif room.room_type.name == 'Suite':
            # Suites can have multiple extra beds
            room.extra_bed_available = True
            room.extra_bed_cost = 40000  # 40,000 MMK per night
            room.max_extra_beds = 2
            updated_count += 1
            print(f"✅ {room.room_number} ({room.room_type.name}) - Extra bed ENABLED: 40,000 MMK (max 2)")
        
        else:
            # Smaller rooms - no extra bed
            room.extra_bed_available = False
            room.extra_bed_cost = 0
            room.max_extra_beds = 0
            print(f"ℹ️ {room.room_number} ({room.room_type.name}) - No extra bed (room too small)")
        
        room.save()
    
    print("\n" + "="*60)
    print(f"✅ Updated {updated_count} rooms with extra beds enabled")
    print("="*60)
    
    # Verify the updates
    print("\nVERIFYING UPDATES:")
    rooms_with_extra = Room.objects.filter(extra_bed_available=True)
    print(f"Rooms with extra beds now: {rooms_with_extra.count()}")
    
    # Group by room type
    print("\nBreakdown by room type:")
    for room_type in RoomType.objects.all():
        count = rooms_with_extra.filter(room_type=room_type).count()
        if count > 0:
            print(f"  - {room_type.name}: {count} rooms")

if __name__ == "__main__":
    enable_extra_beds()