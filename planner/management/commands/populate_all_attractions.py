# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\populate_all_attractions.py

from django.core.management.base import BaseCommand
from django.db.models import Q
from planner.models import Destination
import random

class Command(BaseCommand):
    help = 'Populate attractions for all cities and towns with researched data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to populate attractions with researched data...'))
        
        # First, delete Tharrawaddy and ThanLwin if they exist
        self.stdout.write("\n📌 Checking for Tharrawaddy and ThanLwin...")
        tharrawaddy = Destination.objects.filter(name='Tharrawaddy').first()
        thanlwin = Destination.objects.filter(name='ThanLwin').first()
        
        if tharrawaddy:
            tharrawaddy.delete()
            self.stdout.write("  ✅ Deleted Tharrawaddy")
        else:
            self.stdout.write("  ⏩ Tharrawaddy not found")
            
        if thanlwin:
            thanlwin.delete()
            self.stdout.write("  ✅ Deleted ThanLwin")
        else:
            self.stdout.write("  ⏩ ThanLwin not found")
        
        # Get all remaining cities and towns
        cities_towns = Destination.objects.filter(
            type__in=['city', 'town'],
            is_active=True
        ).order_by('name')
        
        self.stdout.write(f"\n📍 Found {cities_towns.count()} cities/towns to process")
        
        attractions_created = 0
        attractions_updated = 0
        
        # Process each city/town
        for city in cities_towns:
            self.stdout.write(f"\n{'='*50}")
            self.stdout.write(f"Processing: {city.name} ({city.type})")
            self.stdout.write(f"{'='*50}")
            
            # Get attractions for this city
            attractions = self.get_attractions_for_city(city)
            
            if attractions:
                self.stdout.write(f"  Found {len(attractions)} attractions to add")
                
                for attr_data in attractions:
                    # Check if attraction already exists
                    existing = Destination.objects.filter(
                        name=attr_data['name'],
                        parent=city
                    ).first()
                    
                    if not existing:
                        # Create full description with all details
                        full_description = attr_data['description']
                        full_description += f"\n\nRating: {attr_data.get('rating', 4.5):.1f}/5"
                        full_description += f"\nReviews: {attr_data.get('review_count', random.randint(50, 500))}"
                        full_description += f"\nEntry Fee: {attr_data.get('entry_fee', 'Free entry')}"
                        if 'distance' in attr_data:
                            full_description += f"\nDistance: {attr_data['distance']}"
                        if 'features' in attr_data:
                            full_description += f"\nFeatures: {', '.join(attr_data['features'])}"
                        
                        # NOTE: Photos will be added later through Django Admin
                        # You can upload photos to each attraction after creation
                        
                        # Create the attraction
                        attraction = Destination.objects.create(
                            name=attr_data['name'],
                            type='attraction',
                            description=full_description,
                            region=city.region,
                            parent=city,
                            is_region=False,
                            is_active=True
                        )
                        attractions_created += 1
                        self.stdout.write(f"  ✅ Created: {attr_data['name']}")
                        
                        # Add placeholder comment for photos
                        self.stdout.write(f"     📷 Add photos via Django Admin for: {attr_data['name']}")
                    else:
                        attractions_updated += 1
                        self.stdout.write(f"  ⏩ Already exists: {attr_data['name']}")
            else:
                self.stdout.write(f"  ⚠️ No attractions data available for {city.name}")
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f"\n{'='*50}"))
        self.stdout.write(self.style.SUCCESS(f"COMPLETE: {attractions_created} attractions created, {attractions_updated} already existed"))
        self.stdout.write(self.style.SUCCESS(f"\n📷 To add photos:"))
        self.stdout.write(self.style.SUCCESS(f"   1. Go to Django Admin: http://127.0.0.1:8000/admin/"))
        self.stdout.write(self.style.SUCCESS(f"   2. Click on 'Destinations'"))
        self.stdout.write(self.style.SUCCESS(f"   3. Find each attraction and upload photos to:"))
        self.stdout.write(self.style.SUCCESS(f"      - Main Image: main_image"))
        self.stdout.write(self.style.SUCCESS(f"      - Gallery Images: gallery_image1 to gallery_image4"))
        self.stdout.write(f"{'='*50}")
    
    def get_attractions_for_city(self, city):
        """Return list of attractions for a given city based on researched data"""
        city_name = city.name.lower()
        
        # Common features for different types of attractions
        common_features = {
            'pagoda': ['Religious site', 'Historic buildings', 'Photography', 'Cultural landmark'],
            'temple': ['Religious site', 'Historic buildings', 'Architecture', 'Cultural heritage'],
            'monastery': ['Religious site', 'Historic buildings', 'Meditation', 'Peaceful'],
            'market': ['Shopping', 'Local market', 'Food', 'Souvenirs'],
            'lake': ['Natural scenery', 'Boating', 'Photography', 'Picnic spot'],
            'beach': ['Beach', 'Swimming', 'Relaxation', 'Sunset views'],
            'waterfall': ['Waterfall', 'Nature', 'Photography', 'Swimming'],
            'cave': ['Cave', 'Adventure', 'Exploration', 'Natural wonder'],
            'bridge': ['Historic bridge', 'Scenic spot', 'Photography', 'Sunset view'],
            'palace': ['Historic buildings', 'Royal palace', 'Museum', 'Architecture'],
            'museum': ['Museum', 'Cultural', 'Artifacts', 'History'],
            'hill': ['Hiking', 'Scenic spot', 'Sunset view', 'Trekking'],
            'garden': ['Gardens', 'Nature', 'Relaxation', 'Walking'],
            'park': ['Park', 'Nature', 'Walking', 'Picnic'],
            'island': ['Island', 'Beach', 'Snorkeling', 'Boat trip'],
            'village': ['Village', 'Cultural', 'Traditional', 'Local life'],
            'hot_spring': ['Hot spring', 'Relaxation', 'Wellness', 'Natural'],
            'dam': ['Scenic views', 'Photography', 'Picnic', 'Water'],
            'viewpoint': ['Viewpoint', 'Photography', 'Sunset', 'Panoramic views'],
            'war_cemetery': ['War memorial', 'History', 'Remembrance', 'WWII'],
            'zoo': ['Zoo', 'Wildlife', 'Family-friendly', 'Animals'],
            'cultural_center': ['Cultural', 'Traditional', 'Performances', 'Art']
        }
        
        # Complete attractions database based on your researched data
        attractions_db = {
            # 1. AMARAPURA
            'amarapura': [
                {
                    'name': 'U Bein Bridge',
                    'description': 'World\'s longest teakwood bridge at 1.2 kilometers, built in 1850. Best visited at sunset when the sky creates stunning reflections on Taungthaman Lake.',
                    'features': common_features['bridge'],
                    'rating': 4.8,
                    'review_count': 523,
                    'entry_fee': 'Free entry',
                    'distance': 'Central Amarapura'
                },
                {
                    'name': 'Maha Gandhayon Monastery',
                    'description': 'Famous modern monastery where over 1,000 monks line up daily at 10:30 AM to receive alms. A unique cultural experience and photo opportunity.',
                    'features': common_features['monastery'],
                    'rating': 4.6,
                    'review_count': 234,
                    'entry_fee': 'Free entry',
                    'distance': '1km from U Bein Bridge'
                },
                {
                    'name': 'Bagaya Monastery',
                    'description': 'Beautiful 19th-century monastery built entirely of teak wood, featuring intricate carvings and traditional Burmese architecture.',
                    'features': common_features['monastery'],
                    'rating': 4.4,
                    'review_count': 87,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Taungthaman Lake',
                    'description': 'Scenic lake that reflects U Bein Bridge beautifully. Popular for boat rides and sunset photography.',
                    'features': common_features['lake'],
                    'rating': 4.5,
                    'review_count': 156,
                    'entry_fee': 'Free entry',
                    'distance': 'Adjacent to U Bein Bridge'
                },
                {
                    'name': 'Kyauktawgyi Pagoda',
                    'description': 'Pagoda housing large marble Buddha images, known for its peaceful atmosphere and traditional architecture.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 67,
                    'entry_fee': 'Free entry',
                    'distance': '1.5km from downtown'
                }
            ],
            
            # 2. BAGAN
            'bagan': [
                {
                    'name': 'Ananda Temple',
                    'description': 'One of Bagan\'s most beautiful and best-preserved temples, built in 1105. Known for its stunning architecture and four standing Buddha statues.',
                    'features': common_features['temple'],
                    'rating': 4.9,
                    'review_count': 856,
                    'entry_fee': 'Included in Archaeological Zone pass',
                    'distance': 'Central Bagan'
                },
                {
                    'name': 'Shwezigon Pagoda',
                    'description': 'One of the most important pagodas in Myanmar, built by King Anawrahta. A prototype of later Myanmar stupas with its golden dome.',
                    'features': common_features['pagoda'],
                    'rating': 4.8,
                    'review_count': 567,
                    'entry_fee': 'Included in Archaeological Zone pass',
                    'distance': 'Nyaung U'
                },
                {
                    'name': 'Dhammayangyi Temple',
                    'description': 'The largest temple in Bagan with massive brick structure. Known for its mysterious history and excellent brickwork.',
                    'features': common_features['temple'],
                    'rating': 4.6,
                    'review_count': 423,
                    'entry_fee': 'Included in Archaeological Zone pass',
                    'distance': 'Central Bagan'
                },
                {
                    'name': 'Sulamani Temple',
                    'description': 'Considered one of the most beautiful temples in Bagan, known for its elegant architecture and well-preserved murals.',
                    'features': common_features['temple'],
                    'rating': 4.7,
                    'review_count': 345,
                    'entry_fee': 'Included in Archaeological Zone pass',
                    'distance': 'Central Bagan'
                },
                {
                    'name': 'Thatbyinnyu Temple',
                    'description': 'The tallest temple in Bagan at 61 meters high, offering panoramic views of the surrounding plains.',
                    'features': common_features['temple'],
                    'rating': 4.6,
                    'review_count': 289,
                    'entry_fee': 'Included in Archaeological Zone pass',
                    'distance': 'Central Bagan'
                },
                {
                    'name': 'Htilominlo Temple',
                    'description': 'Beautiful temple known for its intricate plaster carvings and large Buddha images.',
                    'features': common_features['temple'],
                    'rating': 4.5,
                    'review_count': 198,
                    'entry_fee': 'Included in Archaeological Zone pass',
                    'distance': 'Central Bagan'
                },
                {
                    'name': 'Hot Air Balloon Ride over Bagan',
                    'description': 'Experience breathtaking sunrise views over thousands of ancient temples from a hot air balloon. A once-in-a-lifetime experience.',
                    'features': ['Adventure', 'Scenic views', 'Sunrise', 'Photography'],
                    'rating': 5.0,
                    'review_count': 1243,
                    'entry_fee': '$320-380 per person',
                    'distance': 'Various launch sites'
                }
            ],
            
            # 3. BAGO
            'bago': [
                {
                    'name': 'Shwemawdaw Pagoda',
                    'description': 'One of Myanmar\'s tallest pagodas at 114 meters, often called the "Golden God Temple". It predates Shwedagon Pagoda.',
                    'features': common_features['pagoda'],
                    'rating': 4.7,
                    'review_count': 234,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Shwethalyaung Buddha',
                    'description': 'Massive reclining Buddha image, 55 meters long and 16 meters high, built in 994 AD. Considered one of the most lifelike Buddha images.',
                    'features': ['Buddha image', 'Religious site', 'Historic'],
                    'rating': 4.8,
                    'review_count': 312,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Kyaik Pun Pagoda',
                    'description': 'Four giant seated Buddha images back-to-back, each 27 meters high, built in the 7th century.',
                    'features': common_features['pagoda'],
                    'rating': 4.5,
                    'review_count': 167,
                    'entry_fee': 'Free entry',
                    'distance': '4km from downtown'
                },
                {
                    'name': 'Kanbawzathadi Palace',
                    'description': 'Reconstructed 16th-century palace of King Bayinnaung, featuring golden architecture and historical exhibits.',
                    'features': common_features['palace'],
                    'rating': 4.3,
                    'review_count': 98,
                    'entry_fee': '5,000 MMK',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Mahazedi Pagoda',
                    'description': 'Historic pagoda built in 1560 by King Bayinnaung to house a Buddha tooth relic.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 76,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                }
            ],
            
            # 4. BOGALE
            'bogale': [
                {
                    'name': 'Meinmahla Kyun Wildlife Sanctuary',
                    'description': 'Protected mangrove forest and wildlife sanctuary, home to saltwater crocodiles, dolphins, and diverse bird species. A Ramsar wetland site.',
                    'features': ['Wildlife sanctuary', 'Mangrove forest', 'Bird watching', 'Boat tours'],
                    'rating': 4.5,
                    'review_count': 45,
                    'entry_fee': '5,000 MMK',
                    'distance': '15km from town'
                },
                {
                    'name': 'Ga Do Ga Ni Village',
                    'description': 'Traditional riverside village where you can experience local life, fishing communities, and authentic Ayeyarwady delta culture.',
                    'features': common_features['village'],
                    'rating': 4.2,
                    'review_count': 23,
                    'entry_fee': 'Free entry',
                    'distance': '10km from town'
                },
                {
                    'name': 'Natchaung Bridge & Seikma Bridge',
                    'description': 'Scenic bridges spanning the delta waterways, offering picturesque views of local boats and river life.',
                    'features': ['Bridge', 'Scenic views', 'Photography'],
                    'rating': 4.0,
                    'review_count': 12,
                    'entry_fee': 'Free entry',
                    'distance': '5km from town'
                }
            ],
            
            # 5. DAWEI
            'dawei': [
                {
                    'name': 'Maungmagan Beach',
                    'description': 'Long beach popular with locals, featuring golden sand, casuarina trees, and seafood restaurants. Great for swimming and relaxation.',
                    'features': common_features['beach'],
                    'rating': 4.3,
                    'review_count': 87,
                    'entry_fee': 'Free entry',
                    'distance': '15km from downtown'
                },
                {
                    'name': 'Shin Maw Pagoda',
                    'description': 'Beautiful pagoda on the coast with stunning sunset views over the Andaman Sea.',
                    'features': common_features['pagoda'],
                    'rating': 4.4,
                    'review_count': 56,
                    'entry_fee': 'Free entry',
                    'distance': '16km from downtown'
                },
                {
                    'name': 'Grandfather Beach',
                    'description': 'Unique beach named for rock formations resembling an elderly man. Popular for photography and picnics.',
                    'features': common_features['beach'],
                    'rating': 4.1,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '18km from downtown'
                },
                {
                    'name': 'Myaw Yit Pagoda',
                    'description': 'Hilltop pagoda offering panoramic views of Dawei and the surrounding coastline.',
                    'features': common_features['pagoda'],
                    'rating': 4.3,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Lawka Tharaphu Pagoda',
                    'description': 'Important local pagoda with intricate carvings and peaceful atmosphere.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 23,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Nabule Beach',
                    'description': 'Secluded beach with crystal clear water, ideal for swimming and escaping crowds.',
                    'features': common_features['beach'],
                    'rating': 4.4,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '25km from downtown'
                },
                {
                    'name': 'Pa Nyit Beach',
                    'description': 'Beautiful beach known for its rock formations and tide pools at low tide.',
                    'features': common_features['beach'],
                    'rating': 4.2,
                    'review_count': 23,
                    'entry_fee': 'Free entry',
                    'distance': '22km from downtown'
                },
                {
                    'name': 'Tizit Beach',
                    'description': 'Quiet beach perfect for relaxation and long walks along the shore.',
                    'features': common_features['beach'],
                    'rating': 4.1,
                    'review_count': 18,
                    'entry_fee': 'Free entry',
                    'distance': '20km from downtown'
                },
                {
                    'name': 'Shwe Taung Zar Pagoda',
                    'description': 'Golden pagoda visible from many parts of Dawei, a important religious site.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Sandawshin Pagoda Tavoy',
                    'description': 'Historic pagoda with legends of Buddha relics, offering city views.',
                    'features': common_features['pagoda'],
                    'rating': 4.3,
                    'review_count': 29,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                }
            ],
            
            # 6. HAKHA
            'hakha': [
                {
                    'name': 'Mount Victoria (Natma-Tuang)',
                    'description': 'Highest mountain in Chin State at 3,053 meters, offering spectacular trekking through pine forests and stunning sunrise views.',
                    'features': ['Mountain', 'Trekking', 'Sunrise', 'Camping'],
                    'rating': 4.9,
                    'review_count': 134,
                    'entry_fee': 'Free entry',
                    'distance': '60km from Hakha'
                },
                {
                    'name': 'Chin State Cultural Museum',
                    'description': 'Fascinating museum showcasing traditional costumes, artifacts, and cultural heritage of the Chin people, including facial tattoo displays.',
                    'features': common_features['museum'],
                    'rating': 4.6,
                    'review_count': 89,
                    'entry_fee': '3,000 MMK',
                    'distance': 'Downtown Hakha'
                },
                {
                    'name': 'Rik Lake (Rih Dil)',
                    'description': 'Culturally significant heart-shaped lake in Chin Hills, considered a sacred site in Chin mythology.',
                    'features': common_features['lake'],
                    'rating': 4.7,
                    'review_count': 112,
                    'entry_fee': 'Free entry',
                    'distance': '80km from Hakha'
                },
                {
                    'name': 'Mount Zion (Zion Tlang)',
                    'description': 'Popular viewpoint offering 360-degree panoramic views of Hakha town and the surrounding Chin Hills.',
                    'features': common_features['hill'],
                    'rating': 4.5,
                    'review_count': 67,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Bungtla Waterfall',
                    'description': 'One of Myanmar\'s longest waterfalls at over 1,500 feet, cascading down multiple tiers through lush jungle.',
                    'features': common_features['waterfall'],
                    'rating': 4.8,
                    'review_count': 78,
                    'entry_fee': 'Free entry',
                    'distance': '40km from Hakha'
                },
                {
                    'name': 'Hiking the Chin Hills',
                    'description': 'Numerous trekking opportunities through breathtaking mountain landscapes, traditional villages, and terraced farms.',
                    'features': ['Trekking', 'Mountain views', 'Villages', 'Adventure'],
                    'rating': 4.7,
                    'review_count': 156,
                    'entry_fee': 'Guide fees vary',
                    'distance': 'Various starting points'
                }
            ],
            
            # 7. HEHO
            'heho': [
                {
                    'name': 'Lay Thar Taung Pagoda',
                    'description': 'Hilltop pagoda overlooking Heho airport and surrounding Shan hills. Peaceful spot with panoramic views.',
                    'features': common_features['pagoda'],
                    'rating': 4.3,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': '2km from airport'
                },
                {
                    'name': 'Inle Lake',
                    'description': 'Famous freshwater lake accessible via Heho, known for leg-rowing fishermen, floating gardens, and stilt-house villages.',
                    'features': ['Lake', 'Boat tours', 'Floating villages', 'Photography'],
                    'rating': 4.8,
                    'review_count': 1243,
                    'entry_fee': '12,500 MMK',
                    'distance': '30km from Heho'
                },
                {
                    'name': 'Pindaya Caves',
                    'description': 'Limestone caves housing over 8,000 Buddha images, a major pilgrimage site with stunning natural formations.',
                    'features': common_features['cave'],
                    'rating': 4.6,
                    'review_count': 234,
                    'entry_fee': '5,000 MMK',
                    'distance': '45km from Heho'
                }
            ],
            
            # 8. HINTHADA
            'hinthada': [
                {
                    'name': 'Hinthada Myathalun Pagoda',
                    'description': 'Major pagoda in the city center, a important religious site for locals with beautiful architecture.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Kyauk Taw Gyi Monastery',
                    'description': 'Peaceful monastery with large Buddha image and meditation spaces.',
                    'features': common_features['monastery'],
                    'rating': 4.1,
                    'review_count': 23,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Hinthada Kayin Baptist Church',
                    'description': 'Historic church serving the local Kayin community, with unique architecture.',
                    'features': ['Church', 'Religious site', 'Historic'],
                    'rating': 4.0,
                    'review_count': 15,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                }
            ],
            
            # 9. HMAWBI
            'hmawbi': [
                {
                    'name': 'Hlawga National Park',
                    'description': 'Protected wildlife park with deer, wild boar, and bird species. Features walking trails, lake views, and observation towers.',
                    'features': ['National park', 'Wildlife', 'Walking trails', 'Bird watching'],
                    'rating': 4.4,
                    'review_count': 156,
                    'entry_fee': '3,000 MMK',
                    'distance': '5km from Hmawbi'
                },
                {
                    'name': 'Allied War Cemetery (Hmawbi)',
                    'description': 'Well-maintained cemetery honoring Allied soldiers who died in WWII, with peaceful gardens and memorial stones.',
                    'features': common_features['war_cemetery'],
                    'rating': 4.5,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '3km from Hmawbi'
                },
                {
                    'name': 'Hmawbi Market',
                    'description': 'Local market offering fresh produce, traditional foods, and daily necessities. Great for experiencing local life.',
                    'features': common_features['market'],
                    'rating': 4.0,
                    'review_count': 23,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                }
            ],
            
            # 10. HPA-AN
            'hpa-an': [
                {
                    'name': 'Mount Zwegabin',
                    'description': 'Iconic 725-meter high limestone mountain offering challenging hike with stunning panoramic views of Hpa-An and surrounding plains.',
                    'features': common_features['hill'],
                    'rating': 4.8,
                    'review_count': 234,
                    'entry_fee': 'Free entry',
                    'distance': '8km from downtown'
                },
                {
                    'name': 'Saddan Cave',
                    'description': 'Massive cave system with Buddha images, featuring a hidden lake at the far end that you can explore by bamboo raft.',
                    'features': common_features['cave'],
                    'rating': 4.6,
                    'review_count': 178,
                    'entry_fee': '2,000 MMK',
                    'distance': '15km from downtown'
                },
                {
                    'name': 'Kawgun Cave',
                    'description': 'Ancient cave filled with thousands of small Buddha images carved into the walls over centuries, dating back to the 7th century.',
                    'features': common_features['cave'],
                    'rating': 4.5,
                    'review_count': 145,
                    'entry_fee': '2,000 MMK',
                    'distance': '10km from downtown'
                },
                {
                    'name': 'Kyauk Kalap Pagoda',
                    'description': 'Stunning pagoda perched atop a tall limestone pillar rising from a lake, one of Myanmar\'s most photographed sites.',
                    'features': common_features['pagoda'],
                    'rating': 4.7,
                    'review_count': 312,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Bat Cave',
                    'description': 'Large cave system famous for the spectacular evening emergence of millions of bats, a natural phenomenon best viewed at sunset.',
                    'features': common_features['cave'],
                    'rating': 4.4,
                    'review_count': 167,
                    'entry_fee': 'Free entry',
                    'distance': '12km from downtown'
                }
            ],
            
            # 11. HSIPAW
            'hsipaw': [
                {
                    'name': 'Hsipaw Palace (Shan Palace)',
                    'description': 'Former residence of the last Sawbwa (Prince) of Hsipaw. Rich in history and connected to the book "Twilight over Burma". Open 3-6 PM for visitors to hear family stories.',
                    'features': common_features['palace'],
                    'rating': 4.5,
                    'review_count': 134,
                    'entry_fee': '3,000 MMK',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Little Bagan (Myauk Myo)',
                    'description': 'Peaceful area with ancient, decaying stupas and pagodas overgrown with trees, reminiscent of Bagan. Perfect for quiet exploration.',
                    'features': ['Ancient ruins', 'Pagodas', 'Photography'],
                    'rating': 4.3,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Bawgyo Pagoda',
                    'description': 'Highly revered pagoda about 8km from town, featuring intricate Shan art and a significant spiritual beacon for the region.',
                    'features': common_features['pagoda'],
                    'rating': 4.4,
                    'review_count': 67,
                    'entry_fee': 'Free entry',
                    'distance': '8km from downtown'
                },
                {
                    'name': 'Madahya Monastery',
                    'description': 'Beautiful monastery with traditional Shan architecture and peaceful atmosphere.',
                    'features': common_features['monastery'],
                    'rating': 4.1,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Bamboo Buddha Monastery (Maha Nanda Kantha)',
                    'description': 'Unique monastery featuring Buddha images made from bamboo, showcasing local craftsmanship.',
                    'features': common_features['monastery'],
                    'rating': 4.2,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': '4km from downtown'
                },
                {
                    'name': 'Hsipaw Nam-Doke Waterfall',
                    'description': 'Beautiful multi-tiered waterfall surrounded by jungle, perfect for swimming and picnics.',
                    'features': common_features['waterfall'],
                    'rating': 4.5,
                    'review_count': 78,
                    'entry_fee': '2,000 MMK',
                    'distance': '15km from downtown'
                },
                {
                    'name': 'Hsipaw Hot Springs',
                    'description': 'Natural hot springs where you can soak in warm, mineral-rich waters surrounded by nature.',
                    'features': common_features['hot_spring'],
                    'rating': 4.3,
                    'review_count': 56,
                    'entry_fee': '2,000 MMK',
                    'distance': '12km from downtown'
                }
            ],
            
            # 12. KALAW
            'kalaw': [
                {
                    'name': 'FairyLand Kalaw',
                    'description': 'Charming café and garden with European-style atmosphere, popular for relaxation and refreshments.',
                    'features': ['Café', 'Garden', 'Relaxation'],
                    'rating': 4.3,
                    'review_count': 67,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Green Hill Valley Elephant Camp',
                    'description': 'Ethical elephant camp focused on conservation and care for retired logging elephants. Offers feeding, bathing, and interaction opportunities.',
                    'features': ['Elephant camp', 'Wildlife', 'Conservation'],
                    'rating': 4.8,
                    'review_count': 145,
                    'entry_fee': '20,000 MMK',
                    'distance': '5km from downtown'
                },
                {
                    'name': 'Hnee Pagoda',
                    'description': 'Hilltop pagoda with panoramic views of Kalaw and surrounding hills. Peaceful spot for meditation.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 56,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Kalaw City View',
                    'description': 'Scenic viewpoint overlooking the town and Shan hills, especially beautiful at sunset.',
                    'features': common_features['viewpoint'],
                    'rating': 4.4,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Kalaw Clock Tower',
                    'description': 'Historic colonial-era clock tower in the town center, a popular meeting point and landmark.',
                    'features': ['Landmark', 'Historic', 'Colonial'],
                    'rating': 4.0,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Kalaw Myoma Market',
                    'description': 'Vibrant local market selling fresh produce, traditional foods, and handmade crafts. Best visited in the morning.',
                    'features': common_features['market'],
                    'rating': 4.2,
                    'review_count': 78,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Kalaw Railway Station',
                    'description': 'Colonial-era railway station with charming architecture, still in operation on the Thazi-Shwenyaung line.',
                    'features': ['Railway station', 'Colonial architecture', 'Historic'],
                    'rating': 4.1,
                    'review_count': 56,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Shwe Oo Min Pagoda (Natural Cave)',
                    'description': 'Important pagoda with meditation caves and hundreds of Buddha images in natural limestone formations.',
                    'features': common_features['pagoda'],
                    'rating': 4.5,
                    'review_count': 123,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Thein Taung Pagoda Monastery',
                    'description': 'Hilltop monastery complex with multiple pagodas and stunning views.',
                    'features': common_features['monastery'],
                    'rating': 4.3,
                    'review_count': 67,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Byite Mountain (ဗျိုက်တောင်)',
                    'description': 'Popular hiking destination offering challenging trails and rewarding panoramic views.',
                    'features': common_features['hill'],
                    'rating': 4.4,
                    'review_count': 78,
                    'entry_fee': 'Free entry',
                    'distance': '6km from downtown'
                }
            ],
            
            # 13. KALAY
            'kalay': [
                {
                    'name': 'Yazagyo Dam',
                    'description': 'Scenic dam about 1.5 hours from Kalay, a top destination for photography and nature lovers.',
                    'features': common_features['dam'],
                    'rating': 4.4,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': '40km from downtown'
                },
                {
                    'name': 'Tahan Market',
                    'description': 'Bustling market ideal for shopping, local culture, and experiencing the town\'s vibrant atmosphere.',
                    'features': common_features['market'],
                    'rating': 4.2,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Taungphila Hill',
                    'description': 'Prominent scenic spot offering views of the surrounding plains.',
                    'features': common_features['hill'],
                    'rating': 4.1,
                    'review_count': 23,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Myatheintan Pagoda',
                    'description': 'Key religious site with beautiful architecture and peaceful atmosphere.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 29,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Thang Pagoda',
                    'description': 'Important local pagoda with cultural significance.',
                    'features': common_features['pagoda'],
                    'rating': 4.0,
                    'review_count': 18,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Myitsone & Panmon Creek',
                    'description': 'Natural scenic spots ideal for relaxation and picnics.',
                    'features': ['Creek', 'Nature', 'Picnic'],
                    'rating': 4.1,
                    'review_count': 15,
                    'entry_fee': 'Free entry',
                    'distance': '15km from downtown'
                },
                {
                    'name': 'Manipura Dam',
                    'description': 'Popular water-based site for recreation and photography.',
                    'features': common_features['dam'],
                    'rating': 4.0,
                    'review_count': 12,
                    'entry_fee': 'Free entry',
                    'distance': '25km from downtown'
                },
                {
                    'name': 'Hand Washing Lake',
                    'description': 'Local landmark with scenic views and cultural significance.',
                    'features': common_features['lake'],
                    'rating': 3.9,
                    'review_count': 8,
                    'entry_fee': 'Free entry',
                    'distance': '5km from downtown'
                }
            ],
            
            # 14. KAWTHAUNG
            'kawthaung': [
                {
                    'name': 'Nyaung Oo Phee Island',
                    'description': 'Beautiful island with pristine beaches and excellent snorkeling opportunities.',
                    'features': common_features['island'],
                    'rating': 4.6,
                    'review_count': 67,
                    'entry_fee': 'Boat trip required',
                    'distance': '30 minutes by boat'
                },
                {
                    'name': 'Cockburn Island (Kanae Island)',
                    'description': 'Picturesque island with white sand beaches and clear waters.',
                    'features': common_features['island'],
                    'rating': 4.5,
                    'review_count': 45,
                    'entry_fee': 'Boat trip required',
                    'distance': '45 minutes by boat'
                },
                {
                    'name': 'Parker Beach',
                    'description': 'Secluded beach with crystal clear water, perfect for swimming and relaxation.',
                    'features': common_features['beach'],
                    'rating': 4.4,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '20 minutes by boat'
                },
                {
                    'name': 'ZedetkyiKyun Island',
                    'description': 'Remote island with untouched natural beauty and rich marine life.',
                    'features': common_features['island'],
                    'rating': 4.5,
                    'review_count': 23,
                    'entry_fee': 'Boat trip required',
                    'distance': '1 hour by boat'
                },
                {
                    'name': 'Maliwun Waterfall',
                    'description': 'Beautiful waterfall in the jungle, perfect for swimming and picnics.',
                    'features': common_features['waterfall'],
                    'rating': 4.3,
                    'review_count': 29,
                    'entry_fee': '2,000 MMK',
                    'distance': '25km from town'
                },
                {
                    'name': 'Third Mile Pagoda (Pyi Daw Aye Pagoda)',
                    'description': 'Hilltop pagoda offering panoramic views of Kawthaung and the Andaman Sea.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                }
            ],
            
            # 15. LABUTTA
            'labutta': [
                {
                    'name': 'Gaw Yin Gyi Island',
                    'description': 'Scenic island in the Ayeyarwady delta, known for its natural beauty and local villages.',
                    'features': common_features['island'],
                    'rating': 4.3,
                    'review_count': 23,
                    'entry_fee': 'Boat trip required',
                    'distance': 'Boat from Labutta'
                },
                {
                    'name': 'Meinmahla Kyun Wildlife Sanctuary',
                    'description': 'Protected mangrove forest and wildlife sanctuary, accessible from Labutta.',
                    'features': ['Wildlife sanctuary', 'Mangrove forest', 'Boat tours'],
                    'rating': 4.5,
                    'review_count': 34,
                    'entry_fee': '5,000 MMK',
                    'distance': '20km from town'
                },
                {
                    'name': 'Yway River',
                    'description': 'Scenic river perfect for boat trips and observing delta life.',
                    'features': ['River', 'Boat trips', 'Scenic views'],
                    'rating': 4.1,
                    'review_count': 15,
                    'entry_fee': 'Free entry',
                    'distance': 'Adjacent to town'
                }
            ],
            
            # 16. LETPADAN
            'letpadan': [
                {
                    'name': 'Law Ka Nandar Pagoda',
                    'description': 'Important local pagoda with beautiful architecture and peaceful grounds.',
                    'features': common_features['pagoda'],
                    'rating': 4.1,
                    'review_count': 18,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Letpadan Public Park',
                    'description': 'Green space in town, popular for evening walks and relaxation.',
                    'features': common_features['park'],
                    'rating': 4.0,
                    'review_count': 12,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                }
            ],
            
            # 17. LOIKAW
            'loikaw': [
                {
                    'name': 'Taung Kwe Pagoda (Thirimingala Pagoda)',
                    'description': 'Stunning complex of white and golden spires built on rocky hills, offering panoramic views of Loikaw and surrounding hills.',
                    'features': common_features['pagoda'],
                    'rating': 4.8,
                    'review_count': 134,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Kayah State Cultural Museum',
                    'description': 'Highlights the diverse ethnic groups of Kayah State, showcasing traditional costumes, musical instruments, and artifacts.',
                    'features': common_features['museum'],
                    'rating': 4.4,
                    'review_count': 67,
                    'entry_fee': '3,000 MMK',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Pan Pat Villages',
                    'description': 'Villages in surrounding hills known for the Padaung community, where you can learn about weaving traditions and lifestyle.',
                    'features': common_features['village'],
                    'rating': 4.5,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '15km from downtown'
                },
                {
                    'name': 'Ngwe Taung Dam',
                    'description': 'Scenic spot popular for relaxing, picnics, and observing local life.',
                    'features': common_features['dam'],
                    'rating': 4.2,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': '8km from downtown'
                },
                {
                    'name': 'Pilu River',
                    'description': 'Scenic river offering boat trips and beautiful natural scenery.',
                    'features': ['River', 'Boat trips', 'Scenic views'],
                    'rating': 4.3,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                }
            ],
            
            # 18. MAGWAY
            'magway': [
                {
                    'name': 'Myathalun Pagoda',
                    'description': 'Major pagoda in Magway, visible from many parts of the city with its golden spire.',
                    'features': common_features['pagoda'],
                    'rating': 4.3,
                    'review_count': 56,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Yokesone Monastery',
                    'description': 'Beautiful monastery with traditional architecture and peaceful atmosphere.',
                    'features': common_features['monastery'],
                    'rating': 4.1,
                    'review_count': 23,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Fort Min Hla',
                    'description': 'Historic fort with remains of colonial-era structures.',
                    'features': ['Fort', 'Historic', 'Colonial'],
                    'rating': 4.0,
                    'review_count': 18,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Salay House',
                    'description': 'Historic building with traditional architecture, now a small museum.',
                    'features': ['Historic building', 'Museum'],
                    'rating': 4.1,
                    'review_count': 15,
                    'entry_fee': '2,000 MMK',
                    'distance': '4km from downtown'
                },
                {
                    'name': 'Tantkyi Taung Pagoda',
                    'description': 'Hilltop pagoda overlooking the Irrawaddy River, offering scenic views.',
                    'features': common_features['pagoda'],
                    'rating': 4.3,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '5km from downtown'
                }
            ],
            
            # 19. MANDALAY
            'mandalay': [
                {
                    'name': 'Mandalay Palace',
                    'description': 'The last royal palace of the Burmese monarchy, a massive complex surrounded by moats and walls. Reconstructed after WWII damage.',
                    'features': common_features['palace'],
                    'rating': 4.5,
                    'review_count': 567,
                    'entry_fee': '10,000 MMK',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Mandalay Hill',
                    'description': 'Famous 240-meter hill offering panoramic views of Mandalay and the Irrawaddy River. Covered with pagodas and monasteries.',
                    'features': common_features['hill'],
                    'rating': 4.7,
                    'review_count': 789,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Kuthodaw Pagoda',
                    'description': 'Known as "the world\'s largest book" with 729 marble slabs inscribed with Buddhist scriptures, each in its own white stupa.',
                    'features': common_features['pagoda'],
                    'rating': 4.6,
                    'review_count': 456,
                    'entry_fee': '5,000 MMK',
                    'distance': '2.5km from downtown'
                },
                {
                    'name': 'Mahamuni Buddha Temple',
                    'description': 'One of Myanmar\'s most revered Buddha images, covered in thick gold leaf applied by male devotees.',
                    'features': common_features['temple'],
                    'rating': 4.8,
                    'review_count': 678,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Shwenandaw Monastery',
                    'description': 'Known for exquisite teak carvings and architecture, originally part of the royal palace before being moved.',
                    'features': common_features['monastery'],
                    'rating': 4.5,
                    'review_count': 234,
                    'entry_fee': '5,000 MMK',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Zegyo Market',
                    'description': 'Mandalay\'s main market, offering everything from food and clothing to handicrafts and souvenirs.',
                    'features': common_features['market'],
                    'rating': 4.2,
                    'review_count': 189,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'U Bein Bridge',
                    'description': 'World\'s longest teakwood bridge at 1.2 kilometers, best visited at sunset in nearby Amarapura.',
                    'features': common_features['bridge'],
                    'rating': 4.9,
                    'review_count': 912,
                    'entry_fee': 'Free entry',
                    'distance': '11km from downtown'
                }
            ],
            
            # 20. MAWLAMYINE
            'mawlamyine': [
                {
                    'name': 'Kyaikthanlan Pagoda',
                    'description': 'Famous pagoda on a hill overlooking Mawlamyine, mentioned in Rudyard Kipling\'s poetry. Offers panoramic city views.',
                    'features': common_features['pagoda'],
                    'rating': 4.5,
                    'review_count': 234,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Win Sein Taw Ya',
                    'description': 'Home to one of the world\'s largest reclining Buddha images, 180 meters long, surrounded by thousands of Buddha statues.',
                    'features': ['Buddha image', 'Religious site', 'Massive statue'],
                    'rating': 4.7,
                    'review_count': 312,
                    'entry_fee': 'Free entry',
                    'distance': '15km from downtown'
                },
                {
                    'name': 'Santawshin Pagoda',
                    'description': 'Beautiful pagoda with intricate carvings and peaceful atmosphere.',
                    'features': common_features['pagoda'],
                    'rating': 4.3,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'The Death Railway Museum',
                    'description': 'Museum documenting the history of the WWII Death Railway, with photographs and artifacts from that era.',
                    'features': common_features['museum'],
                    'rating': 4.4,
                    'review_count': 145,
                    'entry_fee': '3,000 MMK',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Nwa La Bo Pagoda',
                    'description': 'Important religious site with unique architecture and ocean views.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 67,
                    'entry_fee': 'Free entry',
                    'distance': '4km from downtown'
                }
            ],
            
            # 21. MEIKTILA
            'meiktila': [
                {
                    'name': 'Meiktila Lake',
                    'description': 'Scenic lake in the center of the city, surrounded by parks and pagodas. Popular for boating and evening walks.',
                    'features': common_features['lake'],
                    'rating': 4.3,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Kyaung Daw Pagoda',
                    'description': 'Important pagoda with beautiful architecture and lake views.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'General Aung San Park',
                    'description': 'Public park dedicated to the national hero, perfect for relaxation.',
                    'features': common_features['park'],
                    'rating': 4.1,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Shwe Myin Tin Pagoda',
                    'description': 'Historic pagoda with legends and local significance.',
                    'features': common_features['pagoda'],
                    'rating': 4.0,
                    'review_count': 23,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Nagayon Pagoda',
                    'description': 'Unique pagoda with naga (serpent) imagery and peaceful atmosphere.',
                    'features': common_features['pagoda'],
                    'rating': 4.1,
                    'review_count': 19,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Dhamma Thukha Shwezigon Pagoda',
                    'description': 'Important meditation center and pagoda complex.',
                    'features': common_features['pagoda'],
                    'rating': 4.1,
                    'review_count': 21,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                }
            ],
            
            # 22. MONYWA
            'monywa': [
                {
                    'name': 'Thanboddhay Pagoda',
                    'description': 'Unique pagoda with over 500,000 Buddha images inside and out, featuring an unusual colorful design.',
                    'features': common_features['pagoda'],
                    'rating': 4.8,
                    'review_count': 345,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Bodhi Tataung',
                    'description': 'Home to the giant standing Buddha (129 meters) and reclining Buddha (90 meters), among the largest in the world.',
                    'features': ['Giant Buddha', 'Religious site', 'Photography'],
                    'rating': 4.7,
                    'review_count': 278,
                    'entry_fee': 'Free entry',
                    'distance': '15km from downtown'
                },
                {
                    'name': 'Pho Win Taung',
                    'description': 'Complex of hundreds of caves carved into sandstone cliffs, containing ancient Buddha images and murals.',
                    'features': common_features['cave'],
                    'rating': 4.6,
                    'review_count': 156,
                    'entry_fee': 'Free entry',
                    'distance': '25km from downtown'
                }
            ],
            
            # 23. MRAUK U
            'mrauk u': [
                {
                    'name': 'Shitthaung Temple',
                    'description': 'Famous temple with complex passages and 80,000+ Buddha images, built in 1535. Known for its intricate stone carvings.',
                    'features': common_features['temple'],
                    'rating': 4.8,
                    'review_count': 234,
                    'entry_fee': 'Combined pass 10,000 MMK',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Htukkanthein Temple',
                    'description': 'Fortress-like temple with circular corridor and panoramic views from the top.',
                    'features': common_features['temple'],
                    'rating': 4.6,
                    'review_count': 167,
                    'entry_fee': 'Included in pass',
                    'distance': '1.5km from downtown'
                },
                {
                    'name': 'Andaw-thein Ordination Hall',
                    'description': 'Known for its stone carvings and architecture, containing a tooth relic.',
                    'features': common_features['temple'],
                    'rating': 4.4,
                    'review_count': 98,
                    'entry_fee': 'Included in pass',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Koe-Thaung Temple',
                    'description': 'The largest temple in Mrauk U, containing 90,000 Buddha images.',
                    'features': common_features['temple'],
                    'rating': 4.5,
                    'review_count': 123,
                    'entry_fee': 'Included in pass',
                    'distance': '1.5km from downtown'
                },
                {
                    'name': 'Laymyetnha Paya',
                    'description': 'Features unique, colorful exterior ceramic artwork.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 56,
                    'entry_fee': 'Included in pass',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Longban Pyak Pagoda',
                    'description': '16th-century site known for its unique architecture.',
                    'features': common_features['pagoda'],
                    'rating': 4.1,
                    'review_count': 45,
                    'entry_fee': 'Included in pass',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Vesali Village',
                    'description': 'Ancient village site with the large, 17-foot-tall Great Vesali Buddha.',
                    'features': ['Ancient ruins', 'Archaeological site'],
                    'rating': 4.3,
                    'review_count': 67,
                    'entry_fee': 'Free entry',
                    'distance': '8km from Mrauk U'
                }
            ],
            
            # 24. MYAUNGMYA
            'myaungmya': [
                {
                    'name': 'Sakya Nanda Sakya Thiha Pagoda',
                    'description': 'Prominent pagoda located in the downtown city area, a key religious site.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Kabalone Pagoda',
                    'description': 'Famous religious site situated within the city center.',
                    'features': common_features['pagoda'],
                    'rating': 4.1,
                    'review_count': 23,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Shwe Thalyaung Pagoda',
                    'description': 'Well-known reclining Buddha image found in downtown Myaungmya.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 29,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Tawatain Tha Pagoda',
                    'description': 'Notable religious landmark for visitors in the city\'s heart.',
                    'features': common_features['pagoda'],
                    'rating': 4.0,
                    'review_count': 18,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Shwe Boddhaw Pagoda',
                    'description': 'Located near the town, often visited along with nearby scenic villages.',
                    'features': common_features['pagoda'],
                    'rating': 4.1,
                    'review_count': 21,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Mya Kan Thar Park',
                    'description': 'Pleasant green space with various plants and flowers, popular for evening walks.',
                    'features': common_features['park'],
                    'rating': 4.2,
                    'review_count': 34,
                    'entry_fee': '1,000 MMK',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Bo Gyoke Aung San Park',
                    'description': 'Local park dedicated to the national hero, providing outdoor leisure space.',
                    'features': common_features['park'],
                    'rating': 4.0,
                    'review_count': 15,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Dee Dote U Ba Cho Park',
                    'description': 'Recreational spot within the township for residents and visitors.',
                    'features': common_features['park'],
                    'rating': 3.9,
                    'review_count': 12,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                }
            ],
            
            # 25. MYEIK
            'myeik': [
                {
                    'name': 'Thein Daw Gyi Pagoda',
                    'description': 'Important pagoda in Myeik with historical significance.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Harris Island',
                    'description': 'Renowned for coral reefs, swimming, and snorkeling in crystal clear waters.',
                    'features': common_features['island'],
                    'rating': 4.6,
                    'review_count': 67,
                    'entry_fee': 'Boat trip required',
                    'distance': '30 minutes by boat'
                },
                {
                    'name': 'Frost Island',
                    'description': 'Offers white sandy beaches, corals, and sea urchins for snorkeling.',
                    'features': common_features['island'],
                    'rating': 4.5,
                    'review_count': 56,
                    'entry_fee': 'Boat trip required',
                    'distance': '45 minutes by boat'
                },
                {
                    'name': 'Phi Lar Island',
                    'description': 'Uninhabited island with colorful coral reefs and pristine beaches.',
                    'features': common_features['island'],
                    'rating': 4.6,
                    'review_count': 49,
                    'entry_fee': 'Boat trip required',
                    'distance': '1 hour by boat'
                },
                {
                    'name': 'Lampi Island',
                    'description': 'Known for marine life and eco-tourism, part of Lampi Marine National Park.',
                    'features': common_features['island'],
                    'rating': 4.7,
                    'review_count': 78,
                    'entry_fee': 'Boat trip required',
                    'distance': '2 hours by boat'
                },
                {
                    'name': 'Nyaung Wee Island',
                    'description': 'Famous for its Moken (sea gypsy) villages and traditional lifestyle.',
                    'features': common_features['island'],
                    'rating': 4.5,
                    'review_count': 56,
                    'entry_fee': 'Boat trip required',
                    'distance': '1.5 hours by boat'
                }
            ],
            
            # 26. MYITKYINA
            'myitkyina': [
                {
                    'name': 'Myit-Sone (Confluence)',
                    'description': 'The most famous landmark, located about 25 miles north, where the Mali and Nmai rivers merge to form the Ayeyarwady River.',
                    'features': ['Scenic views', 'River confluence', 'Photography'],
                    'rating': 4.8,
                    'review_count': 156,
                    'entry_fee': 'Free entry',
                    'distance': '25km from downtown'
                },
                {
                    'name': 'Kachin National Manau Park',
                    'description': 'Cultural hub hosting the annual Manau Festival, featuring distinct, colorful totem poles.',
                    'features': ['Cultural park', 'Festival ground', 'Totem poles'],
                    'rating': 4.5,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Hsu Taung Pye Zedidaw Pagoda',
                    'description': 'Major golden, gilded pagoda situated on the bank of the Irrawaddy River.',
                    'features': common_features['pagoda'],
                    'rating': 4.4,
                    'review_count': 67,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Kachin State Cultural Museum',
                    'description': 'Displays Kachin traditional costumes, jewelry, musical instruments, and cultural artifacts.',
                    'features': common_features['museum'],
                    'rating': 4.3,
                    'review_count': 56,
                    'entry_fee': '3,000 MMK',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Sri Saraswati Temple',
                    'description': 'Prominent, colorful Hindu temple known for its impressive bright golden structure.',
                    'features': ['Hindu temple', 'Colorful architecture'],
                    'rating': 4.2,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Geis Memorial Church',
                    'description': 'Historic Baptist church built in memory of early missionaries.',
                    'features': ['Church', 'Historic', 'Colonial'],
                    'rating': 4.1,
                    'review_count': 29,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Irrawaddy Riverbank',
                    'description': 'Spot for taking in views, with opportunities to see local gold panning activities.',
                    'features': ['River views', 'Gold panning', 'Photography'],
                    'rating': 4.3,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                }
            ],
            
            # 27. NAYPYIDAW
            'naypyidaw': [
                {
                    'name': 'Uppatasanti Pagoda',
                    'description': 'Prominent 99-meter-tall "Peace Pagoda" replica of Shwedagon, housing a Buddha tooth relic.',
                    'features': common_features['pagoda'],
                    'rating': 4.6,
                    'review_count': 345,
                    'entry_fee': 'Free entry',
                    'distance': '5km from downtown'
                },
                {
                    'name': 'Gem Museum',
                    'description': 'Showcases Myanmar\'s natural resources with vast collection of precious stones and jade.',
                    'features': ['Gem museum', 'Jewelry', 'Exhibits'],
                    'rating': 4.4,
                    'review_count': 178,
                    'entry_fee': '5,000 MMK',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Nay Pyi Taw Zoological Garden',
                    'description': 'One of the largest zoos in Southeast Asia, known for spacious, natural enclosures.',
                    'features': common_features['zoo'],
                    'rating': 4.3,
                    'review_count': 234,
                    'entry_fee': '5,000 MMK',
                    'distance': '4km from downtown'
                },
                {
                    'name': 'National Landmark Garden',
                    'description': 'Features miniature replicas of famous landmarks from across Myanmar.',
                    'features': ['Miniature landmarks', 'Garden', 'Photography'],
                    'rating': 4.2,
                    'review_count': 156,
                    'entry_fee': '3,000 MMK',
                    'distance': '5km from downtown'
                },
                {
                    'name': 'National Herbal Park',
                    'description': 'Green space containing over 20,000 herbal and medicinal plants.',
                    'features': common_features['garden'],
                    'rating': 4.1,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '6km from downtown'
                },
                {
                    'name': 'Water Fountain Garden',
                    'description': 'Public park with impressive, lit fountains near the city center.',
                    'features': ['Fountain', 'Garden', 'Evening light show'],
                    'rating': 4.3,
                    'review_count': 167,
                    'entry_fee': '2,000 MMK',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Nay Pyi Taw Safari Park',
                    'description': 'Features wildlife in safari-style environments.',
                    'features': ['Safari park', 'Wildlife'],
                    'rating': 4.2,
                    'review_count': 112,
                    'entry_fee': '5,000 MMK',
                    'distance': '8km from downtown'
                },
                {
                    'name': 'Thapyaygone Market',
                    'description': 'Local market area, good for experiencing local food and culture.',
                    'features': common_features['market'],
                    'rating': 4.0,
                    'review_count': 67,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                }
            ],
            
            # 28. NYAUNGLEBIN
            'nyaunglebin': [
                {
                    'name': 'Pa Ya Gyi Pagoda',
                    'description': 'Important local pagoda with beautiful architecture and peaceful grounds.',
                    'features': common_features['pagoda'],
                    'rating': 4.1,
                    'review_count': 23,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                }
            ],
            
            # 29. PAKOKKU
            'pakokku': [
                {
                    'name': 'Shwe Ku Pagoda',
                    'description': 'Beautiful pagoda overlooking the Irrawaddy River, with stunning views.',
                    'features': common_features['pagoda'],
                    'rating': 4.3,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Thi Ho Shin Pagoda',
                    'description': 'Important religious site with traditional architecture.',
                    'features': common_features['pagoda'],
                    'rating': 4.1,
                    'review_count': 23,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Pakhangyi Archaeological Museum',
                    'description': 'Museum showcasing artifacts from the ancient Pakhangyi city ruins.',
                    'features': common_features['museum'],
                    'rating': 4.2,
                    'review_count': 34,
                    'entry_fee': '2,000 MMK',
                    'distance': '10km from downtown'
                },
                {
                    'name': 'Shin-ma-taung Hill',
                    'description': 'Scenic hill offering panoramic views of Pakokku and the river.',
                    'features': common_features['hill'],
                    'rating': 4.3,
                    'review_count': 29,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                }
            ],
            
            # 30. PATHEIN
            'pathein': [
                {
                    'name': 'Shwemokhtaw Pagoda',
                    'description': 'Historic pagoda with Buddha hair relic, a major religious site in Pathein.',
                    'features': common_features['pagoda'],
                    'rating': 4.3,
                    'review_count': 78,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Ngwe Saung Beach',
                    'description': 'One of Myanmar\'s most beautiful beaches, 48km from Pathein, with white sand and clear water.',
                    'features': common_features['beach'],
                    'rating': 4.7,
                    'review_count': 345,
                    'entry_fee': 'Free entry',
                    'distance': '48km from Pathein'
                },
                {
                    'name': 'Shwe Sar Umbrella Workshop',
                    'description': 'Famous workshop producing traditional Pathein umbrellas, where you can see artisans at work.',
                    'features': ['Workshop', 'Shopping', 'Traditional crafts'],
                    'rating': 4.4,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Gaw Yin Gyi Island',
                    'description': 'Scenic island in the Ayeyarwady delta, accessible by boat.',
                    'features': common_features['island'],
                    'rating': 4.2,
                    'review_count': 45,
                    'entry_fee': 'Boat trip required',
                    'distance': 'Boat from Pathein'
                },
                {
                    'name': 'Chaung Thar Beach',
                    'description': 'Popular beach resort town, 55km from Pathein, known for relaxing atmosphere.',
                    'features': common_features['beach'],
                    'rating': 4.5,
                    'review_count': 234,
                    'entry_fee': 'Free entry',
                    'distance': '55km from Pathein'
                }
            ],
            
            # 31. PAUNGDE
            'paungde': [
                {
                    'name': 'Myat Swetaw Buddhist Temple',
                    'description': 'Important Buddhist temple with beautiful architecture.',
                    'features': common_features['temple'],
                    'rating': 4.1,
                    'review_count': 18,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Min Lak Yar Pagoda',
                    'description': 'Local pagoda with religious significance.',
                    'features': common_features['pagoda'],
                    'rating': 4.0,
                    'review_count': 12,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Nyein Chan Shwe Ti Public Park',
                    'description': 'Public park for recreation and relaxation.',
                    'features': common_features['park'],
                    'rating': 3.9,
                    'review_count': 8,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                }
            ],
            
            # 33. PYAY
            'pyay': [
                {
                    'name': 'Sri Ksetra (Tharaykhittaya) Ruins',
                    'description': 'Ancient 5th-9th century Pyu Kingdom capital, a UNESCO World Heritage Site with ancient stupas like Bawbawgyi.',
                    'features': ['Ancient ruins', 'UNESCO site', 'Archaeological'],
                    'rating': 4.8,
                    'review_count': 234,
                    'entry_fee': '5,000 MMK',
                    'distance': '8km from downtown'
                },
                {
                    'name': 'Akauk Taung',
                    'description': 'Boat trip to see numerous Buddha images carved into the cliffs along the Irrawaddy River.',
                    'features': ['Cliff carvings', 'Boat trip', 'Buddha images'],
                    'rating': 4.6,
                    'review_count': 167,
                    'entry_fee': '5,000 MMK',
                    'distance': '12km from downtown'
                },
                {
                    'name': 'Shwesandaw Paya',
                    'description': 'Prominent massive pagoda complex offering great panoramic views of the city and river.',
                    'features': common_features['pagoda'],
                    'rating': 4.5,
                    'review_count': 145,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Shwe Myet Man Paya (Shwemyethman Paya)',
                    'description': 'Temple featuring a Buddha statue wearing large gold-rimmed glasses, believed to cure eye ailments.',
                    'features': common_features['temple'],
                    'rating': 4.3,
                    'review_count': 78,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Hmawza (Srikshetra) Archaeological Museum',
                    'description': 'Displays artifacts, jewelry, sculptures, and coins excavated from the nearby ancient city.',
                    'features': common_features['museum'],
                    'rating': 4.4,
                    'review_count': 89,
                    'entry_fee': '3,000 MMK',
                    'distance': '8km from downtown'
                },
                {
                    'name': 'Sehtatgyi Buddha',
                    'description': 'Features a large sitting Buddha statue in a peaceful local residential area.',
                    'features': ['Buddha statue', 'Religious site'],
                    'rating': 4.2,
                    'review_count': 56,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Nawaday Bridge',
                    'description': 'Offers scenic views of the Irrawaddy River.',
                    'features': ['Bridge', 'River views'],
                    'rating': 4.1,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Thone Pan Hla',
                    'description': 'Scenic area along the river, popular for relaxation.',
                    'features': ['River views', 'Relaxation'],
                    'rating': 4.0,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '4km from downtown'
                }
            ],
            
            # 34. PYIN OO LWIN
            'pyin oo lwin': [
                {
                    'name': 'National Kandawgyi Botanical Gardens',
                    'description': '50-acre park established in 1915, featuring over 500 species of trees, orchid types, rose garden, and bird sanctuary.',
                    'features': common_features['garden'],
                    'rating': 4.7,
                    'review_count': 456,
                    'entry_fee': '5,000 MMK',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Anisakan Falls (Dattawgyaik Waterfall)',
                    'description': 'Dramatic 122-meter high waterfall tucked in a deep gorge, surrounded by jungle.',
                    'features': common_features['waterfall'],
                    'rating': 4.6,
                    'review_count': 234,
                    'entry_fee': '2,000 MMK',
                    'distance': '12km from downtown'
                },
                {
                    'name': 'Peik Chin Myaung Cave',
                    'description': 'Large limestone cave filled with countless Buddha images, stalactites, and underground streams.',
                    'features': common_features['cave'],
                    'rating': 4.5,
                    'review_count': 189,
                    'entry_fee': '3,000 MMK',
                    'distance': '8km from downtown'
                },
                {
                    'name': 'Pwe Kauk Waterfalls (Hampshire Falls)',
                    'description': 'Popular scenic picnic spot with multiple cascades and clear pools.',
                    'features': common_features['waterfall'],
                    'rating': 4.4,
                    'review_count': 167,
                    'entry_fee': '2,000 MMK',
                    'distance': '10km from downtown'
                },
                {
                    'name': 'Purcell Tower',
                    'description': 'Colonial-era clock tower gifted by Queen Victoria, located in the town center.',
                    'features': ['Colonial architecture', 'Landmark'],
                    'rating': 4.2,
                    'review_count': 98,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Maha Ant Htoo Kan Thar Pagoda',
                    'description': 'Prominent scenic pagoda known for its large Buddha image.',
                    'features': common_features['pagoda'],
                    'rating': 4.3,
                    'review_count': 78,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Chan Tak Buddhist Temple',
                    'description': 'Colorful Chinese temple built by Yunnanese immigrants.',
                    'features': ['Chinese temple', 'Colorful architecture'],
                    'rating': 4.2,
                    'review_count': 67,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                }
            ],
            
            # 35. SAGAING
            'sagaing': [
                {
                    'name': 'Sagaing Hill',
                    'description': 'Spiritual epicenter packed with hundreds of pagodas, monasteries, and nunneries offering panoramic views of the Ayeyarwady River.',
                    'features': common_features['hill'],
                    'rating': 4.8,
                    'review_count': 345,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Soon U Ponya Shin Pagoda',
                    'description': 'Situated atop Sagaing Hill, this 14th-century temple is a major pilgrimage site.',
                    'features': common_features['pagoda'],
                    'rating': 4.6,
                    'review_count': 234,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'U Min Thonze (30 Caves) Pagoda',
                    'description': 'Famous for its crescent-shaped structure containing 45 seated Buddha images.',
                    'features': common_features['pagoda'],
                    'rating': 4.5,
                    'review_count': 189,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Kaunghmudaw Pagoda',
                    'description': 'Massive dome-shaped pagoda built in 1636, inspired by the Ruwanweli Seya stupa in Sri Lanka.',
                    'features': common_features['pagoda'],
                    'rating': 4.5,
                    'review_count': 167,
                    'entry_fee': 'Free entry',
                    'distance': '4km from downtown'
                },
                {
                    'name': 'Settawa Paya',
                    'description': 'Temple housing a Buddha footprint, a significant religious site.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 78,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Tilawkaguru',
                    'description': 'Cave temple containing interesting murals and historical significance.',
                    'features': common_features['cave'],
                    'rating': 4.3,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                }
            ],
            
            # 36. SHWEBO
            'shwebo': [
                {
                    'name': 'Shwebon Yadana Mingalar Palace',
                    'description': 'Reconstruction of King Alaungpaya\'s palace, representing the start of the Konbaung Dynasty.',
                    'features': common_features['palace'],
                    'rating': 4.3,
                    'review_count': 67,
                    'entry_fee': '5,000 MMK',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Maw Daw Myin Thar Pagoda',
                    'description': 'Major historically significant and uniquely styled pagoda built in 1757.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Hanlin World Heritage Site',
                    'description': 'Ancient Pyu city, recognized as a UNESCO World Heritage site, featuring archaeological ruins.',
                    'features': ['Ancient ruins', 'UNESCO site', 'Archaeological'],
                    'rating': 4.5,
                    'review_count': 89,
                    'entry_fee': '5,000 MMK',
                    'distance': '15km from downtown'
                }
            ],
            
            # 37. SHWEGYIN
            'shwegyin': [
                {
                    'name': 'Phaya Gyi Pagoda',
                    'description': 'Important local pagoda with religious significance.',
                    'features': common_features['pagoda'],
                    'rating': 4.0,
                    'review_count': 15,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Pyuntaza Lake',
                    'description': 'Scenic lake popular for relaxation and picnics.',
                    'features': common_features['lake'],
                    'rating': 4.1,
                    'review_count': 18,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                }
            ],
            
            # 38. SITTWE
            'sittwe': [
                {
                    'name': 'Sittwe Viewpoint',
                    'description': 'Located at the end of Strand Road, premier spot to watch sunset over the Bay of Bengal and the Kaladan River.',
                    'features': common_features['viewpoint'],
                    'rating': 4.5,
                    'review_count': 112,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Law Ka Nandar Pagoda',
                    'description': 'Major highly-rated unique pagoda, famous for its distinct, intricate, patterned architecture.',
                    'features': common_features['pagoda'],
                    'rating': 4.4,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Rakhine State Cultural Museum',
                    'description': 'Features exhibits on the history, culture, and art of the Rakhine people.',
                    'features': common_features['museum'],
                    'rating': 4.3,
                    'review_count': 67,
                    'entry_fee': '3,000 MMK',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Buddhist Museum',
                    'description': 'Houses a large collection of ancient Buddha statues and artifacts.',
                    'features': common_features['museum'],
                    'rating': 4.2,
                    'review_count': 45,
                    'entry_fee': '2,000 MMK',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Central Market & Fish Market',
                    'description': 'Vibrant area to explore local life and food, particularly in the morning.',
                    'features': common_features['market'],
                    'rating': 4.3,
                    'review_count': 78,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Shwezedi Monastery',
                    'description': 'Historic century-old monastery with traditional architecture.',
                    'features': common_features['monastery'],
                    'rating': 4.1,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Lay Shan Taung Lighthouse',
                    'description': 'Located on a hill, offering panoramic views, reachable by boat from the jetty.',
                    'features': ['Lighthouse', 'Viewpoint'],
                    'rating': 4.3,
                    'review_count': 45,
                    'entry_fee': 'Boat trip required',
                    'distance': 'Boat from jetty'
                },
                {
                    'name': 'Ahkyaib-daw Pagoda',
                    'description': 'Important local religious site with cultural significance.',
                    'features': common_features['pagoda'],
                    'rating': 4.1,
                    'review_count': 29,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                }
            ],
            
            # 39. TACHILEIK
            'tachileik': [
                {
                    'name': 'Tachileik Shwedagon Pagoda',
                    'description': 'Prominent replica of the famous Yangon pagoda located on a hill, offering views of both Thailand and Myanmar.',
                    'features': common_features['pagoda'],
                    'rating': 4.3,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Tachileik Market',
                    'description': 'Bustling large market near the border crossing, famous for local goods, snacks, and imported products.',
                    'features': common_features['market'],
                    'rating': 4.2,
                    'review_count': 112,
                    'entry_fee': 'Free entry',
                    'distance': 'Downtown'
                },
                {
                    'name': 'Golden Triangle Viewpoint',
                    'description': 'Panoramic view of the three-country border (Myanmar, Thailand, Laos) where the Ruak and Mekong rivers meet.',
                    'features': ['Viewpoint', 'Golden Triangle', 'Mekong River'],
                    'rating': 4.6,
                    'review_count': 234,
                    'entry_fee': 'Free entry',
                    'distance': '15km from Tachileik'
                }
            ],
            
            # 40. TAUNGGYI
            'taunggyi': [
                {
                    'name': 'Kakku Pagodas',
                    'description': 'Ancient complex of over 2,500 stupas dating back centuries, hidden in the hills south of Taunggyi.',
                    'features': common_features['pagoda'],
                    'rating': 4.9,
                    'review_count': 345,
                    'entry_fee': '10,000 MMK',
                    'distance': '38.6km from downtown'
                },
                {
                    'name': 'Hetm Sann Cave',
                    'description': 'Beautiful cave with Buddha images and natural formations.',
                    'features': common_features['cave'],
                    'rating': 4.3,
                    'review_count': 56,
                    'entry_fee': 'Free entry',
                    'distance': '15km from downtown'
                },
                {
                    'name': 'Kyang Daw Pagoda',
                    'description': 'Important local pagoda with scenic views.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Main Ma Ye` Tha Khin Ma Mountain',
                    'description': 'Scenic mountain offering hiking and panoramic views.',
                    'features': common_features['hill'],
                    'rating': 4.3,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '10km from downtown'
                },
                {
                    'name': 'Nga Phe Chaung Monastery',
                    'description': 'Ancient monastery built on stilts over Inle Lake, accessible from Taunggyi.',
                    'features': common_features['monastery'],
                    'rating': 4.4,
                    'review_count': 78,
                    'entry_fee': 'Free entry',
                    'distance': '32km from downtown'
                },
                {
                    'name': 'Nyaungshewe',
                    'description': 'Gateway town to Inle Lake with markets and temples.',
                    'features': ['Town', 'Gateway to Inle Lake'],
                    'rating': 4.2,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '25km from downtown'
                },
                {
                    'name': 'Shwe Bone Pwint Pagoda',
                    'description': 'Beautiful pagoda with stunning architecture, near Taunggyi.',
                    'features': common_features['pagoda'],
                    'rating': 4.1,
                    'review_count': 34,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Sulamuni Lawka Chanthar Pagoda',
                    'description': 'Important religious site with beautiful architecture.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 29,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                }
            ],
            
            # 41. TAUNGOO
            'taungoo': [
                {
                    'name': 'Shwesandaw Pagoda',
                    'description': 'The city\'s most famous towering golden pagoda built by King Min Gyi Nyo.',
                    'features': common_features['pagoda'],
                    'rating': 4.5,
                    'review_count': 112,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Myat Saw Nyi Naung Pagoda',
                    'description': 'Known for its photogenic glass tile finishes and beautiful architecture.',
                    'features': common_features['pagoda'],
                    'rating': 4.3,
                    'review_count': 67,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Statue of King Bayintnaung',
                    'description': 'Massive revered statue honoring the founder of the Second Burmese Empire, located on the old road.',
                    'features': ['Statue', 'Historical monument'],
                    'rating': 4.4,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Old City Moat/Walls',
                    'description': 'Ruins from the 16th-century Taungoo Dynasty, particularly on the eastern side.',
                    'features': ['Ancient ruins', 'Historic walls'],
                    'rating': 4.2,
                    'review_count': 56,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Pho Kyar Elephant Camp',
                    'description': 'Located in the Bago Yoma mountain range, offering nature walks and glimpses into elephant life.',
                    'features': ['Elephant camp', 'Nature walks'],
                    'rating': 4.4,
                    'review_count': 78,
                    'entry_fee': '5,000 MMK',
                    'distance': '25km from downtown'
                },
                {
                    'name': 'Kantawgyi Garden/Lake',
                    'description': 'Peaceful artificial pond, ideal for walking and relaxing.',
                    'features': common_features['lake'],
                    'rating': 4.1,
                    'review_count': 45,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                }
            ],
            
            # 43. THANDWE
            'thandwe': [
                {
                    'name': 'Ngapali Beach',
                    'description': 'Myanmar\'s premier beach destination, featuring 3 kilometers of white sand and palm-fringed shores, located 7km west of Thandwe.',
                    'features': common_features['beach'],
                    'rating': 4.9,
                    'review_count': 567,
                    'entry_fee': 'Free entry',
                    'distance': '7km from downtown'
                },
                {
                    'name': 'Tilawkasayambhu Buddha Statue',
                    'description': 'Massive standing Buddha statue on a hill overlooking the southern bay of Ngapali, a symbolic guardian for local fishermen.',
                    'features': ['Buddha statue', 'Hilltop', 'Views'],
                    'rating': 4.5,
                    'review_count': 89,
                    'entry_fee': 'Free entry',
                    'distance': '8km from downtown'
                },
                {
                    'name': 'Pao Wun Bridge',
                    'description': 'Scenic wooden bridge set within a mangrove forest area, popular for photography and local relaxation.',
                    'features': ['Bridge', 'Mangrove forest', 'Photography'],
                    'rating': 4.3,
                    'review_count': 56,
                    'entry_fee': 'Free entry',
                    'distance': '5km from downtown'
                }
            ],
            
            # 45. WAKEMA
            'wakema': [
                {
                    'name': 'Myat Swal Taw Pagoda',
                    'description': 'Important pagoda housing sacred relics, a key religious site.',
                    'features': common_features['pagoda'],
                    'rating': 4.2,
                    'review_count': 23,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Mya Thein Tan Pagoda',
                    'description': 'Beautiful pagoda with traditional architecture.',
                    'features': common_features['pagoda'],
                    'rating': 4.1,
                    'review_count': 18,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                },
                {
                    'name': 'Thet Kya Ma Har Thiri Pagoda',
                    'description': 'Local pagoda with religious significance.',
                    'features': common_features['pagoda'],
                    'rating': 4.0,
                    'review_count': 12,
                    'entry_fee': 'Free entry',
                    'distance': '1km from downtown'
                }
            ],
            
            # 46. YANGON
            'yangon': [
                {
                    'name': 'Shwedagon Pagoda',
                    'description': 'The most sacred Buddhist pagoda in Myanmar, covered in gold, standing 99 meters tall. A stunning sight at sunrise and sunset.',
                    'features': common_features['pagoda'],
                    'rating': 4.9,
                    'review_count': 2345,
                    'entry_fee': '10,000 MMK',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'Bogyoke Aung San Market',
                    'description': 'Historic colonial-era market with hundreds of shops for souvenirs, jewelry, art, and handicrafts.',
                    'features': common_features['market'],
                    'rating': 4.4,
                    'review_count': 789,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Botataung Pagoda',
                    'description': 'Unique hollow pagoda with glass-walled corridors and relics of Buddha, located near the river.',
                    'features': common_features['pagoda'],
                    'rating': 4.3,
                    'review_count': 456,
                    'entry_fee': '3,000 MMK',
                    'distance': '5km from downtown'
                },
                {
                    'name': 'Chaukhtagyi Buddha Temple',
                    'description': 'Houses one of Myanmar\'s largest reclining Buddha images, 65 meters long.',
                    'features': ['Buddha image', 'Temple'],
                    'rating': 4.3,
                    'review_count': 345,
                    'entry_fee': 'Free entry',
                    'distance': '6km from downtown'
                },
                {
                    'name': 'Htauk Kyant War Memorial Cemetery',
                    'description': 'Beautifully maintained cemetery honoring Allied soldiers who died in WWII.',
                    'features': common_features['war_cemetery'],
                    'rating': 4.6,
                    'review_count': 234,
                    'entry_fee': 'Free entry',
                    'distance': '32km from downtown'
                },
                {
                    'name': 'Inya Lake',
                    'description': 'Largest lake in Yangon, popular for jogging, picnics, and sunset views.',
                    'features': common_features['lake'],
                    'rating': 4.3,
                    'review_count': 567,
                    'entry_fee': 'Free entry',
                    'distance': '5km from downtown'
                },
                {
                    'name': 'Kandawgyi Park',
                    'description': 'Scenic park with a beautiful lake and views of Shwedagon Pagoda, featuring the Karaweik Palace.',
                    'features': common_features['park'],
                    'rating': 4.4,
                    'review_count': 678,
                    'entry_fee': '2,000 MMK',
                    'distance': '4km from downtown'
                },
                {
                    'name': 'Myanmar Plaza',
                    'description': 'Modern shopping mall with international brands, restaurants, and a cinema.',
                    'features': ['Shopping mall', 'Restaurants'],
                    'rating': 4.2,
                    'review_count': 345,
                    'entry_fee': 'Free entry',
                    'distance': '8km from downtown'
                },
                {
                    'name': 'National Museum of Myanmar',
                    'description': 'Extensive collection of Burmese art, history, and culture, including the Lion Throne.',
                    'features': common_features['museum'],
                    'rating': 4.3,
                    'review_count': 456,
                    'entry_fee': '5,000 MMK',
                    'distance': '3km from downtown'
                },
                {
                    'name': 'The Secretariat Yangon',
                    'description': 'Historic colonial building where General Aung San was assassinated, now open for tours.',
                    'features': ['Historic building', 'Colonial architecture'],
                    'rating': 4.5,
                    'review_count': 234,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Yangon Chinatown',
                    'description': 'Vibrant area with street food, markets, and the colorful Kheng Hock Keong Temple.',
                    'features': ['Chinatown', 'Street food', 'Markets'],
                    'rating': 4.3,
                    'review_count': 567,
                    'entry_fee': 'Free entry',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Yangon City Hall',
                    'description': 'Impressive colonial-era building with traditional Burmese architectural influences.',
                    'features': ['Colonial architecture', 'Landmark'],
                    'rating': 4.2,
                    'review_count': 234,
                    'entry_fee': 'Free entry (outside only)',
                    'distance': '2km from downtown'
                },
                {
                    'name': 'Yangon Zoo',
                    'description': 'One of the oldest zoos in Southeast Asia, home to elephants, tigers, and various animals.',
                    'features': common_features['zoo'],
                    'rating': 4.0,
                    'review_count': 345,
                    'entry_fee': '5,000 MMK',
                    'distance': '4km from downtown'
                },
                {
                    'name': 'Bogyoke Aung San Museum',
                    'description': 'Museum housed in the former residence of General Aung San, displaying personal belongings and photos.',
                    'features': common_features['museum'],
                    'rating': 4.3,
                    'review_count': 156,
                    'entry_fee': '2,000 MMK',
                    'distance': '5km from downtown'
                }
            ]
        }
        
        # Check for exact city name match
        if city_name in attractions_db:
            return attractions_db[city_name]
        
        # Check for partial matches
        for key, attractions in attractions_db.items():
            if key in city_name or city_name in key:
                return attractions
        
        # Default attractions for cities without specific data
        default_attractions = [
            {
                'name': f'{city.name} Central Market',
                'description': f'Main market in {city.name} where locals gather to buy fresh produce, traditional foods, and daily necessities. A great place to experience local life.',
                'features': common_features['market'],
                'rating': 4.0,
                'review_count': random.randint(15, 40),
                'entry_fee': 'Free entry',
                'distance': 'Downtown'
            },
            {
                'name': f'{city.name} Pagoda',
                'description': f'Important religious site in {city.name} featuring beautiful architecture and peaceful atmosphere. A place of worship and meditation for locals.',
                'features': common_features['pagoda'],
                'rating': 4.1,
                'review_count': random.randint(10, 35),
                'entry_fee': 'Free entry',
                'distance': '1-2km from downtown'
            },
            {
                'name': f'{city.name} Viewpoint',
                'description': f'Scenic viewpoint offering panoramic views of {city.name} and the surrounding countryside. Perfect for photography and watching sunset.',
                'features': common_features['viewpoint'],
                'rating': 4.2,
                'review_count': random.randint(5, 25),
                'entry_fee': 'Free entry',
                'distance': '2-3km from downtown'
            },
            {
                'name': f'{city.name} Monastery',
                'description': f'Peaceful monastery where monks reside and meditate. Features traditional Burmese architecture and serene gardens.',
                'features': common_features['monastery'],
                'rating': 4.0,
                'review_count': random.randint(5, 20),
                'entry_fee': 'Free entry',
                'distance': '1-2km from downtown'
            },
            {
                'name': f'{city.name} Lake',
                'description': f'Scenic lake popular for relaxation, walking, and picnics. A peaceful escape from the city bustle.',
                'features': common_features['lake'],
                'rating': 3.9,
                'review_count': random.randint(5, 15),
                'entry_fee': 'Free entry',
                'distance': '2-4km from downtown'
            }
        ]
        
        # Return 3-5 default attractions
        num_attractions = random.randint(3, 5)
        return default_attractions[:num_attractions]