# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\remove_duplicate_regions.py

from django.core.management.base import BaseCommand
from django.db.models import Q
from planner.models import Destination

class Command(BaseCommand):
    help = 'Remove duplicate region entries and fix region display'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Removing duplicate region entries...'))
        
        removed_count = 0
        fixed_count = 0
        
        # ===========================================
        # FIX 1: AYEYARWADY REGION - Remove duplicates
        # ===========================================
        self.stdout.write("\n📌 Fixing Ayeyarwady Region...")
        
        # Find all Ayeyarwady entries
        ayeyarwady_entries = Destination.objects.filter(
            Q(name__icontains='Ayeyarwady') |
            Q(name__icontains='Ayyearwady') |
            Q(name='Ayeyarwady') |
            Q(name='Ayeyarwady Region')
        )
        
        # Keep the one with "Region" in the name, delete others
        kept_one = None
        for entry in ayeyarwady_entries:
            if 'Region' in entry.name:
                # This is the one we want to keep
                kept_one = entry
                # Fix its name to standard format
                if entry.name != 'Ayeyarwady Region':
                    old_name = entry.name
                    entry.name = 'Ayeyarwady Region'
                    entry.type = 'region'
                    entry.region = 'Ayeyarwady Region'
                    entry.parent = None
                    entry.save()
                    fixed_count += 1
                    self.stdout.write(f"  ✅ Fixed: {old_name} → 'Ayeyarwady Region'")
            else:
                # This is a duplicate, delete it
                self.stdout.write(f"  🗑️ Deleting duplicate: {entry.name}")
                entry.delete()
                removed_count += 1
        
        if not kept_one:
            # Create the proper region if none exists
            Destination.objects.create(
                name='Ayeyarwady Region',
                type='region',
                description='Delta region with riverine landscapes and fishing villages.',
                region='Ayeyarwady Region',
                is_active=True,
                is_region=True,
                parent=None
            )
            fixed_count += 1
            self.stdout.write(f"  ✅ Created Ayeyarwady Region")
        
        # ===========================================
        # FIX 2: BAGO REGION - Remove duplicates
        # ===========================================
        self.stdout.write("\n📌 Fixing Bago Region...")
        
        # Find all Bago entries
        bago_entries = Destination.objects.filter(
            Q(name__icontains='Bago')
        )
        
        # Separate region and city
        region_entry = None
        city_entry = None
        
        for entry in bago_entries:
            if 'Region' in entry.name:
                region_entry = entry
            elif entry.name == 'Bago':
                city_entry = entry
        
        # Fix region entry
        if region_entry:
            if region_entry.name != 'Bago Region':
                old_name = region_entry.name
                region_entry.name = 'Bago Region'
                region_entry.type = 'region'
                region_entry.region = 'Bago Region'
                region_entry.parent = None
                region_entry.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed region: {old_name} → 'Bago Region'")
        else:
            # Create region if missing
            Destination.objects.create(
                name='Bago Region',
                type='region',
                description='Historic region with ancient capital Bago and Shwemawdaw Pagoda.',
                region='Bago Region',
                is_active=True,
                is_region=True,
                parent=None
            )
            fixed_count += 1
            self.stdout.write(f"  ✅ Created Bago Region")
        
        # Fix city entry
        if city_entry:
            if city_entry.type != 'city':
                city_entry.type = 'city'
                city_entry.is_region = False
                city_entry.parent = None
                city_entry.region = 'Bago Region'
                city_entry.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed Bago city: type → 'city'")
        
        # Delete any other Bago entries that are neither region nor city
        for entry in bago_entries:
            if entry != region_entry and entry != city_entry:
                self.stdout.write(f"  🗑️ Deleting duplicate: {entry.name}")
                entry.delete()
                removed_count += 1
        
        # ===========================================
        # FIX 3: SAGAING REGION - Remove duplicates
        # ===========================================
        self.stdout.write("\n📌 Fixing Sagaing Region...")
        
        # Find all Sagaing entries
        sagaing_entries = Destination.objects.filter(
            Q(name__icontains='Sagaing')
        )
        
        # Separate region and city
        sagaing_region_entry = None
        sagaing_city_entry = None
        other_entries = []
        
        for entry in sagaing_entries:
            if 'Region' in entry.name:
                sagaing_region_entry = entry
            elif entry.name == 'Sagaing':
                sagaing_city_entry = entry
            else:
                other_entries.append(entry)
        
        # Fix region entry
        if sagaing_region_entry:
            if sagaing_region_entry.name != 'Sagaing Region':
                old_name = sagaing_region_entry.name
                sagaing_region_entry.name = 'Sagaing Region'
                sagaing_region_entry.type = 'region'
                sagaing_region_entry.region = 'Sagaing Region'
                sagaing_region_entry.parent = None
                sagaing_region_entry.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed region: {old_name} → 'Sagaing Region'")
        else:
            # Create region if missing
            Destination.objects.create(
                name='Sagaing Region',
                type='region',
                description='Region in central Myanmar with many monasteries and religious sites.',
                region='Sagaing Region',
                is_active=True,
                is_region=True,
                parent=None
            )
            fixed_count += 1
            self.stdout.write(f"  ✅ Created Sagaing Region")
        
        # Fix city entry
        if sagaing_city_entry:
            if sagaing_city_entry.type != 'city':
                sagaing_city_entry.type = 'city'
                sagaing_city_entry.is_region = False
                sagaing_city_entry.parent = None
                sagaing_city_entry.region = 'Sagaing Region'
                sagaing_city_entry.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed Sagaing city: type → 'city'")
        else:
            # Create Sagaing city if missing
            Destination.objects.create(
                name='Sagaing',
                type='city',
                description='City in Sagaing Region with many monasteries and religious sites.',
                region='Sagaing Region',
                is_active=True,
                is_region=False,
                parent=None
            )
            fixed_count += 1
            self.stdout.write(f"  ✅ Created Sagaing city")
        
        # Other entries (Monywa, Shwebo, Kalay) should be cities
        for entry in other_entries:
            if entry.name in ['Monywa', 'Shwebo', 'Kalay']:
                if entry.type != 'city':
                    entry.type = 'city'
                    entry.is_region = False
                    entry.parent = None
                    entry.region = 'Sagaing Region'
                    entry.save()
                    fixed_count += 1
                    self.stdout.write(f"  ✅ Fixed {entry.name}: type → 'city'")
        
        # ===========================================
        # FIX 4: TANINTHARYI REGION - Remove duplicates
        # ===========================================
        self.stdout.write("\n📌 Fixing Tanintharyi Region...")
        
        # Find all Tanintharyi entries
        tanintharyi_entries = Destination.objects.filter(
            Q(name__icontains='Tanintharyi')
        )
        
        # Separate region and others
        tanintharyi_region_entry = None
        tanintharyi_city_entries = []
        
        for entry in tanintharyi_entries:
            if 'Region' in entry.name:
                tanintharyi_region_entry = entry
            elif entry.name in ['Dawei', 'Myeik', 'Kawthaung']:
                tanintharyi_city_entries.append(entry)
            else:
                # This might be a duplicate region without "Region" in name
                if entry.name == 'Tanintharyi':
                    self.stdout.write(f"  🗑️ Deleting duplicate: {entry.name}")
                    entry.delete()
                    removed_count += 1
        
        # Fix region entry
        if tanintharyi_region_entry:
            if tanintharyi_region_entry.name != 'Tanintharyi Region':
                old_name = tanintharyi_region_entry.name
                tanintharyi_region_entry.name = 'Tanintharyi Region'
                tanintharyi_region_entry.type = 'region'
                tanintharyi_region_entry.region = 'Tanintharyi Region'
                tanintharyi_region_entry.parent = None
                tanintharyi_region_entry.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed region: {old_name} → 'Tanintharyi Region'")
        else:
            # Create region if missing
            Destination.objects.create(
                name='Tanintharyi Region',
                type='region',
                description='Southernmost region with beautiful islands and beaches.',
                region='Tanintharyi Region',
                is_active=True,
                is_region=True,
                parent=None
            )
            fixed_count += 1
            self.stdout.write(f"  ✅ Created Tanintharyi Region")
        
        # Fix city entries
        for city in tanintharyi_city_entries:
            if city.type != 'city':
                city.type = 'city'
                city.is_region = False
                city.parent = None
                city.region = 'Tanintharyi Region'
                city.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed {city.name}: type → 'city'")
        
        # ===========================================
        # FINAL CLEANUP: Remove ALL parent relationships
        # ===========================================
        self.stdout.write("\n📌 Final cleanup - removing all parent relationships...")
        
        # Remove parents from all regions
        regions = Destination.objects.filter(type='region')
        for region in regions:
            if region.parent:
                region.parent = None
                region.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ {region.name}: parent removed")
        
        # Remove parents from all cities/towns
        cities = Destination.objects.filter(type__in=['city', 'town'])
        for city in cities:
            if city.parent:
                city.parent = None
                city.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ {city.name}: parent removed")
        
        # ===========================================
        # SUMMARY
        # ===========================================
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"SUMMARY: {removed_count} duplicates deleted, {fixed_count} fixes applied"))
        self.stdout.write("="*50)
        
        # Show current regions
        self.stdout.write("\n📊 CURRENT REGIONS:")
        regions = Destination.objects.filter(type='region').order_by('name')
        
        for region in regions:
            cities = Destination.objects.filter(
                region=region.name,
                type__in=['city', 'town']
            ).order_by('name')
            
            self.stdout.write(f"\n📍 {region.name}:")
            self.stdout.write(f"   Cities/Towns: {cities.count()}")
            for city in cities:
                self.stdout.write(f"     - {city.name} ({city.type})")