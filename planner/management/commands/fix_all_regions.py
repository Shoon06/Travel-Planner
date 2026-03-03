# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\fix_all_regions.py

from django.core.management.base import BaseCommand
from planner.models import Destination
from django.db.models import Q  
class Command(BaseCommand):
    help = 'Fix all region names to use proper State/Region names only'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Fixing all region names...'))
        
        # Mapping of incorrect region names to correct State/Region names
        region_mapping = {
            # ===== LOWER MYANMAR =====
            'Lower Myanmar': 'Yangon Region',
            'lower myanmar': 'Yangon Region',
            'Lower Myanmar ': 'Yangon Region',
            
            # ===== UPPER MYANMAR =====
            'Upper Myanmar': 'Mandalay Region',
            'upper myanmar': 'Mandalay Region',
            'Upper Myanmar ': 'Mandalay Region',
            
            # ===== SOUTHERN MYANMAR =====
            'Southern Myanmar': 'Tanintharyi Region',
            'southern myanmar': 'Tanintharyi Region',
            'Southern Myanmar ': 'Tanintharyi Region',
            
            # ===== EASTERN MYANMAR =====
            'Eastern Myanmar': 'Shan State',
            'eastern myanmar': 'Shan State',
            'Eastern Myanmar ': 'Shan State',
            
            # ===== WESTERN MYANMAR =====
            'Western Myanmar': 'Rakhine State',
            'western myanmar': 'Rakhine State',
            'Western Myanmar ': 'Rakhine State',
            
            # ===== NORTHERN MYANMAR =====
            'Northern Myanmar': 'Kachin State',
            'northern myanmar': 'Kachin State',
            'Northern Myanmar ': 'Kachin State',
            
            # ===== SOUTHEASTERN MYANMAR =====
            'Southeastern Myanmar': 'Kayin State',
            'southeastern myanmar': 'Kayin State',
            'Southeastern Myanmar ': 'Kayin State',
            
            # ===== SPECIFIC REGION FIXES =====
            # Yangon
            'Yangon': 'Yangon Region',
            'Yangon Region': 'Yangon Region',
            'YANGON': 'Yangon Region',
            'yangon': 'Yangon Region',
            'YANGON REGION': 'Yangon Region',
            
            # Mandalay
            'Mandalay': 'Mandalay Region',
            'Mandalay Region': 'Mandalay Region',
            'MANDALAY': 'Mandalay Region',
            'mandalay': 'Mandalay Region',
            'MANDALAY REGION': 'Mandalay Region',
            
            # Shan
            'Shan': 'Shan State',
            'Shan State': 'Shan State',
            'SHAN': 'Shan State',
            'shan': 'Shan State',
            'SHAN STATE': 'Shan State',
            
            # Rakhine
            'Rakhine': 'Rakhine State',
            'Rakhine State': 'Rakhine State',
            'RAKHINE': 'Rakhine State',
            'rakhine': 'Rakhine State',
            
            # Kayin
            'Kayin': 'Kayin State',
            'Kayin State': 'Kayin State',
            'KAYIN': 'Kayin State',
            'kayin': 'Kayin State',
            
            # Mon
            'Mon': 'Mon State',
            'Mon State': 'Mon State',
            'MON': 'Mon State',
            'mon': 'Mon State',
            
            # Chin
            'Chin': 'Chin State',
            'Chin State': 'Chin State',
            'CHIN': 'Chin State',
            'chin': 'Chin State',
            
            # Kachin
            'Kachin': 'Kachin State',
            'Kachin State': 'Kachin State',
            'KACHIN': 'Kachin State',
            'kachin': 'Kachin State',
            
            # Kayah
            'Kayah': 'Kayah State',
            'Kayah State': 'Kayah State',
            'KAYAH': 'Kayah State',
            'kayah': 'Kayah State',
            
            # Sagaing
            'Sagaing': 'Sagaing Region',
            'Sagaing Region': 'Sagaing Region',
            'SAGAING': 'Sagaing Region',
            'sagaing': 'Sagaing Region',
            
            # Tanintharyi
            'Tanintharyi': 'Tanintharyi Region',
            'Tanintharyi Region': 'Tanintharyi Region',
            'TANINTHARYI': 'Tanintharyi Region',
            'tanintharyi': 'Tanintharyi Region',
            
            # Ayeyarwady
            'Ayeyarwady': 'Ayeyarwady Region',
            'Ayeyarwady Region': 'Ayeyarwady Region',
            'AYEYARWADY': 'Ayeyarwady Region',
            'ayeyarwady': 'Ayeyarwady Region',
            'Ayeayrawdy': 'Ayeyarwady Region',  # Fix typo
            
            # Bago
            'Bago': 'Bago Region',
            'Bago Region': 'Bago Region',
            'BAGO': 'Bago Region',
            'bago': 'Bago Region',
            
            # Magway
            'Magway': 'Magway Region',
            'Magway Region': 'Magway Region',
            'MAGWAY': 'Magway Region',
            'magway': 'Magway Region',
            
            # Naypyidaw
            'Naypyidaw': 'Naypyidaw Union Territory',
            'Nay Pyi Taw': 'Naypyidaw Union Territory',
            'NAYPYIDAW': 'Naypyidaw Union Territory',
            'naypyidaw': 'Naypyidaw Union Territory',
        }
        
        fixed_count = 0
        
        # Show current regions before fix
        self.stdout.write("\n📊 CURRENT REGIONS IN DATABASE:")
        current_regions = Destination.objects.values_list('region', flat=True).distinct().order_by('region')
        for region in sorted(current_regions):
            if region:
                count = Destination.objects.filter(region=region).count()
                self.stdout.write(f"  - {region}: {count} destinations")
        
        self.stdout.write("\n🔄 STANDARDIZING REGION NAMES...")
        
        # Update each destination's region based on mapping
        for old_name, new_name in region_mapping.items():
            # Find destinations with this region name (case insensitive)
            destinations = Destination.objects.filter(region__iexact=old_name)
            count = destinations.count()
            
            if count > 0:
                destinations.update(region=new_name)
                fixed_count += count
                self.stdout.write(f"  ✅ Updated {count} destinations from '{old_name}' to '{new_name}'")
        
        # Also fix any destinations with empty or null regions
        empty_regions = Destination.objects.filter(Q(region__isnull=True) | Q(region=''))
        if empty_regions.count() > 0:
            self.stdout.write(f"\n⚠️ Found {empty_regions.count()} destinations with empty regions:")
            for dest in empty_regions:
                # Try to assign region based on name or parent
                if dest.parent and dest.parent.region:
                    dest.region = dest.parent.region
                elif dest.name in ['Yangon', 'Mandalay', 'Bagan', 'Taunggyi']:
                    if dest.name == 'Yangon':
                        dest.region = 'Yangon Region'
                    elif dest.name == 'Mandalay':
                        dest.region = 'Mandalay Region'
                    elif dest.name == 'Bagan':
                        dest.region = 'Mandalay Region'
                    elif dest.name == 'Taunggyi':
                        dest.region = 'Shan State'
                else:
                    dest.region = 'Unknown Region'
                
                dest.save()
                fixed_count += 1
                self.stdout.write(f"  ✅ Fixed: {dest.name} → region: {dest.region}")
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ SUCCESSFULLY FIXED {fixed_count} DESTINATIONS"))
        
        # Show updated regions after fix
        self.stdout.write("\n📊 UPDATED REGIONS IN DATABASE:")
        updated_regions = Destination.objects.values_list('region', flat=True).distinct().order_by('region')
        for region in sorted(updated_regions):
            if region:
                cities = Destination.objects.filter(region=region, type__in=['city', 'town']).count()
                attractions = Destination.objects.filter(region=region, type='attraction').count()
                self.stdout.write(f"  - {region}: {cities} cities/towns, {attractions} attractions")