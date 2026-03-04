import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Hotel, Destination

def add_coordinates_to_hotels():
    """Add coordinates to hotels that don't have them"""
    
    # Destination coordinates map
    destination_coords = {
        'Yangon': (16.8409, 96.1735),
        'Mandalay': (21.9750, 96.0833),
        'Bagan': (21.1722, 94.8603),
        'Inle Lake': (20.5500, 96.9167),
        'Ngapali Beach': (18.4492, 94.3267),
        'Naypyidaw': (19.7475, 96.1150),
        'Pyin Oo Lwin': (22.0333, 96.4667),
        'Hpa-An': (16.8833, 97.6333),
        'Kalaw': (20.6333, 96.5667),
    }
    
    hotels_without_coords = Hotel.objects.filter(latitude__isnull=True, longitude__isnull=True)
    print(f"Found {hotels_without_coords.count()} hotels without coordinates")
    
    updated_count = 0
    for hotel in hotels_without_coords:
        destination_name = hotel.destination.name
        
        if destination_name in destination_coords:
            lat, lng = destination_coords[destination_name]
            # Add small random offset so markers don't overlap exactly
            import random
            lat_offset = random.uniform(-0.005, 0.005)
            lng_offset = random.uniform(-0.005, 0.005)
            
            hotel.latitude = lat + lat_offset
            hotel.longitude = lng + lng_offset
            hotel.save()
            updated_count += 1
            print(f"Added coordinates to {hotel.name}: {hotel.latitude}, {hotel.longitude}")
    
    print(f"Updated {updated_count} hotels with coordinates")

if __name__ == "__main__":
    add_coordinates_to_hotels()