# C:\Users\ASUS\MyanmarTravelPlanner\setup_complete_hierarchy.py

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Destination

def setup_hierarchy():
    print("=" * 70)
    print("SETTING UP COMPLETE DESTINATION HIERARCHY")
    print("=" * 70)
    
    # =========================================================
    # STEP 1: Mark all States and Regions as is_region = True
    # =========================================================
    print("\n📌 STEP 1: Marking States and Regions...")
    print("-" * 50)
    
    # List of all states and regions that should be top-level
    top_level_regions = [
        # States
        'Shan State',
        'Kachin State',
        'Kayah State',
        'Kayin State',
        'Chin State',
        'Mon State',
        'Rakhine State',
        
        # Regions
        'Yangon Region',
        'Mandalay Region',
        'Ayeyarwady Region',
        'Bago Region',
        'Magway Region',
        'Sagaing Region',
        'Tanintharyi Region',
        
        # Union Territory
        'Naypyidaw',
        
        # Also mark the ones without suffixes
        'Shan',
        'Kachin',
        'Kayah',
        'Kayin',
        'Chin',
        'Mon',
        'Rakhine',
        'Ayeyarwady',
        'Bago',
        'Magway',
        'Sagaing',
        'Tanintharyi',
        'Yangon',
        'Mandalay',
    ]
    
    region_count = 0
    for region_name in top_level_regions:
        try:
            region = Destination.objects.get(name=region_name)
            region.is_region = True
            region.save()
            print(f"✅ Marked as region: {region_name}")
            region_count += 1
        except Destination.DoesNotExist:
            print(f"❌ Not found: {region_name}")
    
    print(f"\n📊 Total regions marked: {region_count}")
    
    # =========================================================
    # STEP 2: Link Cities and Towns to their Parent Regions
    # =========================================================
    print("\n" + "=" * 70)
    print("📌 STEP 2: Linking Cities and Towns to Regions...")
    print("=" * 70)
    
    city_to_region = {
        # Shan State
        'Taunggyi': 'Shan State',
        'Heho': 'Shan State',
        'Hsipaw': 'Shan State',
        'Kalaw': 'Shan State',
        'Tachileik': 'Shan State',
        'Lashio': 'Shan State',
        'Kengtung': 'Shan State',
        'Muse': 'Shan State',
        'Namhsan': 'Shan State',
        'Kyaukme': 'Shan State',
        'Nyaungshwe': 'Shan State',
        
        # Yangon Region
        'Yangon': 'Yangon Region',
        'ThanLwin': 'Yangon Region',
        'HmawBi': 'Yangon Region',
        'Dagon': 'Yangon Region',
        'Bahan': 'Yangon Region',
        'Sanchaung': 'Yangon Region',
        'Tamwe': 'Yangon Region',
        'Thanlyin': 'Yangon Region',
        'Twante': 'Yangon Region',
        
        # Mandalay Region
        'Mandalay': 'Mandalay Region',
        'Pyin Oo Lwin': 'Mandalay Region',
        'Meiktila': 'Mandalay Region',
        'Amarapura': 'Mandalay Region',
        'Bagan': 'Mandalay Region',
        'Myingyan': 'Mandalay Region',
        'Yamethin': 'Mandalay Region',
        'Kyaukse': 'Mandalay Region',
        'Mount Popa': 'Mandalay Region',
        
        # Ayeyarwady Region
        'Pathein': 'Ayeyarwady Region',
        'Ngwe Saung Beach': 'Ayeyarwady Region',
        'Chaung Tha Beach': 'Ayeyarwady Region',
        
        # Bago Region
        'Bago': 'Bago Region',
        'Pyay': 'Bago Region',
        'Thaton': 'Bago Region',
        
        # Magway Region
        'Magway': 'Magway Region',
        'Pakokku': 'Magway Region',
        'Yenangyaung': 'Magway Region',
        'Chauk': 'Magway Region',
        
        # Sagaing Region
        'Sagaing': 'Sagaing Region',
        'Monywa': 'Sagaing Region',
        'Shwebo': 'Sagaing Region',
        'Kalay': 'Sagaing Region',
        
        # Tanintharyi Region
        'Tanintharyi': 'Tanintharyi Region',
        'Dawei': 'Tanintharyi Region',
        'Myeik': 'Tanintharyi Region',
        'Kawthaung': 'Tanintharyi Region',
        
        # Kachin State
        'Myitkyina': 'Kachin State',
        'Bhamo': 'Kachin State',
        'Mogaung': 'Kachin State',
        
        # Kayah State
        'Loikaw': 'Kayah State',
        
        # Kayin State
        'Hpa-An': 'Kayin State',
        
        # Chin State
        'Hakha': 'Chin State',
        'Falam': 'Chin State',
        
        # Mon State
        'Mawlamyine': 'Mon State',
        'Mudon': 'Mon State',
        
        # Rakhine State
        'Sittwe': 'Rakhine State',
        'Thandwe': 'Rakhine State',
        'Ngapali Beach': 'Rakhine State',
        'Mrauk U': 'Rakhine State',
        
        # Naypyidaw
        'Naypyidaw': 'Naypyidaw',
    }
    
    city_count = 0
    error_count = 0
    
    for city_name, parent_name in city_to_region.items():
        try:
            city = Destination.objects.get(name=city_name)
            
            # Find parent region
            try:
                parent = Destination.objects.get(name=parent_name)
                city.parent = parent
                city.is_region = False
                city.save()
                print(f"✅ Linked: {city_name} → {parent.name}")
                city_count += 1
            except Destination.DoesNotExist:
                # Try without "Region" or "State"
                base_name = parent_name.replace(' Region', '').replace(' State', '')
                try:
                    parent = Destination.objects.get(name=base_name)
                    city.parent = parent
                    city.is_region = False
                    city.save()
                    print(f"✅ Linked: {city_name} → {parent.name} (via {base_name})")
                    city_count += 1
                except Destination.DoesNotExist:
                    print(f"❌ Parent not found: {parent_name} for {city_name}")
                    error_count += 1
                    
        except Destination.DoesNotExist:
            print(f"❌ City not found: {city_name}")
            error_count += 1
    
    print(f"\n📊 Cities linked: {city_count}, Errors: {error_count}")
    
    # =========================================================
    # STEP 3: Link Attractions to their Parent Cities/Regions
    # =========================================================
    print("\n" + "=" * 70)
    print("📌 STEP 3: Linking Attractions to Cities/Regions...")
    print("=" * 70)
    
    attraction_to_parent = {
        # Shan State Attractions
        'Inle Lake': 'Shan State',
        'Kakku Pagodas': 'Taunggyi',
        'Shwe Bone Pwint Pagoda': 'Taunggyi',
        'Nga Phe Chaung Monastery': 'Taunggyi',
        'Htem Sann Cave': 'Taunggyi',
        'Kyaung Daw Pagoda': 'Taunggyi',
        'Sulamuni Lawka Chanthar Pagoda': 'Taunggyi',
        'Main Ma Ye Tha Khin Ma Mountain': 'Taunggyi',
        'Pindaya Caves': 'Shan State',
        'Indein Village': 'Inle Lake',
        
        # Yangon Attractions
        'Shwedagon Pagoda': 'Yangon',
        'Sule Pagoda': 'Yangon',
        'Botahtaung Pagoda': 'Yangon',
        'Kandawgyi Lake': 'Yangon',
        
        # Mandalay Attractions
        'Mandalay Palace': 'Mandalay',
        'Mandalay Hill': 'Mandalay',
        'Kuthodaw Pagoda': 'Mandalay',
        'Maha Muni Buddha Temple': 'Mandalay',
        'U Bein Bridge': 'Amarapura',
        'Hsinbyume Pagoda': 'Mandalay',
        
        # Bagan Attractions
        'Ananda Temple': 'Bagan',
        'Thatbyinnyu Temple': 'Bagan',
        'Dhammayangyi Temple': 'Bagan',
        'Shwezigon Pagoda': 'Bagan',
        'Mount Popa': 'Bagan',
        
        # Mon State Attractions
        'Kyaiktiyo Pagoda': 'Mon State',
        'Kyauk Kalat Pagoda': 'Mawlamyine',
        'Win Sein Taw Ya': 'Mawlamyine',
        
        # Kayin State Attractions
        'Kyauk Kalat': 'Hpa-An',
        
        # Rakhine State Attractions
        'Ngapali Beach': 'Thandwe',
        'Mrauk U': 'Sittwe',
        
        # Bago Region Attractions
        'Shwemawdaw Pagoda': 'Bago',
        'Shwethalyaung Buddha': 'Bago',
        
        # Sagaing Attractions
        'Thanboddhay Pagoda': 'Monywa',
        'Bodhi Tataung': 'Monywa',
    }
    
    attraction_count = 0
    error_count = 0
    
    for attraction_name, parent_name in attraction_to_parent.items():
        try:
            attraction = Destination.objects.get(name=attraction_name)
            
            # Find parent
            try:
                parent = Destination.objects.get(name=parent_name)
                attraction.parent = parent
                attraction.is_region = False
                attraction.save()
                print(f"✅ Linked: {attraction_name} → {parent.name}")
                attraction_count += 1
            except Destination.DoesNotExist:
                print(f"❌ Parent not found: {parent_name} for {attraction_name}")
                error_count += 1
                
        except Destination.DoesNotExist:
            print(f"❌ Attraction not found: {attraction_name}")
            error_count += 1
    
    print(f"\n📊 Attractions linked: {attraction_count}, Errors: {error_count}")
    
    # =========================================================
    # STEP 4: Show Complete Hierarchy
    # =========================================================
    print("\n" + "=" * 70)
    print("📌 STEP 4: COMPLETE HIERARCHY")
    print("=" * 70)
    
    # Get all top-level regions (is_region=True and no parent)
    top_regions = Destination.objects.filter(is_region=True, parent__isnull=True).order_by('name')
    
    for region in top_regions:
        # Get all direct children of this region
        cities = Destination.objects.filter(parent=region, type__in=['city', 'town']).order_by('name')
        direct_attractions = Destination.objects.filter(parent=region, type='attraction').order_by('name')
        
        print(f"\n📍 {region.name} ({region.type})")
        
        if cities.exists():
            print(f"   🏙️ Cities/Towns ({cities.count()}):")
            for city in cities:
                print(f"      • {city.name}")
                
                # Get attractions in this city
                city_attractions = Destination.objects.filter(parent=city, type='attraction')
                if city_attractions.exists():
                    for attraction in city_attractions:
                        print(f"         📍 {attraction.name}")
        
        if direct_attractions.exists():
            print(f"   🏛️ Direct Attractions ({direct_attractions.count()}):")
            for attraction in direct_attractions:
                print(f"      • {attraction.name}")
    
    # =========================================================
    # STEP 5: Summary Statistics
    # =========================================================
    print("\n" + "=" * 70)
    print("📌 STEP 5: SUMMARY STATISTICS")
    print("=" * 70)
    
    total_regions = Destination.objects.filter(is_region=True).count()
    total_cities = Destination.objects.filter(type__in=['city', 'town']).count()
    total_attractions = Destination.objects.filter(type='attraction').count()
    linked_places = Destination.objects.filter(parent__isnull=False).count()
    
    print(f"Total Regions/States: {total_regions}")
    print(f"Total Cities/Towns: {total_cities}")
    print(f"Total Attractions: {total_attractions}")
    print(f"Linked Places (have parent): {linked_places}")
    print(f"Unlinked Places: {Destination.objects.count() - linked_places}")
    
    print("\n" + "=" * 70)
    print("✅ HIERARCHY SETUP COMPLETE!")
    print("=" * 70)

if __name__ == "__main__":
    setup_hierarchy()