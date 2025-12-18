import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Destination

MYANMAR_PLACES = [
    # States and Regions
    {'name': 'Yangon', 'type': 'region', 'region': 'Lower Myanmar'},
    {'name': 'Mandalay', 'type': 'region', 'region': 'Central Myanmar'},
    {'name': 'Bago', 'type': 'region', 'region': 'Lower Myanmar'},
    {'name': 'Magway', 'type': 'region', 'region': 'Central Myanmar'},
    {'name': 'Sagaing', 'type': 'region', 'region': 'Northern Myanmar'},
    {'name': 'Tanintharyi', 'type': 'region', 'region': 'Southern Myanmar'},
    {'name': 'Ayeyarwady', 'type': 'region', 'region': 'Lower Myanmar'},
    {'name': 'Kachin', 'type': 'state', 'region': 'Northern Myanmar'},
    {'name': 'Kayah', 'type': 'state', 'region': 'Eastern Myanmar'},
    {'name': 'Kayin', 'type': 'state', 'region': 'Southeastern Myanmar'},
    {'name': 'Chin', 'type': 'state', 'region': 'Western Myanmar'},
    {'name': 'Mon', 'type': 'state', 'region': 'Southern Myanmar'},
    {'name': 'Rakhine', 'type': 'state', 'region': 'Western Myanmar'},
    {'name': 'Shan', 'type': 'state', 'region': 'Eastern Myanmar'},
    {'name': 'Naypyidaw', 'type': 'union_territory', 'region': 'Central Myanmar'},
    
    # Major Cities and Towns
    {'name': 'Bagan', 'type': 'city', 'region': 'Mandalay Region'},
    {'name': 'Inle Lake', 'type': 'attraction', 'region': 'Shan State'},
    {'name': 'Ngapali Beach', 'type': 'attraction', 'region': 'Rakhine State'},
    {'name': 'Ngwe Saung Beach', 'type': 'attraction', 'region': 'Ayeyarwady Region'},
    {'name': 'Chaung Tha Beach', 'type': 'attraction', 'region': 'Ayeyarwady Region'},
    {'name': 'Pyin Oo Lwin', 'type': 'town', 'region': 'Mandalay Region'},
    {'name': 'Hsipaw', 'type': 'town', 'region': 'Shan State'},
    {'name': 'Kalaw', 'type': 'town', 'region': 'Shan State'},
    {'name': 'Mawlamyine', 'type': 'city', 'region': 'Mon State'},
    {'name': 'Hpa-An', 'type': 'town', 'region': 'Kayin State'},
    {'name': 'Dawei', 'type': 'city', 'region': 'Tanintharyi Region'},
    {'name': 'Myeik', 'type': 'city', 'region': 'Tanintharyi Region'},
    {'name': 'Monywa', 'type': 'city', 'region': 'Sagaing Region'},
    {'name': 'Taunggyi', 'type': 'city', 'region': 'Shan State'},
    {'name': 'Loikaw', 'type': 'city', 'region': 'Kayah State'},
    {'name': 'Hakha', 'type': 'city', 'region': 'Chin State'},
    {'name': 'Sittwe', 'type': 'city', 'region': 'Rakhine State'},
    {'name': 'Pathein', 'type': 'city', 'region': 'Ayeyarwady Region'},
    {'name': 'Pakokku', 'type': 'city', 'region': 'Magway Region'},
    {'name': 'Meiktila', 'type': 'city', 'region': 'Mandalay Region'},
    {'name': 'Myitkyina', 'type': 'city', 'region': 'Kachin State'},
    {'name': 'Lashio', 'type': 'city', 'region': 'Shan State'},
    {'name': 'Pyay', 'type': 'city', 'region': 'Bago Region'},
    {'name': 'Thaton', 'type': 'city', 'region': 'Mon State'},
    {'name': 'Yenangyaung', 'type': 'town', 'region': 'Magway Region'},
    {'name': 'Chauk', 'type': 'town', 'region': 'Magway Region'},
    {'name': 'Mudon', 'type': 'town', 'region': 'Mon State'},
    {'name': 'Thanlyin', 'type': 'town', 'region': 'Yangon Region'},
    {'name': 'Twante', 'type': 'town', 'region': 'Yangon Region'},
    {'name': 'Bhamo', 'type': 'town', 'region': 'Kachin State'},
    {'name': 'Mogaung', 'type': 'town', 'region': 'Kachin State'},
    {'name': 'Kengtung', 'type': 'town', 'region': 'Shan State'},
    {'name': 'Tachileik', 'type': 'town', 'region': 'Shan State'},
    {'name': 'Muse', 'type': 'town', 'region': 'Shan State'},
    {'name': 'Namhsan', 'type': 'town', 'region': 'Shan State'},
    {'name': 'Kyaukme', 'type': 'town', 'region': 'Shan State'},
    {'name': 'Nyaungshwe', 'type': 'town', 'region': 'Shan State'},
    {'name': 'Shwebo', 'type': 'town', 'region': 'Sagaing Region'},
    {'name': 'Monywa', 'type': 'city', 'region': 'Sagaing Region'},
    {'name': 'Kalay', 'type': 'town', 'region': 'Sagaing Region'},
    {'name': 'Tamwe', 'type': 'town', 'region': 'Yangon Region'},
    {'name': 'Sanchaung', 'type': 'town', 'region': 'Yangon Region'},
    {'name': 'Dagon', 'type': 'town', 'region': 'Yangon Region'},
    {'name': 'Bahan', 'type': 'town', 'region': 'Yangon Region'},
    
    # Popular Attractions
    {'name': 'Shwedagon Pagoda', 'type': 'attraction', 'region': 'Yangon Region'},
    {'name': 'Sule Pagoda', 'type': 'attraction', 'region': 'Yangon Region'},
    {'name': 'Botahtaung Pagoda', 'type': 'attraction', 'region': 'Yangon Region'},
    {'name': 'Kyaiktiyo Pagoda', 'type': 'attraction', 'region': 'Mon State'},
    {'name': 'Mandalay Palace', 'type': 'attraction', 'region': 'Mandalay Region'},
    {'name': 'Mandalay Hill', 'type': 'attraction', 'region': 'Mandalay Region'},
    {'name': 'Kuthodaw Pagoda', 'type': 'attraction', 'region': 'Mandalay Region'},
    {'name': 'Maha Muni Buddha Temple', 'type': 'attraction', 'region': 'Mandalay Region'},
    {'name': 'U Bein Bridge', 'type': 'attraction', 'region': 'Mandalay Region'},
    {'name': 'Mount Popa', 'type': 'attraction', 'region': 'Mandalay Region'},
    {'name': 'Kakku Pagodas', 'type': 'attraction', 'region': 'Shan State'},
    {'name': 'Indein Village', 'type': 'attraction', 'region': 'Shan State'},
    {'name': 'Pindaya Caves', 'type': 'attraction', 'region': 'Shan State'},
    {'name': 'Thanboddhay Pagoda', 'type': 'attraction', 'region': 'Sagaing Region'},
    {'name': 'Bodhi Tataung', 'type': 'attraction', 'region': 'Sagaing Region'},
    {'name': 'Hsinbyume Pagoda', 'type': 'attraction', 'region': 'Mandalay Region'},
    {'name': 'Shwemawdaw Pagoda', 'type': 'attraction', 'region': 'Bago Region'},
    {'name': 'Shwethalyaung Buddha', 'type': 'attraction', 'region': 'Bago Region'},
    {'name': 'Kyauk Kalat Pagoda', 'type': 'attraction', 'region': 'Mon State'},
    {'name': 'Win Sein Taw Ya', 'type': 'attraction', 'region': 'Mon State'},
]

def populate_myanmar_places():
    print("Populating Myanmar places...")
    created_count = 0
    
    for place in MYANMAR_PLACES:
        # Create unique description for each place
        if place['type'] == 'attraction':
            description = f"Visit {place['name']} in {place['region']}"
        elif place['type'] == 'city':
            description = f"Explore the city of {place['name']} in {place['region']}"
        elif place['type'] == 'town':
            description = f"Discover {place['name']} town in {place['region']}"
        elif place['type'] == 'state':
            description = f"Travel through {place['name']} State"
        elif place['type'] == 'region':
            description = f"Explore {place['name']} Region"
        else:
            description = f"Visit {place['name']}"
        
        dest, created = Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': description,
                'is_active': True
            }
        )
        
        if created:
            created_count += 1
            print(f"Created: {place['name']} ({place['type']}) in {place['region']}")
        else:
            # Update existing
            dest.region = place['region']
            dest.type = place['type']
            dest.description = description
            dest.save()
            print(f"Updated: {place['name']}")
    
    print(f"\nTotal destinations: {Destination.objects.count()}")
    print(f"Newly created: {created_count}")
    
    # Print summary
    print("\nSummary by type:")
    for type_val in ['city', 'town', 'attraction', 'state', 'region', 'union_territory']:
        count = Destination.objects.filter(type=type_val).count()
        if count > 0:
            print(f"  {type_val.title()}s: {count}")

if __name__ == "__main__":
    populate_myanmar_places()