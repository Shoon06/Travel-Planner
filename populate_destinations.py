# C:\Users\ASUS\MyanmarTravelPlanner\populate_destinations.py

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models import Destination

def add_yangon_destinations():
    """Add more destinations to Yangon Region"""
    yangon_places = [
        {
            'name': 'Shwedagon Pagoda',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': 'Most sacred Buddhist pagoda in Myanmar, covered in gold plates and studded with diamonds.'
        },
        {
            'name': 'Sule Pagoda',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': '2,000-year-old pagoda located in downtown Yangon, important political landmark.'
        },
        {
            'name': 'Botahtaung Pagoda',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': 'Hollow pagoda with a maze-like interior containing Buddha relics.'
        },
        {
            'name': 'Chaukhtatgyi Buddha Temple',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': 'Home to one of the largest reclining Buddha images in Myanmar.'
        },
        {
            'name': 'National Museum of Myanmar',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': 'Largest museum in Myanmar showcasing the country\'s history and culture.'
        },
        {
            'name': 'Yangon Circular Railway',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': '46km circular train ride offering glimpses of local life.'
        },
        {
            'name': 'People\'s Square and Park',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': 'Large public park with fountains and the Independence Monument.'
        },
        {
            'name': 'Yangon River',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': 'Major river with ferry rides offering city skyline views.'
        },
        {
            'name': 'Kandawgyi Lake',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': 'Artificial lake with Karaweik Palace replica and beautiful sunset views.'
        },
        {
            'name': 'Bogyoke Aung San Market',
            'region': 'Yangon Region',
            'type': 'shopping',
            'description': 'Colonial-era market with hundreds of shops selling handicrafts, jewelry, and souvenirs.'
        },
        {
            'name': 'Saint Mary\'s Cathedral',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': 'Largest Catholic church in Myanmar, built in neo-Gothic style.'
        },
        {
            'name': 'Ngahtatgyi Buddha Temple',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': 'Impressive seated Buddha image with intricate details.'
        },
        {
            'name': 'Mahabandoola Garden',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': 'Public park with Independence Monument and colonial-era buildings.'
        },
        {
            'name': 'Thakin Mya Park',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': 'Peaceful green space perfect for relaxing and picnics.'
        },
        {
            'name': 'Yangon Zoological Gardens',
            'region': 'Yangon Region',
            'type': 'attraction',
            'description': 'Oldest zoo in Myanmar with various animal species.'
        }
    ]
    
    for place in yangon_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(yangon_places)} destinations to Yangon Region")

def add_mandalay_destinations():
    """Add more destinations to Mandalay Region"""
    mandalay_places = [
        {
            'name': 'Mandalay Palace',
            'region': 'Mandalay Region',
            'type': 'attraction',
            'description': 'Last royal palace of the last Burmese monarchy, rebuilt after WWII.'
        },
        {
            'name': 'Mandalay Hill',
            'region': 'Mandalay Region',
            'type': 'attraction',
            'description': '240m hill offering panoramic views of Mandalay and surrounding areas.'
        },
        {
            'name': 'Kuthodaw Pagoda',
            'region': 'Mandalay Region',
            'type': 'attraction',
            'description': 'Known as the world\'s largest book with 729 marble slabs inscribed with Buddhist scriptures.'
        },
        {
            'name': 'Mingun Pahtodawgyi',
            'region': 'Mandalay Region',
            'type': 'attraction',
            'description': 'Massive unfinished stupa with impressive cracks from an earthquake.'
        },
        {
            'name': 'Mahamuni Buddha Temple',
            'region': 'Mandalay Region',
            'type': 'attraction',
            'description': 'One of the most important pilgrimage sites in Myanmar.'
        },
        {
            'name': 'Sagaing Hill',
            'region': 'Mandalay Region',
            'type': 'attraction',
            'description': 'Hill with numerous monasteries and meditation centers.'
        },
        {
            'name': 'U Bein Bridge',
            'region': 'Mandalay Region',
            'type': 'attraction',
            'description': '1.2km teak footbridge across Taungthaman Lake, longest teak bridge in the world.'
        },
        {
            'name': 'Shwenandaw Monastery',
            'region': 'Mandalay Region',
            'type': 'attraction',
            'description': 'Exquisite teak wood monastery with intricate carvings.'
        },
        {
            'name': 'Inwa (Ava)',
            'region': 'Mandalay Region',
            'type': 'attraction',
            'description': 'Ancient capital accessible by boat with ruins and monasteries.'
        },
        {
            'name': 'Amarapura',
            'region': 'Mandalay Region',
            'type': 'attraction',
            'description': 'Ancient capital known for silk weaving and U Bein Bridge.'
        },
        {
            'name': 'Kyauktawgyi Temple',
            'region': 'Mandalay Region',
            'type': 'attraction',
            'description': 'Temple housing a large Buddha image carved from single marble block.'
        },
        {
            'name': 'Mingun Bell',
            'region': 'Mandalay Region',
            'type': 'attraction',
            'description': 'World\'s second largest ringing bell, weighing 90 tons.'
        },
        {
            'name': 'Atumashi Monastery',
            'region': 'Mandalay Region',
            'type': 'attraction',
            'description': 'Beautiful monastery known as the "Incomparable Monastery".'
        }
    ]
    
    for place in mandalay_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(mandalay_places)} destinations to Mandalay Region")

def add_bagan_destinations():
    """Add more destinations to Bagan"""
    bagan_places = [
        {
            'name': 'Ananda Temple',
            'region': 'Bagan',
            'type': 'attraction',
            'description': 'One of the most beautiful and best preserved temples in Bagan.'
        },
        {
            'name': 'Dhammayangyi Temple',
            'region': 'Bagan',
            'type': 'attraction',
            'description': 'Largest temple in Bagan with mysterious bricked-up inner passageways.'
        },
        {
            'name': 'Thatbyinnyu Temple',
            'region': 'Bagan',
            'type': 'attraction',
            'description': 'Tallest temple in Bagan, offering panoramic views.'
        },
        {
            'name': 'Shwezigon Pagoda',
            'region': 'Bagan',
            'type': 'attraction',
            'description': 'Golden pagoda prototype for many later pagodas in Myanmar.'
        },
        {
            'name': 'Htilominlo Temple',
            'region': 'Bagan',
            'type': 'attraction',
            'description': 'Last Myanmar-style temple built in Bagan with fine plaster carvings.'
        },
        {
            'name': 'Shwesandaw Pagoda',
            'region': 'Bagan',
            'type': 'attraction',
            'description': 'Popular sunset viewing spot with 360-degree views.'
        },
        {
            'name': 'Sulamani Temple',
            'region': 'Bagan',
            'type': 'attraction',
            'description': 'Beautifully proportioned temple known as the "Crowning Jewel".'
        },
        {
            'name': 'Gawdawpalin Temple',
            'region': 'Bagan',
            'type': 'attraction',
            'description': 'One of the largest and most imposing temples in Bagan.'
        },
        {
            'name': 'Manuha Temple',
            'region': 'Bagan',
            'type': 'attraction',
            'description': 'Built by captive Mon king Manuha with unusually large Buddha images.'
        },
        {
            'name': 'Bagan Archaeological Museum',
            'region': 'Bagan',
            'type': 'attraction',
            'description': 'Museum showcasing Bagan\'s history and archaeological finds.'
        },
        {
            'name': 'Mount Popa',
            'region': 'Bagan',
            'type': 'attraction',
            'description': 'Volcanic peak with monastery on top, considered home of Myanmar\'s nats (spirits).'
        },
        {
            'name': 'Buphaya Pagoda',
            'region': 'Bagan',
            'type': 'attraction',
            'description': 'Distinctive gourd-shaped pagoda on the banks of Irrawaddy River.'
        }
    ]
    
    for place in bagan_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(bagan_places)} destinations to Bagan")

def add_inle_lake_destinations():
    """Add more destinations to Inle Lake area"""
    inle_places = [
        {
            'name': 'Inle Lake',
            'region': 'Shan State',
            'type': 'attraction',
            'description': 'Second largest lake in Myanmar known for floating villages and leg-rowing fishermen.'
        },
        {
            'name': 'Phaung Daw Oo Pagoda',
            'region': 'Shan State',
            'type': 'attraction',
            'description': 'Most famous pagoda on Inle Lake with five Buddha images.'
        },
        {
            'name': 'Indein Village',
            'region': 'Shan State',
            'type': 'attraction',
            'description': 'Village with ancient stupa field and scenic boat ride through narrow canals.'
        },
        {
            'name': 'Nyaung Shwe',
            'region': 'Shan State',
            'type': 'attraction',
            'description': 'Gateway town to Inle Lake with local markets and cultural sites.'
        },
        {
            'name': 'Floating Gardens',
            'region': 'Shan State',
            'type': 'attraction',
            'description': 'Hydroponic farms floating on the lake, growing vegetables and flowers.'
        },
        {
            'name': 'Jumping Cat Monastery',
            'region': 'Shan State',
            'type': 'attraction',
            'description': 'Wooden monastery known for cats trained to jump through hoops.'
        },
        {
            'name': 'Shwe Yan Pyay Monastery',
            'region': 'Shan State',
            'type': 'attraction',
            'description': 'Beautiful 19th century wooden monastery with oval windows.'
        },
        {
            'name': 'Kakku Pagodas',
            'region': 'Shan State',
            'type': 'attraction',
            'description': 'Complex of over 2,000 stupas, some dating back 2,000 years.'
        },
        {
            'name': 'Taunggyi',
            'region': 'Shan State',
            'type': 'attraction',
            'description': 'Capital of Shan State known for its hot air balloon festival.'
        },
        {
            'name': 'Pindaya Caves',
            'region': 'Shan State',
            'type': 'attraction',
            'description': 'Limestone caves filled with thousands of Buddha images.'
        }
    ]
    
    for place in inle_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(inle_places)} destinations to Shan State")

def add_mon_state_destinations():
    """Add destinations to Mon State"""
    mon_places = [
        {
            'name': 'Golden Rock (Kyaiktiyo Pagoda)',
            'region': 'Mon State',
            'type': 'attraction',
            'description': 'Small pagoda built on a gold-gilded boulder balancing on a cliff edge.'
        },
        {
            'name': 'Mawlamyine',
            'region': 'Mon State',
            'type': 'city',
            'description': 'Former British colonial capital with multicultural heritage.'
        },
        {
            'name': 'Thanbyuzayat War Cemetery',
            'region': 'Mon State',
            'type': 'attraction',
            'description': 'WWII cemetery for Allied prisoners who died building the Death Railway.'
        },
        {
            'name': 'Setse Beach',
            'region': 'Mon State',
            'type': 'beach',
            'description': 'Beautiful sandy beach popular with locals and tourists.'
        },
        {
            'name': 'Win Sein Taw Ya',
            'region': 'Mon State',
            'type': 'attraction',
            'description': 'World\'s largest reclining Buddha statue, 180 meters long.'
        },
        {
            'name': 'Bilukyun (Ogre Island)',
            'region': 'Mon State',
            'type': 'attraction',
            'description': 'Large island known for its seafood and traditional fishing villages.'
        }
    ]
    
    for place in mon_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(mon_places)} destinations to Mon State")

def add_ayeyarwady_destinations():
    """Add destinations to Ayeyarwady Region"""
    ayeyarwady_places = [
        {
            'name': 'Pathein',
            'region': 'Ayeyarwady Region',
            'type': 'city',
            'description': 'Capital of Ayeyarwady Region, famous for its umbrella making industry.'
        },
        {
            'name': 'Chaung Tha Beach',
            'region': 'Ayeyarwady Region',
            'type': 'beach',
            'description': 'Popular beach destination with palm-fringed coastline.'
        },
        {
            'name': 'Ngwe Saung Beach',
            'region': 'Ayeyarwady Region',
            'type': 'beach',
            'description': '15km long white sand beach, less developed than Chaung Tha.'
        },
        {
            'name': 'Myaungmya',
            'region': 'Ayeyarwady Region',
            'type': 'city',
            'description': 'Town known for its pagodas and traditional festivals.'
        }
    ]
    
    for place in ayeyarwady_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(ayeyarwady_places)} destinations to Ayeyarwady Region")

def add_rakhine_destinations():
    """Add destinations to Rakhine State"""
    rakhine_places = [
        {
            'name': 'Ngapali Beach',
            'region': 'Rakhine State',
            'type': 'beach',
            'description': 'Most famous beach in Myanmar with pristine white sand and clear water.'
        },
        {
            'name': 'Mrauk U',
            'region': 'Rakhine State',
            'type': 'attraction',
            'description': 'Ancient capital with temple ruins often compared to Bagan.'
        },
        {
            'name': 'Sittwe',
            'region': 'Rakhine State',
            'type': 'city',
            'description': 'Capital of Rakhine State and gateway to Mrauk U.'
        },
        {
            'name': 'Shittaung Temple',
            'region': 'Rakhine State',
            'type': 'attraction',
            'description': '"Temple of 80,000 Images" in Mrauk U with intricate carvings.'
        },
        {
            'name': 'Kothaung Temple',
            'region': 'Rakhine State',
            'type': 'attraction',
            'description': 'Largest temple in Mrauk U, "Temple of 90,000 Images".'
        }
    ]
    
    for place in rakhine_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(rakhine_places)} destinations to Rakhine State")

def add_kayin_destinations():
    """Add destinations to Kayin State"""
    kayin_places = [
        {
            'name': 'Hpa-an',
            'region': 'Kayin State',
            'type': 'city',
            'description': 'Capital of Kayin State surrounded by limestone mountains and caves.'
        },
        {
            'name': 'Mount Zwegabin',
            'region': 'Kayin State',
            'type': 'attraction',
            'description': 'Sacred mountain with pagoda on top offering panoramic views.'
        },
        {
            'name': 'Sadang Cave',
            'region': 'Kayin State',
            'type': 'attraction',
            'description': 'Large cave system with Buddha images and streams.'
        },
        {
            'name': 'Kawgun Cave',
            'region': 'Kayin State',
            'type': 'attraction',
            'description': 'Cave filled with thousands of clay Buddha images and tablets.'
        },
        {
            'name': 'Kyauk Kalap',
            'region': 'Kayin State',
            'type': 'attraction',
            'description': 'Monastery on a narrow rock pillar rising from a lake.'
        }
    ]
    
    for place in kayin_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(kayin_places)} destinations to Kayin State")

def add_kachin_destinations():
    """Add destinations to Kachin State"""
    kachin_places = [
        {
            'name': 'Myitkyina',
            'region': 'Kachin State',
            'type': 'city',
            'description': 'Capital of Kachin State on the Irrawaddy River.'
        },
        {
            'name': 'Putao',
            'region': 'Kachin State',
            'type': 'city',
            'description': 'Northernmost town in Myanmar, gateway to Himalayan trekking.'
        },
        {
            'name': 'Indawgyi Lake',
            'region': 'Kachin State',
            'type': 'attraction',
            'description': 'Largest inland lake in Myanmar, UNESCO Biosphere Reserve.'
        },
        {
            'name': 'Myitsone',
            'region': 'Kachin State',
            'type': 'attraction',
            'description': 'Confluence of Mali and N Mai rivers forming the Irrawaddy River.'
        },
        {
            'name': 'Hkakabo Razi',
            'region': 'Kachin State',
            'type': 'attraction',
            'description': 'Highest mountain in Myanmar and Southeast Asia.'
        }
    ]
    
    for place in kachin_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(kachin_places)} destinations to Kachin State")

def add_kayah_destinations():
    """Add destinations to Kayah State"""
    kayah_places = [
        {
            'name': 'Loikaw',
            'region': 'Kayah State',
            'type': 'city',
            'description': 'Capital of Kayah State, home to the Kayan (long-neck) people.'
        },
        {
            'name': 'Taung Kwe Pagoda',
            'region': 'Kayah State',
            'type': 'attraction',
            'description': 'Pagoda complex built on limestone peaks with panoramic views.'
        },
        {
            'name': 'Demawso',
            'region': 'Kayah State',
            'type': 'city',
            'description': 'Town known for traditional Kayah culture and festivals.'
        }
    ]
    
    for place in kayah_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(kayah_places)} destinations to Kayah State")

def add_chin_destinations():
    """Add destinations to Chin State"""
    chin_places = [
        {
            'name': 'Mindat',
            'region': 'Chin State',
            'type': 'city',
            'description': 'Town known for Chin tribes with traditional facial tattoos.'
        },
        {
            'name': 'Mount Victoria (Nat Ma Taung)',
            'region': 'Chin State',
            'type': 'attraction',
            'description': 'Highest peak in Chin State, popular for trekking and bird watching.'
        },
        {
            'name': 'Kanpetlet',
            'region': 'Chin State',
            'type': 'city',
            'description': 'Base for trekking to Mount Victoria, traditional Chin villages.'
        }
    ]
    
    for place in chin_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(chin_places)} destinations to Chin State")

def add_sagaing_destinations():
    """Add destinations to Sagaing Region"""
    sagaing_places = [
        {
            'name': 'Sagaing',
            'region': 'Sagaing Region',
            'type': 'city',
            'description': 'Ancient capital and important religious center with numerous monasteries.'
        },
        {
            'name': 'Monywa',
            'region': 'Sagaing Region',
            'type': 'city',
            'description': 'Major trading center known for nearby archaeological sites.'
        },
        {
            'name': 'Bodhi Tataung',
            'region': 'Sagaing Region',
            'type': 'attraction',
            'description': 'Site with thousand Buddha images and the world\'s second tallest Buddha statue.'
        },
        {
            'name': 'Thanboddhay Pagoda',
            'region': 'Sagaing Region',
            'type': 'attraction',
            'description': 'Colorful pagoda with over 500,000 Buddha images.'
        },
        {
            'name': 'Po Win Daung Caves',
            'region': 'Sagaing Region',
            'type': 'attraction',
            'description': 'Complex of sandstone caves with Buddhist murals and sculptures.'
        }
    ]
    
    for place in sagaing_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(sagaing_places)} destinations to Sagaing Region")

def add_magway_destinations():
    """Add destinations to Magway Region"""
    magway_places = [
        {
            'name': 'Magway',
            'region': 'Magway Region',
            'type': 'city',
            'description': 'Capital of Magway Region, center of Myanmar\'s oil industry.'
        },
        {
            'name': 'Minbu',
            'region': 'Magway Region',
            'type': 'city',
            'description': 'Town known for its hot springs and salt production.'
        },
        {
            'name': 'Salay',
            'region': 'Magway Region',
            'type': 'attraction',
            'description': 'Ancient town with well-preserved wooden monastery and colonial buildings.'
        },
        {
            'name': 'Yokesone Monastery',
            'region': 'Magway Region',
            'type': 'attraction',
            'description': 'Beautiful teak wood monastery in Salay with intricate carvings.'
        }
    ]
    
    for place in magway_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(magway_places)} destinations to Magway Region")

def add_tanintharyi_destinations():
    """Add destinations to Tanintharyi Region"""
    tanintharyi_places = [
        {
            'name': 'Dawei',
            'region': 'Tanintharyi Region',
            'type': 'city',
            'description': 'Capital of Tanintharyi Region with beautiful beaches nearby.'
        },
        {
            'name': 'Myeik (Mergui)',
            'region': 'Tanintharyi Region',
            'type': 'city',
            'description': 'Coastal city and gateway to the Mergui Archipelago.'
        },
        {
            'name': 'Mergui Archipelago',
            'region': 'Tanintharyi Region',
            'type': 'beach',
            'description': 'Group of 800 islands with pristine beaches and excellent diving.'
        },
        {
            'name': 'Maungmagan Beach',
            'region': 'Tanintharyi Region',
            'type': 'beach',
            'description': 'Beautiful beach near Dawei with black sand in some areas.'
        }
    ]
    
    for place in tanintharyi_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(tanintharyi_places)} destinations to Tanintharyi Region")

def add_naypyidaw_destinations():
    """Add destinations to Naypyidaw Union Territory"""
    naypyidaw_places = [
        {
            'name': 'Naypyidaw',
            'region': 'Naypyidaw Union Territory',
            'type': 'city',
            'description': 'Capital city of Myanmar, known for its wide roads and monumental buildings.'
        },
        {
            'name': 'Uppatasanti Pagoda',
            'region': 'Naypyidaw Union Territory',
            'type': 'attraction',
            'description': 'Replica of Yangon\'s Shwedagon Pagoda, slightly shorter.'
        },
        {
            'name': 'Naypyidaw Zoological Gardens',
            'region': 'Naypyidaw Union Territory',
            'type': 'attraction',
            'description': 'Largest zoo in Myanmar with safari park and penguin exhibit.'
        },
        {
            'name': 'National Landmarks Garden',
            'region': 'Naypyidaw Union Territory',
            'type': 'attraction',
            'description': 'Park with miniature replicas of Myanmar\'s famous landmarks.'
        },
        {
            'name': 'Naypyidaw Water Fountain Garden',
            'region': 'Naypyidaw Union Territory',
            'type': 'attraction',
            'description': 'Large park with musical fountain shows.'
        }
    ]
    
    for place in naypyidaw_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(naypyidaw_places)} destinations to Naypyidaw Union Territory")

def add_all_destinations():
    """Add destinations from all regions of Myanmar"""
    # Major tourist regions
    add_yangon_destinations()
    add_mandalay_destinations()
    add_bagan_destinations()
    add_inle_lake_destinations()
    
    # Other states and regions
    add_mon_state_destinations()
    add_ayeyarwady_destinations()
    add_rakhine_destinations()
    add_kayin_destinations()
    add_kachin_destinations()
    add_kayah_destinations()
    add_chin_destinations()
    add_sagaing_destinations()
    add_magway_destinations()
    add_tanintharyi_destinations()
    add_naypyidaw_destinations()
    
    # Add some special categories
    add_beach_destinations()
    add_festival_destinations()
    add_adventure_destinations()

def add_beach_destinations():
    """Add beach destinations across Myanmar"""
    beach_places = [
        {
            'name': 'Ngapali Beach',
            'region': 'Rakhine State',
            'type': 'beach',
            'description': 'Most famous beach in Myanmar with pristine white sand and clear water.'
        },
        {
            'name': 'Chaung Tha Beach',
            'region': 'Ayeyarwady Region',
            'type': 'beach',
            'description': 'Popular beach destination with palm-fringed coastline.'
        },
        {
            'name': 'Ngwe Saung Beach',
            'region': 'Ayeyarwady Region',
            'type': 'beach',
            'description': '15km long white sand beach, less developed than Chaung Tha.'
        },
        {
            'name': 'Setse Beach',
            'region': 'Mon State',
            'type': 'beach',
            'description': 'Beautiful sandy beach popular with locals and tourists.'
        },
        {
            'name': 'Maungmagan Beach',
            'region': 'Tanintharyi Region',
            'type': 'beach',
            'description': 'Beautiful beach near Dawei with black sand in some areas.'
        }
    ]
    
    for place in beach_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(beach_places)} beach destinations")

def add_festival_destinations():
    """Add festival-related destinations"""
    festival_places = [
        {
            'name': 'Taunggyi Fire Balloon Festival',
            'region': 'Shan State',
            'type': 'festival',
            'description': 'Annual festival with hot air balloons, some carrying fireworks.'
        },
        {
            'name': 'Thingyan Water Festival',
            'region': 'Nationwide',
            'type': 'festival',
            'description': 'Burmese New Year celebration with water throwing festivities.'
        },
        {
            'name': 'Phaya Gyi Pagoda Festival',
            'region': 'Mon State',
            'type': 'festival',
            'description': 'Annual festival at the Golden Rock attracting thousands of pilgrims.'
        },
        {
            'name': 'Shwedagon Pagoda Festival',
            'region': 'Yangon Region',
            'type': 'festival',
            'description': 'Annual festival celebrating the full moon day of Tabaung.'
        }
    ]
    
    for place in festival_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(festival_places)} festival destinations")

def add_adventure_destinations():
    """Add adventure and trekking destinations"""
    adventure_places = [
        {
            'name': 'Putao Trekking',
            'region': 'Kachin State',
            'type': 'adventure',
            'description': 'Trekking in remote Himalayan foothills near the Myanmar-India border.'
        },
        {
            'name': 'Mount Victoria Trek',
            'region': 'Chin State',
            'type': 'adventure',
            'description': 'Trek to the highest peak in Chin State through traditional villages.'
        },
        {
            'name': 'Mergui Archipelago Diving',
            'region': 'Tanintharyi Region',
            'type': 'adventure',
            'description': 'Scuba diving in the pristine waters of the Mergui Archipelago.'
        },
        {
            'name': 'Balloon Over Bagan',
            'region': 'Bagan',
            'type': 'adventure',
            'description': 'Hot air balloon rides over the ancient temples of Bagan at sunrise.'
        },
        {
            'name': 'Irrawaddy River Cruise',
            'region': 'Multiple Regions',
            'type': 'adventure',
            'description': 'River cruises along Myanmar\'s main waterway from Bagan to Mandalay.'
        }
    ]
    
    for place in adventure_places:
        Destination.objects.get_or_create(
            name=place['name'],
            defaults={
                'region': place['region'],
                'type': place['type'],
                'description': place['description'],
                'is_active': True,
            }
        )
    
    print(f"Added {len(adventure_places)} adventure destinations")

if __name__ == '__main__':
    print("Starting to populate Myanmar destinations database...\n")
    
    # Add all destinations from all regions
    add_all_destinations()
    
    # Get statistics
    total_count = Destination.objects.filter(is_active=True).count()
    regions = Destination.objects.filter(is_active=True).values_list('region', flat=True).distinct()
    
    print(f"\n{'='*60}")
    print(f"Database population complete!")
    print(f"{'='*60}")
    print(f"Total destinations in database: {total_count}")
    print(f"Regions covered: {len(regions)}")
    print(f"\nRegions list:")
    for region in sorted(regions):
        count = Destination.objects.filter(region=region, is_active=True).count()
        print(f"  - {region}: {count} destinations")
    
    print(f"\nDestination types distribution:")
    types = Destination.objects.filter(is_active=True).values_list('type', flat=True).distinct()
    for type_name in sorted(types):
        count = Destination.objects.filter(type=type_name, is_active=True).count()
        print(f"  - {type_name}: {count}")
    
    print(f"\nDone! Myanmar travel destinations database is ready.")