# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\fix_regions_complete.py

from django.core.management.base import BaseCommand
from django.db.models import Q
from planner.models import Destination

class Command(BaseCommand):
    help = 'Complete fix for Ayeyarwady and Bago regions'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting complete region fixes...'))
        
        fixed_count = 0
        
        # ===========================================
        # PART 1: FIX AYEYARWADY REGION
        # ===========================================
        self.stdout.write("\n" + "="*50)
        self.stdout.write("📌 PART 1: FIXING AYEYARWADY REGION")
        self.stdout.write("="*50)
        
        # Fix the typo in the region name
        ayeyarwady_region = Destination.objects.filter(
            Q(name__icontains='Ayeayrwayd') | 
            Q(name__icontains='Ayeayrawdy') |
            Q(name='Ayeyarwady Region')
        ).first()
        
        if not ayeyarwady_region:
            # Create Ayeyarwady Region if it doesn't exist
            ayeyarwady_region = Destination.objects.create(
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
        else:
            # Fix the name if it has typo
            if ayeyarwady_region.name != 'Ayeyarwady Region':
                old_name = ayeyarwady_region.name
                ayeyarwady_region.name = 'Ayeyarwady Region'
                ayeyarwady_region.type = 'region'
                ayeyarwady_region.region = 'Ayeyarwady Region'
                ayeyarwady_region.is_region = True
                ayeyarwady_region.parent = None
                ayeyarwady_region.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed Ayeyarwady name: '{old_name}' → 'Ayeyarwady Region'")
        
        # Fix Pathein (should be a city in Ayeyarwady Region)
        pathein = Destination.objects.filter(name='Pathein').first()
        if not pathein:
            pathein = Destination.objects.create(
                name='Pathein',
                type='city',
                description='Capital of Ayeyarwady Region, famous for its traditional umbrella making.',
                region='Ayeyarwady Region',
                is_active=True,
                is_region=False,
                parent=None
            )
            fixed_count += 1
            self.stdout.write(f"  ✅ Created Pathein city")
        else:
            # Update Pathein's region and type
            old_type = pathein.type
            old_region = pathein.region
            
            pathein.type = 'city'
            pathein.region = 'Ayeyarwady Region'
            pathein.is_region = False
            pathein.parent = None
            pathein.save()
            
            if old_type != 'city' or old_region != 'Ayeyarwady Region':
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed Pathein: type '{old_type}' → 'city', region '{old_region}' → 'Ayeyarwady Region'")
        
        # Add more cities/towns to Ayeyarwady Region
        self.stdout.write("\n  📋 Adding cities/towns to Ayeyarwady Region...")
        
        ayeyarwady_cities = [
            {
                'name': 'Myaungmya',
                'type': 'town',
                'description': 'Town in Ayeyarwady Region known for rice trading.',
            },
            {
                'name': 'Hinthada',
                'type': 'town',
                'description': 'Major river port town on the Ayeyarwady River.',
            },
            {
                'name': 'Bogale',
                'type': 'town',
                'description': 'Town in the Ayeyarwady delta region.',
            },
            {
                'name': 'Pyapon',
                'type': 'town',
                'description': 'Town in the southern part of Ayeyarwady Region.',
            },
            {
                'name': 'Labutta',
                'type': 'town',
                'description': 'Coastal town in Ayeyarwady Region.',
            },
            {
                'name': 'Wakema',
                'type': 'town',
                'description': 'Town in Myaungmya District.',
            },
        ]
        
        for city_data in ayeyarwady_cities:
            existing = Destination.objects.filter(name=city_data['name']).first()
            if not existing:
                Destination.objects.create(
                    name=city_data['name'],
                    type=city_data['type'],
                    description=city_data['description'],
                    region='Ayeyarwady Region',
                    is_active=True,
                    is_region=False,
                    parent=None
                )
                fixed_count += 1
                self.stdout.write(f"    ✅ Added {city_data['name']} ({city_data['type']})")
            else:
                # Update existing city's region if needed
                if existing.region != 'Ayeyarwady Region' or existing.type != city_data['type']:
                    old_region = existing.region
                    old_type = existing.type
                    existing.region = 'Ayeyarwady Region'
                    existing.type = city_data['type']
                    existing.is_region = False
                    existing.parent = None
                    existing.save()
                    fixed_count += 1
                    self.stdout.write(f"    ✅ Updated {existing.name}: type '{old_type}' → '{city_data['type']}', region '{old_region}' → 'Ayeyarwady Region'")
        
        # ===========================================
        # PART 2: FIX BAGO REGION
        # ===========================================
        self.stdout.write("\n" + "="*50)
        self.stdout.write("📌 PART 2: FIXING BAGO REGION")
        self.stdout.write("="*50)
        
        # Fix Bago city (should be a city, not region)
        bago_city = Destination.objects.filter(name='Bago').first()
        if not bago_city:
            bago_city = Destination.objects.create(
                name='Bago',
                type='city',
                description='Ancient capital with many pagodas and monasteries, home to the famous Shwemawdaw Pagoda.',
                region='Bago Region',
                is_active=True,
                is_region=False,
                parent=None
            )
            fixed_count += 1
            self.stdout.write(f"  ✅ Created Bago city")
        else:
            old_type = bago_city.type
            old_region = bago_city.region
            
            bago_city.type = 'city'
            bago_city.region = 'Bago Region'
            bago_city.is_region = False
            bago_city.parent = None
            bago_city.save()
            
            if old_type != 'city' or old_region != 'Bago Region':
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed Bago: type '{old_type}' → 'city', region '{old_region}' → 'Bago Region'")
        
        # Fix Bago Region (should be a region)
        bago_region = Destination.objects.filter(name='Bago Region').first()
        if not bago_region:
            bago_region = Destination.objects.create(
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
        else:
            old_type = bago_region.type
            if old_type != 'region':
                bago_region.type = 'region'
                bago_region.is_region = True
                bago_region.parent = None
                bago_region.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed Bago Region: type '{old_type}' → 'region'")
        
        # Add more cities/towns to Bago Region
        self.stdout.write("\n  📋 Adding cities/towns to Bago Region...")
        
        bago_cities = [
            {
                'name': 'Pyay',
                'type': 'city',
                'description': 'Ancient city on the Ayeyarwady River, known for Shwesandaw Pagoda.',
            },
            {
                'name': 'Taungoo',
                'type': 'city',
                'description': 'Historic city with ancient ruins and forests.',
            },
            {
                'name': 'Nyaunglebin',
                'type': 'town',
                'description': 'Town in Bago Region near the Sittaung River.',
            },
            {
                'name': 'Shwegyin',
                'type': 'town',
                'description': 'Town on the Shwegyin River.',
            },
            {
                'name': 'Tharrawaddy',
                'type': 'town',
                'description': 'Town in western Bago Region.',
            },
            {
                'name': 'Letpadan',
                'type': 'town',
                'description': 'Town in Tharrawaddy District.',
            },
            {
                'name': 'Paungde',
                'type': 'town',
                'description': 'Town in Pyay District.',
            },
        ]
        
        for city_data in bago_cities:
            existing = Destination.objects.filter(name=city_data['name']).first()
            if not existing:
                Destination.objects.create(
                    name=city_data['name'],
                    type=city_data['type'],
                    description=city_data['description'],
                    region='Bago Region',
                    is_active=True,
                    is_region=False,
                    parent=None
                )
                fixed_count += 1
                self.stdout.write(f"    ✅ Added {city_data['name']} ({city_data['type']})")
            else:
                # Update existing city's region if needed
                if existing.region != 'Bago Region' or existing.type != city_data['type']:
                    old_region = existing.region
                    old_type = existing.type
                    existing.region = 'Bago Region'
                    existing.type = city_data['type']
                    existing.is_region = False
                    existing.parent = None
                    existing.save()
                    fixed_count += 1
                    self.stdout.write(f"    ✅ Updated {existing.name}: type '{old_type}' → '{city_data['type']}', region '{old_region}' → 'Bago Region'")
        
        # ===========================================
        # PART 3: CLEAN UP - Remove parents from all regions and cities
        # ===========================================
        self.stdout.write("\n" + "="*50)
        self.stdout.write("📌 PART 3: CLEANING UP PARENT RELATIONSHIPS")
        self.stdout.write("="*50)
        
        # Remove parents from all regions
        regions = Destination.objects.filter(type='region')
        for region in regions:
            if region.parent is not None:
                old_parent = region.parent.name
                region.parent = None
                region.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ {region.name}: removed parent '{old_parent}'")
        
        # Remove parents from all cities/towns
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
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"✅ COMPLETE: Total {fixed_count} fixes applied"))
        self.stdout.write("="*50)
        
        # Show final region breakdown
        self.stdout.write("\n📊 FINAL REGION BREAKDOWN:")
        
        regions = Destination.objects.filter(
            type='region'
        ).order_by('name')
        
        for region in regions:
            # Count cities in this region
            cities_count = Destination.objects.filter(
                region=region.name,
                type__in=['city', 'town']
            ).count()
            
            self.stdout.write(f"\n📍 {region.name}:")
            self.stdout.write(f"    Region: {region.name} (type: {region.type})")
            self.stdout.write(f"    Cities/Towns in this region: {cities_count}")
            
            # List the cities
            cities = Destination.objects.filter(
                region=region.name,
                type__in=['city', 'town']
            ).order_by('name')
            
            for city in cities:
                self.stdout.write(f"      - {city.name} ({city.type})")