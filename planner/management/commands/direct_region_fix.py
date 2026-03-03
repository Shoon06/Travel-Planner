# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\direct_region_fix.py

from django.core.management.base import BaseCommand
from django.db.models import Q
from planner.models import Destination

class Command(BaseCommand):
    help = 'Direct fix for specific region issues'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting direct region fixes...'))
        
        fixed_count = 0
        
        # ===========================================
        # FIX 1: Move Bago Region out of Yangon Region
        # ===========================================
        self.stdout.write("\n📌 FIX 1: Moving Bago Region out of Yangon Region")
        
        # Find the Bago Region destination itself
        bago_region = Destination.objects.filter(name='Bago Region').first()
        if bago_region:
            old_region = bago_region.region
            if old_region != 'Bago Region':
                bago_region.region = 'Bago Region'
                bago_region.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed Bago Region: region '{old_region}' → 'Bago Region'")
        
        # Find any other Bago-related destinations
        bago_dests = Destination.objects.filter(
            Q(name__icontains='Bago') & ~Q(name='Bago Region')
        )
        for dest in bago_dests:
            if dest.region != 'Bago Region':
                old_region = dest.region
                dest.region = 'Bago Region'
                dest.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed {dest.name}: region '{old_region}' → 'Bago Region'")
        
        # ===========================================
        # FIX 2: Move Sagaing out of Kachin State
        # ===========================================
        self.stdout.write("\n📌 FIX 2: Moving Sagaing out of Kachin State")
        
        # Find Sagaing
        sagaing = Destination.objects.filter(name='Sagaing').first()
        if sagaing:
            old_region = sagaing.region
            if old_region != 'Sagaing Region':
                sagaing.region = 'Sagaing Region'
                sagaing.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed Sagaing: region '{old_region}' → 'Sagaing Region'")
        
        # Find Sagaing cities
        sagaing_cities = Destination.objects.filter(
            Q(name__in=['Monywa', 'Shwebo', 'Kalay'])
        )
        for city in sagaing_cities:
            if city.region != 'Sagaing Region':
                old_region = city.region
                city.region = 'Sagaing Region'
                city.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed {city.name}: region '{old_region}' → 'Sagaing Region'")
        
        # ===========================================
        # FIX 3: Fix Ayeyarwady Region
        # ===========================================
        self.stdout.write("\n📌 FIX 3: Fixing Ayeyarwady Region")
        
        # Fix the region name
        ayeyarwady = Destination.objects.filter(
            Q(name__icontains='Ayeayrwayd') | 
            Q(name__icontains='Ayeayrawdy') |
            Q(name='Ayeyarwady Region')
        ).first()
        
        if ayeyarwady:
            if ayeyarwady.name != 'Ayeyarwady Region':
                old_name = ayeyarwady.name
                ayeyarwady.name = 'Ayeyarwady Region'
                ayeyarwady.region = 'Ayeyarwady Region'
                ayeyarwady.type = 'region'
                ayeyarwady.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed Ayeyarwady: '{old_name}' → 'Ayeyarwady Region'")
        
        # Fix Pathein
        pathein = Destination.objects.filter(name='Pathein').first()
        if pathein:
            if pathein.region != 'Ayeyarwady Region':
                old_region = pathein.region
                pathein.region = 'Ayeyarwady Region'
                pathein.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed Pathein: region '{old_region}' → 'Ayeyarwady Region'")
        
        # ===========================================
        # FIX 4: Remove parents from ALL regions
        # ===========================================
        self.stdout.write("\n📌 FIX 4: Removing parents from all regions")
        
        regions = Destination.objects.filter(type='region')
        for region in regions:
            if region.parent is not None:
                old_parent = region.parent.name
                region.parent = None
                region.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ {region.name}: removed parent '{old_parent}'")
        
        # ===========================================
        # FIX 5: Remove parents from ALL cities/towns
        # ===========================================
        self.stdout.write("\n📌 FIX 5: Removing parents from all cities/towns")
        
        cities = Destination.objects.filter(type__in=['city', 'town'])
        for city in cities:
            if city.parent is not None:
                old_parent = city.parent.name
                city.parent = None
                city.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ {city.name}: removed parent '{old_parent}'")
        
        # ===========================================
        # SUMMARY
        # ===========================================
        self.stdout.write(self.style.SUCCESS(f"\n✅ TOTAL FIXES: {fixed_count}"))
        
        # Show final region grouping
        self.stdout.write("\n📊 FINAL REGION GROUPING:")
        
        # Get all unique regions from cities/towns
        regions = Destination.objects.filter(
            type__in=['city', 'town'],
            parent__isnull=True
        ).values_list('region', flat=True).distinct().order_by('region')
        
        for region in regions:
            if region:
                # Get cities in this region
                cities = Destination.objects.filter(
                    region=region,
                    type__in=['city', 'town'],
                    parent__isnull=True
                ).order_by('name')
                
                if cities.exists():
                    self.stdout.write(f"\n📍 {region}:")
                    for city in cities:
                        self.stdout.write(f"    - {city.name} ({city.type})")