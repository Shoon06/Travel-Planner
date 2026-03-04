# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\add_attractions_data.py

from django.core.management.base import BaseCommand
from django.db.models import Q  # ← IMPORT Q HERE!
from planner.models import Destination
import random

class Command(BaseCommand):
    help = 'Add attractions data for all destinations'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting to add attractions data...'))
        
        # First, make sure all cities/towns have is_region=True
        cities = Destination.objects.filter(type__in=['city', 'town'])
        for city in cities:
            if not city.is_region:
                city.is_region = True
                city.save()
                self.stdout.write(f"Set {city.name} as region")
        
        # Attractions data for each destination
        attractions_data = {
            'Taunggyi': [
                {
                    'name': 'Floating Market',
                    'type': 'attraction',
                    'description': 'Boat tour | Night view. Popular floating market with local products and souvenirs.',
                    'region': 'Shan State',
                    'rating': 3.9,
                    'review_count': 44,
                    'distance_from_city': '37.9km from downtown',
                    'entry_fee': 'Free entry',
                    'features': ['Boat tour', 'Night view']
                },
                {
                    'name': 'Inle Lake',
                    'type': 'attraction',
                    'description': 'Natural scenery | Boat tour. Freshwater lake famous for leg-rowing fishermen and floating villages.',
                    'region': 'Shan State',
                    'rating': 4.7,
                    'review_count': 137,
                    'distance_from_city': '25.3km from downtown',
                    'entry_fee': 'Free entry',
                    'features': ['Natural scenery', 'Boat tour']
                },
                {
                    'name': 'Shwe Bone Pwint Pagoda',
                    'type': 'attraction',
                    'description': 'Golden Blossoms and Great Glory. Beautiful pagoda with stunning architecture.',
                    'region': 'Shan State',
                    'rating': 4.0,
                    'review_count': 2,
                    'distance_from_city': '1.1km from downtown',
                    'entry_fee': 'Free entry',
                    'features': ['Historic buildings', 'Religious site']
                },
                {
                    'name': 'Nga Phe Chaung Monastery',
                    'type': 'attraction',
                    'description': 'Historic buildings. Ancient monastery built on stilts over Inle Lake.',
                    'region': 'Shan State',
                    'rating': 4.2,
                    'review_count': 49,
                    'distance_from_city': '32.7km from downtown',
                    'entry_fee': 'Free entry',
                    'features': ['Historic buildings', 'Monastery']
                },
                {
                    'name': 'Phaung Daw Oo Pagoda',
                    'type': 'attraction',
                    'description': 'Historic buildings. Famous pagoda on Inle Lake with five sacred Buddha images.',
                    'region': 'Shan State',
                    'rating': 3.5,
                    'review_count': 41,
                    'distance_from_city': '37.3km from downtown',
                    'entry_fee': 'Free entry',
                    'features': ['Historic buildings', 'Religious site']
                },
                {
                    'name': 'Kakku Pagodas',
                    'type': 'attraction',
                    'description': 'Historic buildings. Ancient complex of over 2,500 stupas dating back centuries.',
                    'region': 'Shan State',
                    'rating': 4.0,
                    'review_count': 13,
                    'distance_from_city': '38.6km from downtown',
                    'entry_fee': 'Free entry',
                    'features': ['Historic buildings', 'Archaeological site']
                }
            ],
            'Bagan': [
                {
                    'name': 'Ananda Temple',
                    'type': 'attraction',
                    'description': 'One of Bagan\'s most beautiful and best-preserved temples.',
                    'region': 'Mandalay Region',
                    'rating': 4.8,
                    'review_count': 256,
                    'entry_fee': 'Included in Archaeological Zone pass',
                    'features': ['Historic buildings', 'Religious site', 'Architecture']
                },
                {
                    'name': 'Shwezigon Pagoda',
                    'type': 'attraction',
                    'description': 'One of the most important pagodas in Myanmar.',
                    'region': 'Mandalay Region',
                    'rating': 4.7,
                    'review_count': 189,
                    'entry_fee': 'Included in Archaeological Zone pass',
                    'features': ['Religious site', 'Historic buildings']
                },
                {
                    'name': 'Dhammayangyi Temple',
                    'type': 'attraction',
                    'description': 'The largest temple in Bagan with massive brick structure.',
                    'region': 'Mandalay Region',
                    'rating': 4.5,
                    'review_count': 143,
                    'entry_fee': 'Included in Archaeological Zone pass',
                    'features': ['Historic buildings', 'Architecture']
                },
                {
                    'name': 'Thatbyinnyu Temple',
                    'type': 'attraction',
                    'description': 'The tallest temple in Bagan at 61 meters high.',
                    'region': 'Mandalay Region',
                    'rating': 4.4,
                    'review_count': 98,
                    'entry_fee': 'Included in Archaeological Zone pass',
                    'features': ['Historic buildings', 'Viewpoint']
                },
                {
                    'name': 'Sunset at Buledi',
                    'type': 'attraction',
                    'description': 'Perfect spot to watch sunset over the temple plains.',
                    'region': 'Mandalay Region',
                    'rating': 4.9,
                    'review_count': 312,
                    'entry_fee': 'Free',
                    'features': ['Scenic spot', 'Photography', 'Sunset view']
                },
                {
                    'name': 'Hot Air Balloon Ride',
                    'type': 'activity',
                    'description': 'Experience breathtaking sunrise views over thousands of temples.',
                    'region': 'Mandalay Region',
                    'rating': 4.9,
                    'review_count': 567,
                    'entry_fee': '$320-380 per person',
                    'features': ['Adventure', 'Scenic views', 'Sunrise']
                }
            ],
            'Mandalay': [
                {
                    'name': 'Mandalay Palace',
                    'type': 'attraction',
                    'description': 'The last royal palace of the Burmese monarchy.',
                    'region': 'Mandalay Region',
                    'rating': 4.3,
                    'review_count': 178,
                    'entry_fee': '10,000 MMK',
                    'features': ['Historic buildings', 'Royal palace', 'Museum']
                },
                {
                    'name': 'Mandalay Hill',
                    'type': 'attraction',
                    'description': 'Famous hill offering panoramic views of the city.',
                    'region': 'Mandalay Region',
                    'rating': 4.6,
                    'review_count': 245,
                    'entry_fee': 'Free',
                    'features': ['Scenic spot', 'Sunset view', 'Hiking']
                },
                {
                    'name': 'Kuthodaw Pagoda',
                    'type': 'attraction',
                    'description': 'Known as "the world\'s largest book" with 729 marble slabs.',
                    'region': 'Mandalay Region',
                    'rating': 4.5,
                    'review_count': 134,
                    'entry_fee': '5,000 MMK',
                    'features': ['Religious site', 'Historic buildings']
                },
                {
                    'name': 'U Bein Bridge',
                    'type': 'attraction',
                    'description': 'World\'s longest teakwood bridge at 1.2 kilometers.',
                    'region': 'Mandalay Region',
                    'rating': 4.7,
                    'review_count': 423,
                    'entry_fee': 'Free',
                    'features': ['Scenic spot', 'Historic bridge', 'Sunset view']
                },
                {
                    'name': 'Maha Muni Pagoda',
                    'type': 'attraction',
                    'description': 'One of Myanmar\'s most revered Buddha images covered in gold leaf.',
                    'region': 'Mandalay Region',
                    'rating': 4.6,
                    'review_count': 198,
                    'entry_fee': 'Free',
                    'features': ['Religious site', 'Gold leaf']
                },
                {
                    'name': 'Shwenandaw Monastery',
                    'type': 'attraction',
                    'description': 'Known for exquisite teak carvings and architecture.',
                    'region': 'Mandalay Region',
                    'rating': 4.4,
                    'review_count': 87,
                    'entry_fee': '5,000 MMK',
                    'features': ['Historic buildings', 'Monastery', 'Wood carvings']
                }
            ],
            'Yangon': [
                {
                    'name': 'Shwedagon Pagoda',
                    'type': 'attraction',
                    'description': 'The most sacred Buddhist pagoda in Myanmar, covered in gold.',
                    'region': 'Yangon Region',
                    'rating': 4.9,
                    'review_count': 1245,
                    'entry_fee': '10,000 MMK',
                    'features': ['Religious site', 'Historic buildings', 'Sunset view']
                },
                {
                    'name': 'Bogyoke Market',
                    'type': 'attraction',
                    'description': 'Historic market with hundreds of shops for souvenirs and crafts.',
                    'region': 'Yangon Region',
                    'rating': 4.3,
                    'review_count': 567,
                    'entry_fee': 'Free',
                    'features': ['Shopping', 'Local market', 'Colonial architecture']
                },
                {
                    'name': 'Sule Pagoda',
                    'type': 'attraction',
                    'description': '2,000-year-old pagoda in the heart of downtown.',
                    'region': 'Yangon Region',
                    'rating': 4.2,
                    'review_count': 234,
                    'entry_fee': '3,000 MMK',
                    'features': ['Religious site', 'Historic buildings']
                },
                {
                    'name': 'Kandawgyi Lake',
                    'type': 'attraction',
                    'description': 'Beautiful lake with views of Shwedagon Pagoda and Karaweik Palace.',
                    'region': 'Yangon Region',
                    'rating': 4.3,
                    'review_count': 345,
                    'entry_fee': 'Free',
                    'features': ['Scenic spot', 'Park', 'Boating']
                },
                {
                    'name': 'Botataung Pagoda',
                    'type': 'attraction',
                    'description': 'Unique hollow pagoda with glass-walled corridors.',
                    'region': 'Yangon Region',
                    'rating': 4.1,
                    'review_count': 123,
                    'entry_fee': '3,000 MMK',
                    'features': ['Religious site', 'Historic buildings']
                },
                {
                    'name': 'National Museum',
                    'type': 'attraction',
                    'description': 'Extensive collection of Burmese art, history, and culture.',
                    'region': 'Yangon Region',
                    'rating': 4.0,
                    'review_count': 89,
                    'entry_fee': '5,000 MMK',
                    'features': ['Museum', 'Cultural', 'Artifacts']
                }
            ],
            'Inle Lake': [
                {
                    'name': 'Inle Lake Boat Tour',
                    'type': 'activity',
                    'description': 'Explore the lake with traditional longtail boats.',
                    'region': 'Shan State',
                    'rating': 4.8,
                    'review_count': 345,
                    'entry_fee': '20,000-30,000 MMK per boat',
                    'features': ['Boat tour', 'Scenic views', 'Photography']
                },
                {
                    'name': 'Indein Village',
                    'type': 'attraction',
                    'description': 'Ancient village with hundreds of crumbling stupas.',
                    'region': 'Shan State',
                    'rating': 4.6,
                    'review_count': 178,
                    'entry_fee': 'Free',
                    'features': ['Village', 'Historic buildings', 'Archaeological site']
                },
                {
                    'name': 'Nga Phe Kyaung Monastery',
                    'type': 'attraction',
                    'description': 'Known as the "Jumping Cat Monastery".',
                    'region': 'Shan State',
                    'rating': 4.2,
                    'review_count': 156,
                    'entry_fee': 'Free',
                    'features': ['Monastery', 'Historic buildings']
                },
                {
                    'name': 'Phaw Khone Village',
                    'type': 'attraction',
                    'description': 'Traditional weaving village known for lotus silk production.',
                    'region': 'Shan State',
                    'rating': 4.4,
                    'review_count': 98,
                    'entry_fee': 'Free',
                    'features': ['Village', 'Cultural', 'Weaving']
                },
                {
                    'name': 'Inthein',
                    'type': 'attraction',
                    'description': 'Ancient pagoda complex with over 1,000 stupas.',
                    'region': 'Shan State',
                    'rating': 4.5,
                    'review_count': 112,
                    'entry_fee': 'Free',
                    'features': ['Archaeological site', 'Historic buildings']
                }
            ],
            'Ngapali Beach': [
                {
                    'name': 'Ngapali Beach Main Beach',
                    'type': 'attraction',
                    'description': 'Pristine white sand beach with crystal clear water.',
                    'region': 'Rakhine State',
                    'rating': 4.8,
                    'review_count': 234,
                    'entry_fee': 'Free',
                    'features': ['Beach', 'Relaxation', 'Swimming']
                },
                {
                    'name': 'Pearl Island',
                    'type': 'attraction',
                    'description': 'Small island perfect for day trips and snorkeling.',
                    'region': 'Rakhine State',
                    'rating': 4.5,
                    'review_count': 67,
                    'entry_fee': 'Free',
                    'features': ['Island', 'Snorkeling', 'Beach']
                },
                {
                    'name': 'Lin Thar Fishing Village',
                    'type': 'attraction',
                    'description': 'Traditional fishing village with stilt houses.',
                    'region': 'Rakhine State',
                    'rating': 4.2,
                    'review_count': 45,
                    'entry_fee': 'Free',
                    'features': ['Village', 'Cultural', 'Fishing']
                }
            ],
            'Hsipaw': [
                {
                    'name': 'Hsipaw Palace',
                    'type': 'attraction',
                    'description': 'Former Shan palace with colonial architecture.',
                    'region': 'Shan State',
                    'rating': 4.1,
                    'review_count': 56,
                    'entry_fee': '3,000 MMK',
                    'features': ['Historic buildings', 'Royal palace']
                },
                {
                    'name': 'Little Bagan',
                    'type': 'attraction',
                    'description': 'Ancient pagoda ruins along the river.',
                    'region': 'Shan State',
                    'rating': 4.0,
                    'review_count': 34,
                    'entry_fee': 'Free',
                    'features': ['Archaeological site', 'Historic buildings']
                },
                {
                    'name': 'Bawgyo Pagoda',
                    'type': 'attraction',
                    'description': 'Important Shan pagoda with annual festival.',
                    'region': 'Shan State',
                    'rating': 4.2,
                    'review_count': 23,
                    'entry_fee': 'Free',
                    'features': ['Religious site']
                }
            ],
            'Kalaw': [
                {
                    'name': 'Kalaw to Inle Lake Trek',
                    'type': 'activity',
                    'description': 'Multi-day trek through villages and hills to Inle Lake.',
                    'region': 'Shan State',
                    'rating': 4.8,
                    'review_count': 234,
                    'entry_fee': '40,000-60,000 MMK',
                    'features': ['Trekking', 'Adventure', 'Villages']
                },
                {
                    'name': 'Shwe Oo Min Pagoda',
                    'type': 'attraction',
                    'description': 'Pagoda with meditation caves and Buddha images.',
                    'region': 'Shan State',
                    'rating': 4.3,
                    'review_count': 78,
                    'entry_fee': 'Free',
                    'features': ['Religious site', 'Cave']
                },
                {
                    'name': 'Hnee Pagoda',
                    'type': 'attraction',
                    'description': 'Hilltop pagoda with panoramic views.',
                    'region': 'Shan State',
                    'rating': 4.2,
                    'review_count': 45,
                    'entry_fee': 'Free',
                    'features': ['Religious site', 'Viewpoint']
                }
            ],
            'Pyin Oo Lwin': [
                {
                    'name': 'National Kandawgyi Gardens',
                    'type': 'attraction',
                    'description': 'Beautiful botanical gardens with orchids and birds.',
                    'region': 'Mandalay Region',
                    'rating': 4.5,
                    'review_count': 167,
                    'entry_fee': '5,000 MMK',
                    'features': ['Gardens', 'Scenic spot', 'Nature']
                },
                {
                    'name': 'Pwe Kauk Falls',
                    'type': 'attraction',
                    'description': 'Popular waterfall for picnics and swimming.',
                    'region': 'Mandalay Region',
                    'rating': 4.2,
                    'review_count': 89,
                    'entry_fee': '2,000 MMK',
                    'features': ['Waterfall', 'Scenic spot', 'Swimming']
                },
                {
                    'name': 'Candy Factory',
                    'type': 'attraction',
                    'description': 'Local factory producing strawberry and fruit jams.',
                    'region': 'Mandalay Region',
                    'rating': 4.0,
                    'review_count': 56,
                    'entry_fee': 'Free',
                    'features': ['Food', 'Shopping']
                }
            ],
            'Mrauk U': [
                {
                    'name': 'Shitthaung Temple',
                    'type': 'attraction',
                    'description': 'Famous temple with complex passages and Buddha images.',
                    'region': 'Rakhine State',
                    'rating': 4.7,
                    'review_count': 89,
                    'entry_fee': 'Combined pass available',
                    'features': ['Historic buildings', 'Religious site']
                },
                {
                    'name': 'Htukkanthein Temple',
                    'type': 'attraction',
                    'description': 'Fortress-like temple with circular corridor.',
                    'region': 'Rakhine State',
                    'rating': 4.5,
                    'review_count': 67,
                    'entry_fee': 'Combined pass available',
                    'features': ['Historic buildings', 'Religious site']
                },
                {
                    'name': 'Andaw-thein Ordination Hall',
                    'type': 'attraction',
                    'description': 'Known for its stone carvings and architecture.',
                    'region': 'Rakhine State',
                    'rating': 4.3,
                    'review_count': 45,
                    'entry_fee': 'Combined pass available',
                    'features': ['Historic buildings', 'Religious site']
                }
            ]
        }
        
        # Create attractions for each destination
        attractions_created = 0
        
        for city_name, attractions in attractions_data.items():
            try:
                # Find the parent city - SIMPLIFIED without Q
                parent_city = None
                
                # Try exact match first
                try:
                    parent_city = Destination.objects.get(name__iexact=city_name)
                except Destination.DoesNotExist:
                    pass
                
                if not parent_city:
                    # Try contains match
                    parent_city = Destination.objects.filter(
                        name__icontains=city_name,
                        type__in=['city', 'town']
                    ).first()
                
                if not parent_city:
                    # Try by region
                    parent_city = Destination.objects.filter(
                        region__icontains=city_name,
                        type__in=['city', 'town']
                    ).first()
                
                if parent_city:
                    self.stdout.write(f"Found parent city: {parent_city.name} for {city_name}")
                    
                    for attr_data in attractions:
                        # Check if attraction already exists
                        existing = Destination.objects.filter(
                            name=attr_data['name']
                        ).first()
                        
                        if not existing:
                            # Format description with all details
                            full_description = attr_data['description']
                            full_description += f"\n\nRating: {attr_data.get('rating', 'N/A')}/5"
                            full_description += f"\nReviews: {attr_data.get('review_count', 0)}"
                            full_description += f"\nEntry Fee: {attr_data.get('entry_fee', 'Free entry')}"
                            if 'distance_from_city' in attr_data:
                                full_description += f"\nDistance: {attr_data['distance_from_city']}"
                            if 'features' in attr_data:
                                full_description += f"\nFeatures: {', '.join(attr_data['features'])}"
                            
                            # Create new attraction
                            attraction = Destination.objects.create(
                                name=attr_data['name'],
                                type=attr_data['type'],
                                description=full_description,
                                region=attr_data['region'],
                                parent=parent_city,
                                is_region=False,
                                is_active=True
                            )
                            
                            attractions_created += 1
                            self.stdout.write(f"  ✅ Created: {attr_data['name']}")
                        else:
                            self.stdout.write(f"  ⏩ Already exists: {attr_data['name']}")
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Parent city not found for: {city_name}"))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error creating attractions for {city_name}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Successfully created {attractions_created} new attractions"))