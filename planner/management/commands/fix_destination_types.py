# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\fix_destination_types.py

from django.core.management.base import BaseCommand
from django.db.models import Q  # ← IMPORT Q HERE!
from planner.models import Destination

class Command(BaseCommand):
    help = 'Fix destination types - ensure attractions have correct type and parent'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Fixing destination types...'))
        
        # First, create missing parent cities for attractions that don't have them
        self.create_missing_parent_cities()
        
        # List of known attractions and their parent cities
        attraction_parents = {
            # Taunggyi attractions
            'Floating Market': 'Taunggyi',
            'Inle Lake': 'Taunggyi',
            'Shwe Bone Pwint Pagoda': 'Taunggyi',
            'Nga Phe Chaung Monastery': 'Taunggyi',
            'Phaung Daw Oo Pagoda': 'Taunggyi',
            'Kakku Pagodas': 'Taunggyi',
            
            # Bagan attractions
            'Ananda Temple': 'Bagan',
            'Shwezigon Pagoda': 'Bagan',
            'Dhammayangyi Temple': 'Bagan',
            'Thatbyinnyu Temple': 'Bagan',
            'Hot Air Balloon Ride': 'Bagan',
            
            # Mandalay attractions
            'Mandalay Palace': 'Mandalay',
            'Mandalay Hill': 'Mandalay',
            'Kuthodaw Pagoda': 'Mandalay',
            'U Bein Bridge': 'Mandalay',
            'Maha Muni Pagoda': 'Mandalay',
            'Shwenandaw Monastery': 'Mandalay',
            
            # Yangon attractions
            'Shwedagon Pagoda': 'Yangon',
            'Bogyoke Market': 'Yangon',
            'Sule Pagoda': 'Yangon',
            'Kandawgyi Lake': 'Yangon',
            'Botataung Pagoda': 'Yangon',
            'National Museum': 'Yangon',
            
            # Inle Lake attractions (these need parent cities)
            'Inle Lake Boat Tour': 'Taunggyi',  # Inle Lake is actually near Taunggyi
            'Indein Village': 'Taunggyi',
            'Nga Phe Kyaung Monastery': 'Taunggyi',
            'Phaw Khone Village': 'Taunggyi',
            'Inthein': 'Taunggyi',
            
            # Ngapali attractions
            'Ngapali Beach Main Beach': 'Thandwe',  # Ngapali Beach is near Thandwe
            'Pearl Island': 'Thandwe',
            'Lin Thar Fishing Village': 'Thandwe',
            
            # Hsipaw attractions
            'Hsipaw Palace': 'Hsipaw',
            'Little Bagan': 'Hsipaw',
            'Bawgyo Pagoda': 'Hsipaw',
            
            # Kalaw attractions
            'Kalaw to Inle Lake Trek': 'Kalaw',
            'Shwe Oo Min Pagoda': 'Kalaw',
            'Hnee Pagoda': 'Kalaw',
            
            # Pyin Oo Lwin attractions
            'National Kandawgyi Gardens': 'Pyin Oo Lwin',
            'Pwe Kauk Falls': 'Pyin Oo Lwin',
            'Candy Factory': 'Pyin Oo Lwin',
            
            # Mrauk U attractions (Mrauk U is a town in Rakhine)
            'Shitthaung Temple': 'Mrauk U',
            'Htukkanthein Temple': 'Mrauk U',
            'Andaw-thein Ordination Hall': 'Mrauk U',
        }
        
        fixed_count = 0
        
        # Fix each attraction
        for attraction_name, parent_city_name in attraction_parents.items():
            try:
                # Find the attraction (use more flexible matching)
                attraction = None
                
                # Try exact match first
                try:
                    attraction = Destination.objects.get(name__iexact=attraction_name)
                except Destination.DoesNotExist:
                    # Try contains match
                    attraction = Destination.objects.filter(name__icontains=attraction_name).first()
                
                if attraction:
                    # Find the parent city
                    parent_city = Destination.objects.filter(
                        Q(name__iexact=parent_city_name) |
                        Q(name__icontains=parent_city_name),
                        type__in=['city', 'town']
                    ).first()
                    
                    if parent_city:
                        # Update the attraction
                        old_type = attraction.type
                        old_parent = attraction.parent
                        
                        attraction.type = 'attraction'
                        attraction.parent = parent_city
                        attraction.is_region = False
                        attraction.save()
                        
                        fixed_count += 1
                        self.stdout.write(f"✅ Fixed: {attraction.name} → parent: {parent_city.name}, type: {attraction.type}")
                    else:
                        self.stdout.write(self.style.WARNING(f"⚠️ Parent city '{parent_city_name}' not found for: {attraction_name}"))
                        
                        # Try to create the parent city if it doesn't exist
                        new_city = self.create_city_if_not_exists(parent_city_name)
                        if new_city:
                            attraction.parent = new_city
                            attraction.type = 'attraction'
                            attraction.is_region = False
                            attraction.save()
                            fixed_count += 1
                            self.stdout.write(f"  → Created new city '{new_city.name}' and linked attraction")
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Attraction not found: {attraction_name}"))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error fixing {attraction_name}: {str(e)}"))
        
        # Now fix any remaining attractions that might have wrong type
        attractions = Destination.objects.filter(
            Q(name__icontains='Pagoda') |
            Q(name__icontains='Temple') |
            Q(name__icontains='Monastery') |
            Q(name__icontains='Market') |
            Q(name__icontains='Lake') |
            Q(name__icontains='Beach') |
            Q(name__icontains='Falls') |
            Q(name__icontains='Cave') |
            Q(name__icontains='Bridge') |
            Q(name__icontains='Palace') |
            Q(name__icontains='Village') |
            Q(name__icontains='Island') |
            Q(name__icontains='Factory') |
            Q(name__icontains='Garden') |
            Q(name__icontains='Museum')
        ).exclude(type='attraction')
        
        for attraction in attractions:
            try:
                if not attraction.parent:
                    # Try to find parent from region
                    parent_city = Destination.objects.filter(
                        region=attraction.region,
                        type__in=['city', 'town']
                    ).first()
                    
                    if parent_city:
                        attraction.parent = parent_city
                
                attraction.type = 'attraction'
                attraction.is_region = False
                attraction.save()
                fixed_count += 1
                self.stdout.write(f"✅ Fixed (auto): {attraction.name} → type: attraction")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error auto-fixing {attraction.name}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Successfully fixed {fixed_count} attractions"))
    
    def create_missing_parent_cities(self):
        """Create parent cities that might be missing"""
        cities_to_create = [
            {'name': 'Thandwe', 'region': 'Rakhine State', 'type': 'town'},
            {'name': 'Mrauk U', 'region': 'Rakhine State', 'type': 'town'},
            {'name': 'Ngapali Beach', 'region': 'Rakhine State', 'type': 'attraction'},  # This is actually an attraction
        ]
        
        for city_data in cities_to_create:
            if not Destination.objects.filter(name=city_data['name']).exists():
                city = Destination.objects.create(
                    name=city_data['name'],
                    region=city_data['region'],
                    type=city_data['type'],
                    is_active=True,
                    is_region=True if city_data['type'] in ['city', 'town'] else False
                )
                self.stdout.write(f"✅ Created missing city: {city.name}")
    
    def create_city_if_not_exists(self, city_name):
        """Create a city if it doesn't exist"""
        try:
            # Check if city already exists
            city = Destination.objects.filter(
                Q(name__iexact=city_name) |
                Q(name__icontains=city_name),
                type__in=['city', 'town']
            ).first()
            
            if city:
                return city
            
            # Determine region based on city name
            region_map = {
                'Thandwe': 'Rakhine State',
                'Mrauk U': 'Rakhine State',
                'Taunggyi': 'Shan State',
                'Bagan': 'Mandalay Region',
                'Mandalay': 'Mandalay Region',
                'Yangon': 'Yangon Region',
                'Hsipaw': 'Shan State',
                'Kalaw': 'Shan State',
                'Pyin Oo Lwin': 'Mandalay Region',
            }
            
            region = region_map.get(city_name, 'Unknown')
            
            # Create the city
            city = Destination.objects.create(
                name=city_name,
                region=region,
                type='town',  # Default to town
                is_active=True,
                is_region=True,
                description=f"{city_name} is a beautiful destination in Myanmar."
            )
            self.stdout.write(f"✅ Created new city: {city_name}")
            return city
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error creating city {city_name}: {str(e)}"))
            return None