# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\list_cities.py

from django.core.management.base import BaseCommand
from planner.models import Destination

class Command(BaseCommand):
    help = 'List all cities and towns in the database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Listing all cities and towns...\n'))
        
        # Get all cities and towns
        cities_towns = Destination.objects.filter(
            type__in=['city', 'town'],
            is_active=True
        ).order_by('name')
        
        self.stdout.write(f"📋 TOTAL: {cities_towns.count()} Cities and Towns\n")
        self.stdout.write("=" * 60)
        
        # Group by region
        by_region = {}
        for city in cities_towns:
            if city.region not in by_region:
                by_region[city.region] = []
            by_region[city.region].append(city)
        
        # Print by region
        for region, cities in sorted(by_region.items()):
            self.stdout.write(f"\n📍 {region} ({len(cities)} cities/towns):")
            for city in sorted(cities, key=lambda x: x.name):
                self.stdout.write(f"    - {city.name} ({city.type})")
        
        # Print simple list
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("\n📋 SIMPLE LIST:\n")
        
        for i, city in enumerate(cities_towns, 1):
            self.stdout.write(f"{i:2d}. {city.name}")
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(f"\nTotal: {cities_towns.count()} cities/towns")