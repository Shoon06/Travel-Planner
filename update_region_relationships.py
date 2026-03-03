# C:\Users\ASUS\MyanmarTravelPlanner\update_region_relationships.py

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Destination

def update_region_relationships():
    print("=" * 70)
    print("MYANMAR TRAVEL PLANNER - REGION RELATIONSHIP UPDATER")
    print("=" * 70)
    
    # =========================================================
    # STEP 1: First, identify and mark ALL regions/states
    # =========================================================
    print("\n📌 STEP 1: Marking regions and states...")
    print("-" * 50)
    
    # List of all regions/states from your database
    regions_and_states = [
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
        
        # Also mark the ones without "State" or "Region" in name
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
    for region_name in regions_and_states:
        try:
            region = Destination.objects.get(name=region_name)
            region.is_region = True
            region.save()
            print(f"✅ Marked as region: {region_name}")
            region_count += 1
        except Destination.DoesNotExist:
            print(f"❌ Not found in database: {region_name}")
    
    print(f"\n📊 Total regions/states marked: {region_count}")
    
    # =========================================================
    # STEP 2: Link cities/towns to their parent states/regions
    # =========================================================
    print("\n" + "=" * 70)
    print("📌 STEP 2: Linking cities and towns to their parent regions...")
    print("=" * 70)
    
    # Dictionary mapping: 'City/Town Name' : 'Parent Region Name'
    city_to_region = {
        # Shan State cities and towns
        'Taunggyi': 'Shan State',
        'Heho': 'Shan State',
        'Hsipaw': 'Shan State',
        'Kalaw': 'Shan State',
        'Nyaungshwe': 'Shan State',
        'Tachileik': 'Shan State',
        'Lashio': 'Shan State',
        'Kengtung': 'Shan State',
        'Muse': 'Shan State',
        'Namhsan': 'Shan State',
        'Kyaukme': 'Shan State',
        
        # Yangon Region cities and towns
        'Yangon': 'Yangon Region',
        'ThanLwin': 'Yangon Region',
        'HmawBi': 'Yangon Region',
        'Dagon': 'Yangon Region',
        'Bahan': 'Yangon Region',
        'Sanchaung': 'Yangon Region',
        'Tamwe': 'Yangon Region',
        'Thanlyin': 'Yangon Region',
        'Twante': 'Yangon Region',
        
        # Mandalay Region cities and towns
        'Mandalay': 'Mandalay Region',
        'Pyin Oo Lwin': 'Mandalay Region',
        'Meiktila': 'Mandalay Region',
        'Amarapura': 'Mandalay Region',
        'Bagan': 'Mandalay Region',  # Bagan is in Mandalay Region
        'Myingyan': 'Mandalay Region',
        'Yamethin': 'Mandalay Region',
        'Kyaukse': 'Mandalay Region',
        
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
        'Kyauk Kalat': 'Kayin State',
        'Win Sein Taw Ya': 'Kayin State',
        
        # Chin State
        'Hakha': 'Chin State',
        'Falam': 'Chin State',
        
        # Mon State
        'Mawlamyine': 'Mon State',
        'Mudon': 'Mon State',
        'Thaton': 'Mon State',
        
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
                # Try exact match first
                parent = Destination.objects.get(name=parent_name)
            except Destination.DoesNotExist:
                # Try without "Region" or "State" suffix
                base_name = parent_name.replace(' Region', '').replace(' State', '')
                try:
                    parent = Destination.objects.get(name=base_name)
                except Destination.DoesNotExist:
                    print(f"❌ Parent region not found: {parent_name}")
                    error_count += 1
                    continue
            
            city.parent = parent
            city.is_region = False
            city.save()
            print(f"✅ Linked: {city_name} → {parent.name}")
            city_count += 1
            
        except Destination.DoesNotExist:
            print(f"❌ City not found: {city_name}")
            error_count += 1
    
    print(f"\n📊 Cities linked: {city_count}, Errors: {error_count}")
    
    # =========================================================
    # STEP 3: Link attractions to their parent cities/regions
    # =========================================================
    print("\n" + "=" * 70)
    print("📌 STEP 3: Linking attractions to their parent locations...")
    print("=" * 70)
    
    # Dictionary mapping: 'Attraction Name' : 'Parent Location Name'
    attraction_to_parent = {
        # Shan State attractions
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
        
        # Yangon attractions
        'Shwedagon Pagoda': 'Yangon',
        'Sule Pagoda': 'Yangon',
        'Botahtaung Pagoda': 'Yangon',
        'Kandawgyi Lake': 'Yangon',
        
        # Mandalay attractions
        'Mandalay Palace': 'Mandalay',
        'Mandalay Hill': 'Mandalay',
        'Kuthodaw Pagoda': 'Mandalay',
        'Maha Muni Buddha Temple': 'Mandalay',
        'U Bein Bridge': 'Amarapura',
        'Hsinbyume Pagoda': 'Mandalay',
        
        # Bagan attractions
        'Ananda Temple': 'Bagan',
        'Thatbyinnyu Temple': 'Bagan',
        'Dhammayangyi Temple': 'Bagan',
        'Shwezigon Pagoda': 'Bagan',
        'Mount Popa': 'Bagan',
        
        # Mon State attractions
        'Kyaiktiyo Pagoda': 'Mon State',
        'Kyauk Kalat Pagoda': 'Mawlamyine',
        'Win Sein Taw Ya': 'Mawlamyine',
        
        # Kayin State attractions
        'Kyauk Kalat': 'Hpa-An',
        
        # Rakhine State attractions
        'Ngapali Beach': 'Thandwe',
        'Mrauk U': 'Sittwe',
    }
    
    attraction_count = 0
    error_count = 0
    
    for attraction_name, parent_name in attraction_to_parent.items():
        try:
            attraction = Destination.objects.get(name=attraction_name)
            
            # Find parent (could be a city, town, or region)
            try:
                parent = Destination.objects.get(name=parent_name)
                attraction.parent = parent
                attraction.is_region = False
                attraction.save()
                print(f"✅ Linked: {attraction_name} → {parent.name}")
                attraction_count += 1
            except Destination.DoesNotExist:
                print(f"❌ Parent not found: {parent_name} for attraction {attraction_name}")
                error_count += 1
                
        except Destination.DoesNotExist:
            print(f"❌ Attraction not found: {attraction_name}")
            error_count += 1
    
    print(f"\n📊 Attractions linked: {attraction_count}, Errors: {error_count}")
    
    # =========================================================
    # STEP 4: Show the final hierarchy
    # =========================================================
    print("\n" + "=" * 70)
    print("📌 STEP 4: FINAL HIERARCHY - REGIONS AND THEIR PLACES")
    print("=" * 70)
    
    # Get all regions (is_region=True)
    regions = Destination.objects.filter(is_region=True).order_by('name')
    
    for region in regions:
        # Get all places with this region as parent
        places = Destination.objects.filter(parent=region).order_by('name')
        
        if places.exists():
            print(f"\n📍 {region.name} ({places.count()} places):")
            
            # Group by type for better organization
            cities = places.filter(type__in=['city', 'town'])
            attractions = places.filter(type='attraction')
            
            if cities.exists():
                print(f"   🏙️ Cities/Towns ({cities.count()}):")
                for city in cities[:5]:  # Show first 5
                    print(f"      • {city.name}")
                if cities.count() > 5:
                    print(f"      ... and {cities.count() - 5} more")
            
            if attractions.exists():
                print(f"   🏛️ Attractions ({attractions.count()}):")
                for attraction in attractions[:5]:  # Show first 5
                    print(f"      • {attraction.name}")
                if attractions.count() > 5:
                    print(f"      ... and {attractions.count() - 5} more")
    
    # =========================================================
    # STEP 5: Show cities that have attractions
    # =========================================================
    print("\n" + "=" * 70)
    print("📌 STEP 5: CITIES AND THEIR ATTRACTIONS")
    print("=" * 70)
    
    # Get all cities/towns that have children (attractions)
    cities = Destination.objects.filter(
        type__in=['city', 'town'],
        children__isnull=False
    ).distinct().order_by('name')
    
    for city in cities:
        attractions = city.children.filter(type='attraction')
        if attractions.exists():
            print(f"\n📍 {city.name} ({attractions.count()} attractions):")
            for attraction in attractions[:5]:
                print(f"   • {attraction.name}")
            if attractions.count() > 5:
                print(f"   ... and {attractions.count() - 5} more")
    
    print("\n" + "=" * 70)
    print("✅ UPDATE COMPLETE!")
    print("=" * 70)

if __name__ == "__main__":
    update_region_relationships()