# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\fix_city_parents.py

from django.core.management.base import BaseCommand
from planner.models import Destination

class Command(BaseCommand):
    help = 'Remove parent relationships from cities and towns'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Fixing city parent relationships...'))
        
        fixed_count = 0
        
        # Get all cities and towns that have parents
        cities_with_parents = Destination.objects.filter(
            type__in=['city', 'town', 'region'],
            parent__isnull=False
        )
        
        self.stdout.write(f"Found {cities_with_parents.count()} cities/towns with parents:")
        
        for city in cities_with_parents:
            old_parent = city.parent
            city.parent = None
            city.save()
            fixed_count += 1
            self.stdout.write(f"  ✅ Removed parent '{old_parent.name}' from {city.name} ({city.type})")
        
        # Also fix any states or regions that might have parents
        states_with_parents = Destination.objects.filter(
            type='state',
            parent__isnull=False
        )
        
        for state in states_with_parents:
            state.parent = None
            state.save()
            fixed_count += 1
            self.stdout.write(f"  ✅ Removed parent from state: {state.name}")
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Fixed {fixed_count} destinations"))