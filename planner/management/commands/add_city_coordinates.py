# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\add_city_coordinates.py
from django.core.management.base import BaseCommand
from planner.models import Destination
from decimal import Decimal

class Command(BaseCommand):
    help = 'Add coordinates to Destination objects for Myanmar cities'
    
    def handle(self, *args, **kwargs):
        # Myanmar city coordinates database
        city_coordinates = {
            # City Name: (latitude, longitude, region)
            'Yangon': (Decimal('16.8409'), Decimal('96.1735'), 'Yangon Region'),
            'Mandalay': (Decimal('21.9588'), Decimal('96.0891'), 'Mandalay Region'),
            'Bagan': (Decimal('21.1722'), Decimal('94.8603'), 'Mandalay Region'),
            'Inle Lake': (Decimal('20.5550'), Decimal('96.9150'), 'Shan State'),
            'Naypyidaw': (Decimal('19.7460'), Decimal('96.1270'), 'Naypyidaw Union Territory'),
            'Pyin Oo Lwin': (Decimal('22.0339'), Decimal('96.4561'), 'Mandalay Region'),
            'Ngapali': (Decimal('18.4159'), Decimal('94.2977'), 'Rakhine State'),
            'Kalaw': (Decimal('20.6260'), Decimal('96.5623'), 'Shan State'),
            'Taunggyi': (Decimal('20.7853'), Decimal('97.0374'), 'Shan State'),
            'Hsipaw': (Decimal('22.6286'), Decimal('97.3375'), 'Shan State'),
            'Mrauk U': (Decimal('20.5980'), Decimal('93.1950'), 'Rakhine State'),
            'Kyaiktiyo': (Decimal('17.4818'), Decimal('97.1039'), 'Mon State'),
            'Pathein': (Decimal('16.7861'), Decimal('94.7296'), 'Ayeyarwady Region'),
            'Hpa-an': (Decimal('16.8898'), Decimal('97.6433'), 'Kayin State'),
            'Mawlamyine': (Decimal('16.4834'), Decimal('97.6254'), 'Mon State'),
            'Dawei': (Decimal('14.0854'), Decimal('98.1954'), 'Tanintharyi Region'),
            'Myeik': (Decimal('12.4382'), Decimal('98.6071'), 'Tanintharyi Region'),
            'Kawthaung': (Decimal('9.9820'), Decimal('98.5528'), 'Tanintharyi Region'),
            'Sittwe': (Decimal('20.1500'), Decimal('92.9000'), 'Rakhine State'),
            'Monywa': (Decimal('22.1100'), Decimal('95.1400'), 'Sagaing Region'),
            'Shwedagon Pagoda': (Decimal('16.7984'), Decimal('96.1495'), 'Yangon Region'),
            'U Bein Bridge': (Decimal('21.8589'), Decimal('96.0593'), 'Mandalay Region'),
            'Kyaikhtiyo Pagoda': (Decimal('17.4818'), Decimal('97.1039'), 'Mon State'),
        }
        
        updated_count = 0
        
        for city_name, (lat, lng, region) in city_coordinates.items():
            # Try to find the destination by name
            destinations = Destination.objects.filter(name__icontains=city_name)
            
            if destinations.exists():
                for destination in destinations:
                    # Update coordinates if they don't exist or are different
                    if not destination.latitude or not destination.longitude:
                        destination.latitude = lat
                        destination.longitude = lng
                        # Also update region if needed
                        if not destination.region:
                            destination.region = region
                        destination.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Updated {destination.name} with coordinates: {lat}, {lng}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'⚠ {destination.name} already has coordinates')
                        )
            else:
                # Try partial matches
                for key in city_coordinates.keys():
                    if key.lower() in city_name.lower() or city_name.lower() in key.lower():
                        dests = Destination.objects.filter(name__icontains=key)
                        for dest in dests:
                            dest.latitude = lat
                            dest.longitude = lng
                            dest.save()
                            updated_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ Partial match: Updated {dest.name}')
                            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Updated {updated_count} destinations with coordinates')
        )
        
        # Show destinations still missing coordinates
        missing_coords = Destination.objects.filter(
            latitude__isnull=True
        ) | Destination.objects.filter(
            longitude__isnull=True
        )
        
        if missing_coords.exists():
            self.stdout.write(
                self.style.WARNING(f'\n⚠ {missing_coords.count()} destinations still missing coordinates:')
            )
            for dest in missing_coords:
                self.stdout.write(f'  - {dest.name} ({dest.region})')