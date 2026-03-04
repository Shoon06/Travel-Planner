# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\check_destination_types.py

from django.core.management.base import BaseCommand
from planner.models import Destination

class Command(BaseCommand):
    help = 'Check what types are in the database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Checking destination types...'))
        
        # Count by type
        types = {}
        for dest in Destination.objects.all():
            types[dest.type] = types.get(dest.type, 0) + 1
        
        self.stdout.write("\n📊 DESTINATION TYPES COUNT:")
        for type_name, count in types.items():
            self.stdout.write(f"  - {type_name}: {count}")
        
        # Show all attractions that might be misclassified
        self.stdout.write("\n🔍 ATTRACTIONS WITH NON-ATTRACTION TYPES:")
        attractions = Destination.objects.filter(
            parent__isnull=False  # Has a parent (should be attraction)
        ).exclude(type='attraction')
        
        for attr in attractions:
            self.stdout.write(f"  - {attr.name} (Type: {attr.type}, Parent: {attr.parent})")
        
        # Show all cities/towns that might have wrong parent
        self.stdout.write("\n🏙️ CITIES/TOWNS:")
        cities = Destination.objects.filter(
            type__in=['city', 'town', 'region']
        ).order_by('name')
        
        for city in cities:
            self.stdout.write(f"  - {city.name} (Type: {city.type})")
        
        # Show all attractions that are correctly typed
        self.stdout.write("\n✅ CORRECTLY TYPED ATTRACTIONS:")
        correct_attractions = Destination.objects.filter(
            type='attraction'
        ).order_by('name')
        
        for attr in correct_attractions:
            self.stdout.write(f"  - {attr.name}")