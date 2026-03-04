# C:\Users\ASUS\MyanmarTravelPlanner\populate_destinations.py
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Destination

# Myanmar States and Regions
MYANMAR_DESTINATIONS = [
    # States
    {"name": "Kachin", "region": "Northern Myanmar", "type": "state"},
    {"name": "Kayah", "region": "Eastern Myanmar", "type": "state"},
    {"name": "Kayin", "region": "Southeastern Myanmar", "type": "state"},
    {"name": "Chin", "region": "Western Myanmar", "type": "state"},
    {"name": "Mon", "region": "Southern Myanmar", "type": "state"},
    {"name": "Rakhine", "region": "Western Myanmar", "type": "state"},
    {"name": "Shan", "region": "Eastern Myanmar", "type": "state"},
    
    # Regions
    {"name": "Yangon", "region": "Lower Myanmar", "type": "region"},
    {"name": "Mandalay", "region": "Central Myanmar", "type": "region"},
    {"name": "Bago", "region": "Lower Myanmar", "type": "region"},
    {"name": "Magway", "region": "Central Myanmar", "type": "region"},
    {"name": "Sagaing", "region": "Northern Myanmar", "type": "region"},
    {"name": "Tanintharyi", "region": "Southern Myanmar", "type": "region"},
    {"name": "Ayeyarwady", "region": "Lower Myanmar", "type": "region"},
    {"name": "Naypyidaw", "region": "Central Myanmar", "type": "union_territory"},
    
    # Popular Cities/Towns
    {"name": "Bagan", "region": "Mandalay Region", "type": "city"},
    {"name": "Inle Lake", "region": "Shan State", "type": "attraction"},
    {"name": "Ngapali Beach", "region": "Rakhine State", "type": "attraction"},
    {"name": "Ngwe Saung Beach", "region": "Ayeyarwady Region", "type": "attraction"},
    {"name": "Pyin Oo Lwin", "region": "Mandalay Region", "type": "town"},
    {"name": "Hsipaw", "region": "Shan State", "type": "town"},
    {"name": "Kalaw", "region": "Shan State", "type": "town"},
    {"name": "Mawlamyine", "region": "Mon State", "type": "city"},
    {"name": "Hpa-An", "region": "Kayin State", "type": "town"},
    {"name": "Dawei", "region": "Tanintharyi Region", "type": "city"},
    {"name": "Myeik", "region": "Tanintharyi Region", "type": "city"},
    {"name": "Monywa", "region": "Sagaing Region", "type": "city"},
    {"name": "Taunggyi", "region": "Shan State", "type": "city"},
    {"name": "Loikaw", "region": "Kayah State", "type": "city"},
    {"name": "Hakha", "region": "Chin State", "type": "city"},
    {"name": "Sittwe", "region": "Rakhine State", "type": "city"},
    {"name": "Pathein", "region": "Ayeyarwady Region", "type": "city"},
]

def populate_destinations():
    print("Populating Myanmar destinations...")
    for dest_data in MYANMAR_DESTINATIONS:
        dest, created = Destination.objects.get_or_create(
            name=dest_data["name"],
            defaults={
                "region": dest_data["region"],
                "type": dest_data["type"],
                "description": f"Explore {dest_data['name']} in {dest_data['region']}"
            }
        )
        if created:
            print(f"Created: {dest.name}")
        else:
            print(f"Already exists: {dest.name}")
    
    print(f"Total destinations: {Destination.objects.count()}")

if __name__ == "__main__":
    populate_destinations()