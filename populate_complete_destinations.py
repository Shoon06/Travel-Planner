# C:\Users\ASUS\MyanmarTravelPlanner\populate_complete_destinations.py
import os
import sys
import django
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Destination

# COMPLETE Myanmar Destinations with Coordinates
MYANMAR_DESTINATIONS = [
    # States (7 States)
    {"name": "Kachin State", "region": "Northern Myanmar", "type": "state", 
     "latitude": 25.8500, "longitude": 97.3833, "description": "Northernmost state known for jade mines, mountains, and Myitsone confluence."},
    {"name": "Chin State", "region": "Western Myanmar", "type": "state", 
     "latitude": 22.0000, "longitude": 93.5000, "description": "Mountainous western state famous for tribal cultures and Mount Victoria."},
    {"name": "Kayah State", "region": "Eastern Myanmar", "type": "state", 
     "latitude": 19.2500, "longitude": 97.5000, "description": "Smallest state known for Padaung (long-neck) women and scenic landscapes."},
    {"name": "Kayin State", "region": "Southeastern Myanmar", "type": "state", 
     "latitude": 17.0000, "longitude": 97.7500, "description": "Known for limestone mountains, caves, and the Thanlwin River."},
    {"name": "Mon State", "region": "Southern Myanmar", "type": "state", 
     "latitude": 16.5000, "longitude": 97.5000, "description": "Coastal state famous for Golden Rock (Kyaiktiyo) pagoda and beaches."},
    {"name": "Rakhine State", "region": "Western Myanmar", "type": "state", 
     "latitude": 19.5000, "longitude": 93.5000, "description": "Western coastal state with Ngapali Beach and ancient Mrauk-U."},
    {"name": "Shan State", "region": "Eastern Myanmar", "type": "state", 
     "latitude": 21.0000, "longitude": 98.0000, "description": "Largest state known for Inle Lake, hill tribes, and tea plantations."},
    
    # Regions (7 Regions)
    {"name": "Sagaing Region", "region": "Northern Myanmar", "type": "region", 
     "latitude": 21.8833, "longitude": 95.9667, "description": "Second largest region with ancient cities like Monywa and Shwebo."},
    {"name": "Mandalay Region", "region": "Central Myanmar", "type": "region", 
     "latitude": 21.9750, "longitude": 96.0833, "description": "Cultural heart of Myanmar with ancient capitals and Mandalay city."},
    {"name": "Magway Region", "region": "Central Myanmar", "type": "region", 
     "latitude": 20.1500, "longitude": 94.9500, "description": "Known for oil fields, Thanakha trees, and Magway city."},
    {"name": "Bago Region", "region": "Lower Myanmar", "type": "region", 
     "latitude": 17.3333, "longitude": 96.4833, "description": "Historic region with ancient capital Bago and Shwemawdaw Pagoda."},
    {"name": "Yangon Region", "region": "Lower Myanmar", "type": "region", 
     "latitude": 16.8409, "longitude": 96.1735, "description": "Commercial capital with Shwedagon Pagoda and colonial architecture."},
    {"name": "Ayeyarwady Region", "region": "Lower Myanmar", "type": "region", 
     "latitude": 16.8333, "longitude": 95.1667, "description": "Delta region known for rice cultivation and beaches like Ngwe Saung."},
    {"name": "Tanintharyi Region", "region": "Southern Myanmar", "type": "region", 
     "latitude": 13.0000, "longitude": 98.7500, "description": "Southernmost region with Myeik Archipelago and Dawei city."},
    
    # Union Territory
    {"name": "Naypyidaw", "region": "Central Myanmar", "type": "union_territory", 
     "latitude": 19.7475, "longitude": 96.1150, "description": "Capital city of Myanmar since 2005, known for its wide roads and government buildings."},
    
    # Major Cities (25+ cities)
    {"name": "Yangon", "region": "Yangon Region", "type": "city", 
     "latitude": 16.8409, "longitude": 96.1735, "description": "Largest city and former capital, famous for Shwedagon Pagoda."},
    {"name": "Mandalay", "region": "Mandalay Region", "type": "city", 
     "latitude": 21.9750, "longitude": 96.0833, "description": "Second largest city, cultural capital of Myanmar."},
    {"name": "Naypyidaw", "region": "Naypyidaw", "type": "city", 
     "latitude": 19.7475, "longitude": 96.1150, "description": "Capital city of Myanmar."},
    {"name": "Bagan", "region": "Mandalay Region", "type": "city", 
     "latitude": 21.1722, "longitude": 94.8603, "description": "Ancient city with thousands of Buddhist temples."},
    {"name": "Mawlamyine", "region": "Mon State", "type": "city", 
     "latitude": 16.4800, "longitude": 97.6300, "description": "Third largest city and former British colonial capital."},
    {"name": "Taunggyi", "region": "Shan State", "type": "city", 
     "latitude": 20.7833, "longitude": 97.0333, "description": "Capital of Shan State, known for its floating balloon festival."},
    {"name": "Monywa", "region": "Sagaing Region", "type": "city", 
     "latitude": 22.1167, "longitude": 95.1333, "description": "Major city in Sagaing Region, known for Thanboddhay Pagoda."},
    {"name": "Pyay", "region": "Bago Region", "type": "city", 
     "latitude": 18.8167, "longitude": 95.2167, "description": "Ancient Pyu city with Sri Ksetra archaeological site."},
    {"name": "Sittwe", "region": "Rakhine State", "type": "city", 
     "latitude": 20.1500, "longitude": 92.9000, "description": "Capital of Rakhine State, port city on Bay of Bengal."},
    {"name": "Myitkyina", "region": "Kachin State", "type": "city", 
     "latitude": 25.3833, "longitude": 97.4000, "description": "Capital of Kachin State, near Myitsone confluence."},
    {"name": "Pathein", "region": "Ayeyarwady Region", "type": "city", 
     "latitude": 16.7833, "longitude": 94.7333, "description": "Capital of Ayeyarwady Region, famous for umbrellas."},
    {"name": "Magway", "region": "Magway Region", "type": "city", 
     "latitude": 20.1500, "longitude": 94.9500, "description": "Capital of Magway Region, center of oil industry."},
    {"name": "Pakokku", "region": "Magway Region", "type": "city", 
     "latitude": 21.3333, "longitude": 95.0833, "description": "Important river port on the Irrawaddy River."},
    {"name": "Hakha", "region": "Chin State", "type": "city", 
     "latitude": 22.6500, "longitude": 93.6167, "description": "Capital of Chin State in the mountains."},
    {"name": "Loikaw", "region": "Kayah State", "type": "city", 
     "latitude": 19.6667, "longitude": 97.2167, "description": "Capital of Kayah State, known for Padaung tribe."},
    {"name": "Dawei", "region": "Tanintharyi Region", "type": "city", 
     "latitude": 14.0833, "longitude": 98.2000, "description": "Capital of Tanintharyi Region, southern port city."},
    {"name": "Myeik", "region": "Tanintharyi Region", "type": "city", 
     "latitude": 12.4333, "longitude": 98.6000, "description": "Port city in the Myeik Archipelago, known for pearls."},
    {"name": "Shwebo", "region": "Sagaing Region", "type": "city", 
     "latitude": 22.5667, "longitude": 95.7000, "description": "Historical capital of Konbaung Dynasty."},
    {"name": "Kalay", "region": "Sagaing Region", "type": "city", 
     "latitude": 23.1833, "longitude": 94.0500, "description": "Town in Sagaing Region near Indian border."},
    {"name": "Meiktila", "region": "Mandalay Region", "type": "city", 
     "latitude": 20.8833, "longitude": 95.8833, "description": "Important city in central Myanmar with a large lake."},
    {"name": "Pyin Oo Lwin", "region": "Mandalay Region", "type": "town", 
     "latitude": 22.0333, "longitude": 96.4667, "description": "Hill station known for colonial architecture and flowers."},
    {"name": "Hsipaw", "region": "Shan State", "type": "town", 
     "latitude": 22.6333, "longitude": 97.2833, "description": "Shan town known for trekking and Shan Palace."},
    {"name": "Kalaw", "region": "Shan State", "type": "town", 
     "latitude": 20.6333, "longitude": 96.5667, "description": "Hill station popular for trekking to Inle Lake."},
    {"name": "Hpa-An", "region": "Kayin State", "type": "town", 
     "latitude": 16.8833, "longitude": 97.6333, "description": "Capital of Kayin State with limestone caves."},
    
    # Popular Attractions
    {"name": "Inle Lake", "region": "Shan State", "type": "attraction", 
     "latitude": 20.5500, "longitude": 96.9167, "description": "Freshwater lake famous for leg-rowing fishermen and floating villages."},
    {"name": "Ngapali Beach", "region": "Rakhine State", "type": "attraction", 
     "latitude": 18.4500, "longitude": 94.3333, "description": "Pristine beach on Bay of Bengal with luxury resorts."},
    {"name": "Ngwe Saung Beach", "region": "Ayeyarwady Region", "type": "attraction", 
     "latitude": 16.6667, "longitude": 94.5667, "description": "Beautiful beach with white sand and clear water."},
    {"name": "Kyaiktiyo Pagoda", "region": "Mon State", "type": "attraction", 
     "latitude": 17.4819, "longitude": 97.0967, "description": "Golden Rock pagoda balancing on cliff edge."},
    {"name": "U Bein Bridge", "region": "Mandalay Region", "type": "attraction", 
     "latitude": 21.8700, "longitude": 96.0550, "description": "Longest teakwood bridge in the world."},
    {"name": "Shwedagon Pagoda", "region": "Yangon Region", "type": "attraction", 
     "latitude": 16.7983, "longitude": 96.1494, "description": "Most sacred Buddhist pagoda in Myanmar."},
    {"name": "Mount Popa", "region": "Mandalay Region", "type": "attraction", 
     "latitude": 20.9172, "longitude": 95.2500, "description": "Volcanic peak with monastery on top."},
    {"name": "Mrauk U", "region": "Rakhine State", "type": "attraction", 
     "latitude": 20.5967, "longitude": 93.1928, "description": "Ancient capital with hundreds of temples."},
    {"name": "Pindaya Caves", "region": "Shan State", "type": "attraction", 
     "latitude": 20.9500, "longitude": 96.6667, "description": "Limestone caves with thousands of Buddha images."},
    {"name": "Chaung Tha Beach", "region": "Ayeyarwady Region", "type": "attraction", 
     "latitude": 16.4667, "longitude": 94.3333, "description": "Popular beach destination near Pathein."},
    
    # Major Airports (as departure points)
    {"name": "Yangon International Airport", "region": "Yangon Region", "type": "airport", 
     "latitude": 16.9073, "longitude": 96.1332, "description": "Main international airport of Myanmar."},
    {"name": "Mandalay International Airport", "region": "Mandalay Region", "type": "airport", 
     "latitude": 21.7022, "longitude": 95.9792, "description": "Second largest airport in Myanmar."},
    {"name": "Naypyidaw International Airport", "region": "Naypyidaw", "type": "airport", 
     "latitude": 19.6235, "longitude": 96.2010, "description": "Capital city's international airport."},
    {"name": "Heho Airport", "region": "Shan State", "type": "airport", 
     "latitude": 20.7470, "longitude": 96.7920, "description": "Gateway to Inle Lake and Shan State."},
    {"name": "Nyaung U Airport", "region": "Mandalay Region", "type": "airport", 
     "latitude": 21.1788, "longitude": 94.9302, "description": "Gateway to Bagan temples."},
    {"name": "Thandwe Airport", "region": "Rakhine State", "type": "airport", 
     "latitude": 18.4608, "longitude": 94.3001, "description": "Gateway to Ngapali Beach."},
]

def populate_complete_destinations():
    print("=== POPULATING COMPLETE MYANMAR DESTINATIONS ===")
    created_count = 0
    updated_count = 0
    
    for dest_data in MYANMAR_DESTINATIONS:
        dest, created = Destination.objects.update_or_create(
            name=dest_data["name"],
            defaults={
                "region": dest_data["region"],
                "type": dest_data["type"],
                "latitude": Decimal(str(dest_data["latitude"])),
                "longitude": Decimal(str(dest_data["longitude"])),
                "description": dest_data["description"],
                "is_active": True
            }
        )
        
        if created:
            created_count += 1
            print(f"✓ Created: {dest.name} ({dest.type}) - {dest.region}")
        else:
            updated_count += 1
            print(f"↻ Updated: {dest.name}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total destinations in database: {Destination.objects.count()}")
    print(f"Newly created: {created_count}")
    print(f"Updated: {updated_count}")
    
    # Print breakdown by type
    print("\nBreakdown by type:")
    types = Destination.objects.values_list('type', flat=True).distinct()
    for type_val in types:
        count = Destination.objects.filter(type=type_val).count()
        print(f"  {type_val.title()}: {count}")
    
    # Print some sample destinations
    print("\nSample destinations:")
    samples = Destination.objects.order_by('?')[:5]
    for sample in samples:
        print(f"  • {sample.name} ({sample.region}) - {sample.type}")

if __name__ == "__main__":
    populate_complete_destinations()