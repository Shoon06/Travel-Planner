# C:\Users\ASUS\MyanmarTravelPlanner\populate_airlines.py

import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models import Airline, Destination

def populate_airlines():
    """Populate Myanmar airlines"""
    airlines_data = [
        {
            'name': 'Myanmar National Airlines',
            'code': 'UB',
            'description': 'Flag carrier airline of Myanmar',
            'is_default_for_domestic': True
        },
        {
            'name': 'Air KBZ',
            'code': 'K7',
            'description': 'One of the largest private airlines in Myanmar',
            'is_default_for_domestic': True
        },
        {
            'name': 'Myanmar Airways International',
            'code': '8M',
            'description': 'International airline based in Yangon',
            'is_default_for_domestic': True
        },
        {
            'name': 'Golden Myanmar Airlines',
            'code': 'Y5',
            'description': 'Private airline operating domestic and regional flights',
            'is_default_for_domestic': True
        },
        {
            'name': 'Mann Yadanarpon Airlines',
            'code': '7Y',
            'description': 'Domestic airline based in Mandalay',
            'is_default_for_domestic': True
        },
        {
            'name': 'Air Thanlwin',
            'code': '9A',
            'description': 'Regional airline serving domestic routes',
            'is_default_for_domestic': True
        }
    ]
    
    for airline_data in airlines_data:
        airline, created = Airline.objects.get_or_create(
            name=airline_data['name'],
            defaults={
                'code': airline_data['code'],
                'description': airline_data['description'],
                'is_default_for_domestic': airline_data['is_default_for_domestic']
            }
        )
        if created:
            print(f"Created airline: {airline.name}")
        else:
            print(f"Airline already exists: {airline.name}")

def assign_default_airlines_to_destinations():
    """Assign default airlines to major destinations"""
    
    # Get default airlines
    default_airlines = Airline.objects.filter(is_default_for_domestic=True)[:3]
    
    # Major destinations that need default airlines
    major_destinations = [
        'Yangon',
        'Mandalay',
        'Nay Pyi Taw',
        'Bagan',
        'Inle Lake',
        'Ngapali Beach',
        'Sittwe',
        'Myitkyina',
        'Kawthaung',
        'Dawei',
        'Myeik',
        'Pathein',
        'Mawlamyine',
        'Loikaw',
        'Kengtung',
        'Tachileik',
        'Lashio',
        'Kalaymyo',
        'Kyaukpyu',
        'Putao'
    ]
    
    for dest_name in major_destinations:
        try:
            destination = Destination.objects.get(name__icontains=dest_name)
            destination.default_airlines.set(default_airlines)
            print(f"Assigned default airlines to: {destination.name}")
        except Destination.DoesNotExist:
            # Try partial match
            destinations = Destination.objects.filter(name__icontains=dest_name.split()[0])
            for dest in destinations:
                dest.default_airlines.set(default_airlines)
                print(f"Assigned default airlines to: {dest.name}")
        except Exception as e:
            print(f"Error assigning airlines to {dest_name}: {e}")

if __name__ == '__main__':
    print("Populating airlines...")
    populate_airlines()
    print("\nAssigning default airlines to destinations...")
    assign_default_airlines_to_destinations()
    print("\nDone!")