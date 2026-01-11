import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models import Destination

def populate_destinations():
    destinations_data = [
        # Yangon Region
        {'name': 'Shwedagon Pagoda', 'region': 'Yangon Region', 'type': 'attraction', 
         'description': 'The most sacred Buddhist pagoda in Myanmar, covered in gold leaf and diamonds.'},
        {'name': 'Bogyoke Market', 'region': 'Yangon Region', 'type': 'attraction',
         'description': 'Famous market known for colonial architecture and local crafts.'},
        {'name': 'Kandawgyi Park', 'region': 'Yangon Region', 'type': 'attraction',
         'description': 'Beautiful park with the royal barge and views of Shwedagon Pagoda.'},
        {'name': 'Sule Pagoda', 'region': 'Yangon Region', 'type': 'attraction',
         'description': 'Ancient pagoda located in the center of Yangon city.'},
        
        # Mandalay Region
        {'name': 'Mandalay Palace', 'region': 'Mandalay Region', 'type': 'attraction',
         'description': 'The last royal palace of the last Burmese monarchy.'},
        {'name': 'Mandalay Hill', 'region': 'Mandalay Region', 'type': 'attraction',
         'description': 'Hill with panoramic views of Mandalay and surrounding areas.'},
        {'name': 'U Bein Bridge', 'region': 'Mandalay Region', 'type': 'attraction',
         'description': 'The worlds longest teak bridge spanning Taungthaman Lake.'},
        
        # Bagan
        {'name': 'Ananda Temple', 'region': 'Bagan', 'type': 'attraction',
         'description': 'One of the most beautiful and well-preserved temples in Bagan.'},
        {'name': 'Shwezigon Pagoda', 'region': 'Bagan', 'type': 'attraction',
         'description': 'Gilded pagoda built during the reign of King Anawrahta.'},
        
        # Inle Lake
        {'name': 'Inle Lake', 'region': 'Shan State', 'type': 'attraction',
         'description': 'Freshwater lake known for its leg-rowing fishermen and floating villages.'},
        
        # Ngapali Beach
        {'name': 'Ngapali Beach', 'region': 'Rakhine State', 'type': 'attraction',
         'description': 'Beautiful beach with white sand and clear blue water.'},
    ]
    
    for data in destinations_data:
        Destination.objects.get_or_create(
            name=data['name'],
            defaults={
                'region': data['region'],
                'type': data['type'],
                'description': data['description'],
                'is_active': True,
            }
        )
    
    print(f"Created/updated {len(destinations_data)} destinations")

if __name__ == '__main__':
    populate_destinations()