# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\fix_region_names.py

from django.core.management.base import BaseCommand
from planner.models import Destination

class Command(BaseCommand):
    help = 'Standardize region names (e.g., "Yangon" and "Yangon Region" → "Yangon Region")'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Fixing region names...'))
        
        # Mapping of inconsistent region names to standardized names
        region_mapping = {
            # Yangon
            'Yangon': 'Yangon Region',
            'Yangon Region': 'Yangon Region',
            'YANGON': 'Yangon Region',
            'yangon': 'Yangon Region',
            
            # Mandalay
            'Mandalay': 'Mandalay Region',
            'Mandalay Region': 'Mandalay Region',
            'MANDALAY': 'Mandalay Region',
            'mandalay': 'Mandalay Region',
            
            # Bagan (should be in Mandalay Region)
            'Bagan': 'Mandalay Region',
            'Bagan Region': 'Mandalay Region',
            
            # Shan State
            'Shan': 'Shan State',
            'Shan State': 'Shan State',
            'SHAN': 'Shan State',
            
            # Rakhine
            'Rakhine': 'Rakhine State',
            'Rakhine State': 'Rakhine State',
            
            # Kayin
            'Kayin': 'Kayin State',
            'Kayin State': 'Kayin State',
            
            # Mon
            'Mon': 'Mon State',
            'Mon State': 'Mon State',
            
            # Chin
            'Chin': 'Chin State',
            'Chin State': 'Chin State',
            
            # Kachin
            'Kachin': 'Kachin State',
            'Kachin State': 'Kachin State',
            
            # Kayah
            'Kayah': 'Kayah State',
            'Kayah State': 'Kayah State',
            
            # Sagaing
            'Sagaing': 'Sagaing Region',
            'Sagaing Region': 'Sagaing Region',
            
            # Tanintharyi
            'Tanintharyi': 'Tanintharyi Region',
            'Tanintharyi Region': 'Tanintharyi Region',
            
            # Ayeyarwady
            'Ayeyarwady': 'Ayeyarwady Region',
            'Ayeyarwady Region': 'Ayeyarwady Region',
            
            # Bago
            'Bago': 'Bago Region',
            'Bago Region': 'Bago Region',
            
            # Magway
            'Magway': 'Magway Region',
            'Magway Region': 'Magway Region',
            
            # Naypyidaw
            'Naypyidaw': 'Naypyidaw',
            'Nay Pyi Taw': 'Naypyidaw',
        }
        
        fixed_count = 0
        
        # Get all unique region names currently in database
        current_regions = Destination.objects.values_list('region', flat=True).distinct()
        
        self.stdout.write("\n📊 Current regions in database:")
        for region in sorted(current_regions):
            self.stdout.write(f"  - {region}")
        
        self.stdout.write("\n🔄 Standardizing region names...")
        
        # Update each destination's region based on mapping
        for old_name, new_name in region_mapping.items():
            # Find destinations with this region name
            destinations = Destination.objects.filter(region__iexact=old_name)
            count = destinations.count()
            
            if count > 0:
                destinations.update(region=new_name)
                fixed_count += count
                self.stdout.write(f"  ✅ Updated {count} destinations from '{old_name}' to '{new_name}'")
        
        # Also fix any destinations that might have parent relationships wrong
        self.stdout.write("\n🔄 Fixing parent relationships...")
        
        # Make sure Yangon city has correct region
        yangon_city = Destination.objects.filter(name='Yangon', type='city').first()
        if yangon_city:
            yangon_city.region = 'Yangon Region'
            yangon_city.save()
            self.stdout.write(f"  ✅ Updated Yangon city region to 'Yangon Region'")
        
        # Make sure Mandalay city has correct region
        mandalay_city = Destination.objects.filter(name='Mandalay', type='city').first()
        if mandalay_city:
            mandalay_city.region = 'Mandalay Region'
            mandalay_city.save()
            self.stdout.write(f"  ✅ Updated Mandalay city region to 'Mandalay Region'")
        
        # Make sure Bagan has correct region
        bagan = Destination.objects.filter(name='Bagan').first()
        if bagan:
            bagan.region = 'Mandalay Region'
            bagan.save()
            self.stdout.write(f"  ✅ Updated Bagan region to 'Mandalay Region'")
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Successfully fixed {fixed_count} destinations"))
        
        # Show updated regions
        self.stdout.write("\n📊 Updated regions in database:")
        updated_regions = Destination.objects.values_list('region', flat=True).distinct()
        for region in sorted(updated_regions):
            count = Destination.objects.filter(region=region).count()
            self.stdout.write(f"  - {region}: {count} destinations")