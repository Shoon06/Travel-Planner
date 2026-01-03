# C:\Users\ASUS\MyanmarTravelPlanner\populate_airport_info.py
import os
import sys
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Destination
from planner.airport_data import AIRPORT_DATA, get_airport_info

def update_destinations_with_airports():
    print("=== UPDATING DESTINATIONS WITH AIRPORT INFORMATION ===")
    
    updated_count = 0
    airports_added = 0
    
    # Update existing destinations
    for destination in Destination.objects.all():
        airport_info = get_airport_info(destination.name)
        
        if airport_info:
            # Create a separate airport destination entry
            airport_name = airport_info['airport_name']
            
            # Check if airport destination already exists
            airport_dest, created = Destination.objects.get_or_create(
                name=airport_name,
                defaults={
                    'region': destination.region,
                    'type': 'airport',
                    'latitude': Decimal(str(airport_info.get('latitude', 0))),
                    'longitude': Decimal(str(airport_info.get('longitude', 0))),
                    'description': f"Airport serving {destination.name} ({airport_info['iata_code']}) - {airport_info['airport_type']} Airport",
                    'is_active': True
                }
            )
            
            if created:
                airports_added += 1
                print(f"✓ Created airport destination: {airport_name}")
            
            # Update the city destination description to mention airport
            if airport_info['iata_code'] not in destination.description:
                destination.description += f" Has {airport_info['airport_type'].lower()} airport ({airport_info['iata_code']})."
                destination.save()
                updated_count += 1
                print(f"↻ Updated: {destination.name} - Added airport info")
    
    print(f"\n=== SUMMARY ===")
    print(f"Updated {updated_count} destinations with airport information")
    print(f"Added {airports_added} airport destinations")
    
    # List destinations with airports
    print("\nDestinations with airports:")
    for city, data in AIRPORT_DATA.items():
        print(f"  • {city}: {data['airport_name']} ({data['iata_code']}) - {data['airport_type']}")

if __name__ == "__main__":
    update_destinations_with_airports()