from django.core.management.base import BaseCommand
from planner.models import Attraction, Destination, Hotel, Flight, BusService, CarRental, Airline, TransportSchedule
from decimal import Decimal
from datetime import time, timedelta, datetime
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate database with sample data for Myanmar Travel Planner'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting comprehensive data population...')
        
        # Create destinations
        self.populate_destinations()
        
        # Populate attractions so map has data
        self.populate_attractions()
        
        # Populate hotels
        self.populate_hotels()
        
        # Populate COMPREHENSIVE transport data
        self.populate_comprehensive_transport()
        
        # Create transport schedules
        self.create_transport_schedules()
        
        self.stdout.write(self.style.SUCCESS('All data populated successfully!'))
    
    def populate_destinations(self):
        """Populate destination data"""
        self.stdout.write('Populating destinations...')
        
        # Base destinations required by other seeders (keep names stable for FK lookups)
        base_destinations = [
            {"name": "Inle Lake", "region": "Shan State", "type": "attraction",
             "description": "Freshwater lake known for floating villages and leg-rowing fishermen.",
             "latitude": 20.5550, "longitude": 96.9150},
            {"name": "Ngapali Beach", "region": "Rakhine State", "type": "attraction",
             "description": "Pristine beach with white sand and clear water.",
             "latitude": 18.4159, "longitude": 94.2977},
            {"name": "Ngwe Saung Beach", "region": "Ayeyarwady Region", "type": "attraction",
             "description": "Beautiful beach resort area near Yangon.",
             "latitude": 16.8533, "longitude": 94.3589},
            {"name": "Kachin", "region": "Northern Myanmar", "type": "state",
             "description": "Northernmost state known for jade mines and Hkakabo Razi mountain."},
            {"name": "Kayah", "region": "Eastern Myanmar", "type": "state",
             "description": "Eastern state known for traditional long-necked women and scenic mountains."},
            {"name": "Kayin", "region": "Southeastern Myanmar", "type": "state",
             "description": "State bordering Thailand known for waterfalls and Karen culture."},
            {"name": "Chin", "region": "Western Myanmar", "type": "state",
             "description": "Western state with mountainous terrain and unique tribal cultures."},
            {"name": "Mon", "region": "Southern Myanmar", "type": "state",
             "description": "Southern state with ancient Mon civilization and beaches."},
            {"name": "Rakhine", "region": "Western Myanmar", "type": "state",
             "description": "Western coastal state with Ngapali Beach and ancient Mrauk U."},
            {"name": "Shan", "region": "Eastern Myanmar", "type": "state",
             "description": "Largest state known for Inle Lake, hill tribes, and tea plantations."},
        ]

        # New city/town dataset (replacement for previous city seeds)
        city_destinations = [
            {"name": "Amarapura", "region": "Mandalay Region", "type": "city", "description": "Former royal capital known for the U Bein Bridge and silk weaving.", "latitude": 21.9028, "longitude": 96.0469},
            {"name": "Bagan", "region": "Mandalay Region", "type": "city", "description": "Ancient city with over 2,000 Buddhist temples and pagodas.", "latitude": 21.1717, "longitude": 94.8585},
            {"name": "Bago", "region": "Bago Region", "type": "city", "description": "Ancient capital of the Mon Kingdom featuring massive pagodas and reclining Buddhas.", "latitude": 17.3332, "longitude": 96.4822},
            {"name": "Bogale", "region": "Ayeyarwady Region", "type": "town", "description": "Gateway to the Meinmahla Kyun Wildlife Sanctuary in the Delta region.", "latitude": 16.2931, "longitude": 95.3975},
            {"name": "Dawei", "region": "Tanintharyi Region", "type": "city", "description": "Capital of Tanintharyi, famous for its untouched beaches and colonial charm.", "latitude": 14.0828, "longitude": 98.1940},
            {"name": "Hakha", "region": "Chin State", "type": "city", "description": "Capital of Chin State, situated on a mountain slope with cool climates.", "latitude": 22.6425, "longitude": 93.6186},
            {"name": "Heho", "region": "Shan State", "type": "town", "description": "The primary air gateway to Inle Lake and the southern Shan State hills.", "latitude": 20.7431, "longitude": 96.7919},
            {"name": "Hinthada", "region": "Ayeyarwady Region", "type": "city", "description": "A major river port city in the Ayeyarwady Delta.", "latitude": 17.6506, "longitude": 95.4542},
            {"name": "Hmawbi", "region": "Yangon Region", "type": "town", "description": "Home to Hlawga National Park and a significant agricultural hub.", "latitude": 17.1086, "longitude": 96.0403},
            {"name": "Hpa-An", "region": "Kayin State", "type": "town", "description": "Capital of Kayin State, famous for dramatic limestone mountains and caves.", "latitude": 16.8894, "longitude": 97.6343},
            {"name": "Hsipaw", "region": "Shan State", "type": "town", "description": "A charming trekking hub and home to the historic Shan Palace.", "latitude": 22.6286, "longitude": 97.3375},
            {"name": "Kalaw", "region": "Shan State", "type": "town", "description": "A former British colonial hill station popular for its trekking routes.", "latitude": 20.6260, "longitude": 96.5623},
            {"name": "Kalay", "region": "Sagaing Region", "type": "city", "description": "An important trading hub near the Indian border and Chin State.", "latitude": 23.1906, "longitude": 94.0286},
            {"name": "Kawthaung", "region": "Tanintharyi Region", "type": "city", "description": "The southernmost town in Myanmar, gateway to the Myeik Archipelago.", "latitude": 9.9825, "longitude": 98.5503},
            {"name": "Labutta", "region": "Ayeyarwady Region", "type": "town", "description": "A major rice and salt production center in the Delta region.", "latitude": 16.1420, "longitude": 94.7570},
            {"name": "Letpadan", "region": "Bago Region", "type": "town", "description": "A key agricultural and transport junction in the Bago Region.", "latitude": 17.7844, "longitude": 95.7539},
            {"name": "Loikaw", "region": "Kayah State", "type": "city", "description": "Capital of Kayah State, known for the Taung Kwe Pagoda and Padaung villages.", "latitude": 19.6742, "longitude": 97.2094},
            {"name": "Magway", "region": "Magway Region", "type": "city", "description": "A major river port and center for sesame and groundnut oil production.", "latitude": 20.1496, "longitude": 94.9320},
            {"name": "Mandalay", "region": "Mandalay Region", "type": "city", "description": "The last royal capital of Myanmar and its primary cultural center.", "latitude": 21.9588, "longitude": 96.0891},
            {"name": "Mawlamyine", "region": "Mon State", "type": "city", "description": "Third largest city, former British colonial capital and gateway to the south.", "latitude": 16.4802, "longitude": 97.6212},
            {"name": "Meiktila", "region": "Mandalay Region", "type": "city", "description": "A key transport hub and home to the scenic Meiktila Lake.", "latitude": 20.8752, "longitude": 95.8458},
            {"name": "Monywa", "region": "Sagaing Region", "type": "city", "description": "Known for the Thanboddhay Pagoda and the world's second tallest standing Buddha.", "latitude": 22.1167, "longitude": 95.1333},
            {"name": "Myaungmya", "region": "Ayeyarwady Region", "type": "city", "description": "A significant rice-producing city in the heart of the Delta.", "latitude": 16.5947, "longitude": 94.9292},
            {"name": "Myeik", "region": "Tanintharyi Region", "type": "city", "description": "Famous for the 800 islands of the surrounding archipelago and pearl farming.", "latitude": 12.4377, "longitude": 98.6007},
            {"name": "Myitkyina", "region": "Kachin State", "type": "city", "description": "Capital of Kachin State, located at the head of the Irrawaddy River.", "latitude": 25.3833, "longitude": 97.4000},
            {"name": "Naypyidaw", "region": "Naypyidaw Union Territory", "type": "city", "description": "The planned administrative capital of Myanmar since 2005.", "latitude": 19.7460, "longitude": 96.1270},
            {"name": "Nyaunglebin", "region": "Bago Region", "type": "town", "description": "A historic commercial hub in eastern Bago Region.", "latitude": 17.9547, "longitude": 96.7328},
            {"name": "Pakokku", "region": "Magway Region", "type": "city", "description": "Known for its tobacco trade, weaving, and the historic Thiho Shin Pagoda.", "latitude": 21.3325, "longitude": 95.0789},
            {"name": "Pathein", "region": "Ayeyarwady Region", "type": "city", "description": "Capital of the Ayeyarwady Region, famous for its colorful handmade umbrellas.", "latitude": 16.7770, "longitude": 94.7279},
            {"name": "Paungde", "region": "Bago Region", "type": "town", "description": "A historical city known for the ancient Myat Saw Taw pagoda.", "latitude": 18.4764, "longitude": 95.5125},
            {"name": "Pyay", "region": "Bago Region", "type": "city", "description": "Ancient city near the ruins of the Pyu Kingdom capital, Sri Ksetra.", "latitude": 18.8236, "longitude": 95.2239},
            {"name": "Pyin Oo Lwin", "region": "Mandalay Region", "type": "town", "description": "Scenic hill station famous for its botanical gardens and colonial architecture.", "latitude": 22.0339, "longitude": 96.4561},
            {"name": "Sagaing", "region": "Sagaing Region", "type": "city", "description": "Religious center with hundreds of pagodas and monasteries dotting the hills.", "latitude": 21.8831, "longitude": 95.9782},
            {"name": "Shwebo", "region": "Sagaing Region", "type": "city", "description": "Origin of the Konbaung Dynasty and known for high-quality rice production.", "latitude": 22.5683, "longitude": 95.6983},
            {"name": "Shwegyin", "region": "Bago Region", "type": "town", "description": "A quiet town on the banks of the Shwegyin River known for traditional festivals.", "latitude": 17.9158, "longitude": 96.8775},
            {"name": "Sittwe", "region": "Rakhine State", "type": "city", "description": "Coastal capital of Rakhine State and a significant seaport.", "latitude": 20.1400, "longitude": 92.8997},
            {"name": "Tachileik", "region": "Shan State", "type": "city", "description": "A bustling border town in the Golden Triangle adjacent to Thailand.", "latitude": 20.4481, "longitude": 99.8808},
            {"name": "Taunggyi", "region": "Shan State", "type": "city", "description": "Capital of Shan State and famous for its spectacular Fire Balloon Festival.", "latitude": 20.7853, "longitude": 97.0374},
            {"name": "Taungoo", "region": "Bago Region", "type": "city", "description": "An ancient capital of the Taungoo Dynasty located on the Sittaung River.", "latitude": 18.9333, "longitude": 96.4333},
            {"name": "Thandwe", "region": "Rakhine State", "type": "town", "description": "Gateway to the world-famous Ngapali Beach.", "latitude": 18.4608, "longitude": 94.2997},
            {"name": "Tharrawaddy", "region": "Bago Region", "type": "town", "description": "A historical district capital in western Bago Region.", "latitude": 17.6533, "longitude": 95.7950},
            {"name": "Wakema", "region": "Ayeyarwady Region", "type": "town", "description": "A central Delta town known for its water-based commerce.", "latitude": 16.6022, "longitude": 95.1844},
            {"name": "Yangon", "region": "Yangon Region", "type": "city", "description": "The economic hub and former capital, home to the Shwedagon Pagoda.", "latitude": 16.8409, "longitude": 96.1735},
        ]

        destinations_data = base_destinations + city_destinations

        created, updated = 0, 0
        for data in destinations_data:
            obj, is_created = Destination.objects.update_or_create(
                name=data["name"],
                defaults=data,
            )
            created += int(is_created)
            updated += int(not is_created)
        self.stdout.write(self.style.SUCCESS(f"Destinations upserted — created: {created}, updated: {updated}"))
    
    def populate_attractions(self):
        """Seed key attractions for major destinations"""
        self.stdout.write('Populating attractions...')

        default_open = time(9, 0)
        default_close = time(18, 0)

        # Comprehensive attraction dataset keyed by destination name.
        # NOTE: Fill in precise latitude/longitude where available; when None, we fall back to the destination's coords.
        attractions = {
            "Amarapura": [
                {"name": "U Bein Bridge", "type": "Bridge", "description": "Iconic teak footbridge across Taungthaman Lake", "latitude": 21.892850479981668, "longitude": 96.05324019615111},#21.892850479981668, 96.05324019615111
                {"name": "Maha Gandhayon Monastery", "type": "Monastery", "description": "Renowned monastic college with daily alms", "latitude": 21.89662335889162, "longitude": 96.0505524807544},#21.89662335889162, 96.0505524807544
                {"name": "Bagaya Monastery", "type": "Monastery", "description": "Historic teakwood monastery", "latitude": 21.919104033230834, "longitude": 96.05857409245507},#21.919104033230834, 96.05857409245507
                {"name": "Taungthaman Lake", "type": "Lake", "description": "Scenic lake famous for U Bein Bridge sunsets", "latitude": 21.89760295811356, "longitude": 96.05535483644684},#21.89760295811356, 96.05535483644684
                {"name": "Kyauktawgyi Pagoda", "type": "Pagoda", "description": "Pagoda with a large Buddha image near Taungthaman", "latitude": 21.894163533525564, "longitude": 96.06471107572035},#21.894163533525564, 96.06471107572035
            ],
            "Bagan": [
                {"name": "Ananda Temple", "type": "Temple", "description": "One of Bagan's finest temples", "latitude": 21.170809, "longitude": 94.867595},
                {"name": "Shwezigon Pagoda", "type": "Pagoda", "description": "Early prototype of Burmese stupas", "latitude": 21.195300, "longitude": 94.893700},
                {"name": "Dhammayangyi Temple", "type": "Temple", "description": "Largest temple in Bagan", "latitude": 21.160600, "longitude": 94.859100},
                {"name": "Sulamani Temple", "type": "Temple", "description": "Red-brick masterpiece with murals", "latitude": 21.164944, "longitude": 94.881423},
                {"name": "Thatbyinnyu Temple", "type": "Temple", "description": "Tallest temple in Bagan", "latitude": 21.168787, "longitude": 94.862698},
                {"name": "Htilominlo Temple", "type": "Temple", "description": "Late Bagan style with fine stucco", "latitude": 21.178587, "longitude": 94.879050},
                {"name": "Hot Air Balloon Ride", "type": "Activity", "description": "Sunrise balloon flight over temples", "latitude": 21.190847, "longitude": 94.899209},
                {"name": "Gawdawpalin Temple", "type": "Temple", "description": "One of the tallest and most imposing temples", "latitude": 21.170020, "longitude": 94.856520},
                {"name": "Bupaya Pagoda", "type": "Pagoda", "description": "Gourd-shaped pagoda on the riverbank", "latitude": 21.176353, "longitude": 94.857856},
                {"name": "Mahabodhi Temple", "type": "Temple", "description": "A unique replica of the temple in Bodh Gaya, India", "latitude": 21.171800, "longitude": 94.858700},
                {"name": "Mingalazedi Pagoda", "type": "Pagoda", "description": "One of the last great stupas built in the Bagan era", "latitude": 16.779400, "longitude": 96.143300},
                {"name": "Shwesandaw Pagoda", "type": "Pagoda", "description": "Famous for its sunrise and sunset views", "latitude": 21.163700, "longitude": 94.866500},
                {"name": "Lawkananda Pagoda", "type": "Pagoda", "description": "Built by King Anawrahta on the riverside", "latitude": 21.127222, "longitude": 94.850556},
                {"name": "Gubyaukgyi Temple (Myinkaba)", "type": "Temple", "description": "Notable for its well-preserved 12th-century murals", "latitude": 21.157222, "longitude": 94.860833},
                {"name": "Manuha Temple", "type": "Temple", "description": "Built by the captive Mon King Manuha", "latitude": 21.150000, "longitude": 94.860000},
                {"name": "Nanpaya Temple", "type": "Temple", "description": "Sandstone-faced temple with intricate carvings", "latitude": 21.150278, "longitude": 94.860556},
                {"name": "Alodawpyi Pagoda", "type": "Pagoda", "description": "Highly venerated pagoda known for wish-fulfillment", "latitude": 21.176944, "longitude": 94.882500},
                {"name": "Bagan Archaeological Museum", "type": "Museum", "description": "Houses artifacts and the Myazedi inscription", "latitude": 21.167778, "longitude": 94.856111},
                {"name": "Tharabar Gate", "type": "Historical Site", "description": "The only surviving gate of the ancient city wall", "latitude": 21.171300, "longitude": 94.862200},
                {"name": "Bagan Golden Palace", "type": "Historical Site", "description": "Reconstruction of the 11th-century royal palace", "latitude": 21.170600, "longitude": 94.862500}
            ],
            "Bago": [
                {"name": "Shwemawdaw Pagoda", "type": "Pagoda", "description": "Tallest pagoda in Myanmar at 114 meters", "latitude": 17.336934, "longitude": 96.496664},
                {"name": "Shwethalyaung Buddha", "type": "Reclining Buddha", "description": "Historic reclining Buddha image built in 994 AD", "latitude": 17.337946, "longitude": 96.462512},
                {"name": "Kyaik Pun Pagoda", "type": "Pagoda", "description": "Four 27m-high seated Buddha statues facing four directions", "latitude": 17.304179, "longitude": 96.458913},
                {"name": "Kanbawzathadi Palace", "type": "Palace", "description": "Reconstructed 16th-century palace of King Bayinnaung", "latitude": 17.330253, "longitude": 96.492830},
                {"name": "Mahazedi Pagoda", "type": "Pagoda", "description": "Pyramidal stupa built to enshrine a Buddha tooth relic", "latitude": 17.339151, "longitude": 96.454236},
                {"name": "Hintha Gon Pagoda", "type": "Pagoda", "description": "Hilltop shrine marking the legendary founding spot of Bago", "latitude": 17.336800, "longitude": 96.505000},
                {"name": "Snake Monastery (Yat Kan Sin)", "type": "Monastery", "description": "Home to a giant, century-old Burmese Python believed to be a reborn abbot", "latitude": 17.320144, "longitude": 96.485678},
                {"name": "Maha Kalyani Sima", "type": "Ordination Hall", "description": "Historic sacred hall built by King Dhammazedi in 1476", "latitude": 17.334511, "longitude": 96.468922},
                {"name": "Shwegugale Paya", "type": "Pagoda", "description": "Unique cylindrical pagoda containing 64 seated Buddha figures", "latitude": 17.341255, "longitude": 96.451234},
                {"name": "Mya Tha Lyaung Reclining Buddha", "type": "Reclining Buddha", "description": "A massive, modern outdoor reclining Buddha located near Shwethalyaung", "latitude": 17.335622, "longitude": 96.458741},
                {"name": "Kyaik-Khat-Wai Monastery", "type": "Monastery", "description": "One of the largest teaching monasteries in Myanmar", "latitude": 17.318911, "longitude": 96.482345},
                {"name": "Bago Myoma Market", "type": "Market", "description": "The bustling central commercial hub of the city", "latitude": 17.332455, "longitude": 96.484567}
            ],
            "Bogale": [
                {"name": "Meinmahla Kyun Wildlife Sanctuary", "type": "Sanctuary", "description": "Mangrove-rich delta sanctuary", "latitude": 15.966890021384604, "longitude": 95.2969940757116},#15.966890021384604, 95.2969940757116
                {"name": "Ga Do Ga Ni Village", "type": "Village", "description": "Delta village experience", "latitude": 16.280838686268943, "longitude": 95.41781240974808},#16.280838686268943, 95.41781240974808
                {"name": "Bogale Bridge", "type": "Bridge", "description": "River crossings with delta views", "latitude": 16.278498841647522, "longitude": 95.38862320310334},#16.278498841647522, 95.38862320310334
                {"name": "Natchaung Bridge", "type": "Bridge", "description": "River crossings with delta views", "latitude": 16.285811333524595, "longitude": 95.41061933604254},#16.285811333524595, 95.41061933604254
            ],
            "Dawei": [
                {"name": "Maungmagan Beach", "type": "Beach", "description": "Popular Dawei beach", "latitude": 14.131600986301079, "longitude": 98.09635946714813},#14.131600986301079, 98.09635946714813
                {"name": "Shin Zalun Pagoda", "type": "Pagoda", "description": "Clifftop seaside pagoda", "latitude": 14.176139274855847, "longitude": 98.16854476567606},#14.176139274855847, 98.16854476567606
                {"name": "Grandfather Beach", "type": "Beach", "description": "Long, quiet beach south of Dawei", "latitude": 13.650520337691907, "longitude": 98.15074093726015},#13.650520337691907, 98.15074093726015
                {"name": "Shwe Taung Zar Pagoda", "type": "Pagoda", "description": "Pagoda on a rocky islet", "latitude": 14.079465611538795, "longitude": 98.1960402213607},#14.079465611538795, 98.1960402213607
                {"name": "Standing Buddha", "type": "Pagoda", "description": "Local hilltop pagoda", "latitude": 14.069159775300214, "longitude": 98.19159969411393},#14.069159775300214, 98.19159969411393
                {"name": "Mayin Gyi Beach", "type": "Beach", "description": "Northern stretch of Dawei peninsula", "latitude": 14.293290623723385, "longitude": 97.99774343049558},#14.293290623723385, 97.99774343049558
                {"name": "Pa Nyit Beach", "type": "Beach", "description": "Secluded beach", "latitude": 14.000592176301208, "longitude": 98.06069529598135},#14.000592176301208, 98.06069529598135
                {"name": "Tizit Beach", "type": "Beach", "description": "Palm-lined quiet beach", "latitude": 13.909766758063089, "longitude": 98.08085976714435},#13.909766758063089, 98.08085976714435
                {"name": "Tizit Waterfall", "type": "Pagoda", "description": "Local waterfall spot", "latitude": 13.913232804812601, "longitude": 98.10414611904432},#13.913232804812601, 98.10414611904432
                {"name": "Sandawshin Pagoda Tavoy", "type": "Pagoda", "description": "Pagoda near Dawei", "latitude": 19.87174048191213, "longitude": 93.01200959029171},#19.87174048191213, 93.01200959029171
            ],
            "Hakha": [
                {"name": "Mount Victoria (Nat Ma Taung)", "type": "Mountain", "description": "Highest peak in Chin Hills", "latitude": 21.23324213263783, "longitude": 93.90289236319705},#21.23324213263783, 93.90289236319705
                {"name": "Chin State Cultural Museum", "type": "Museum", "description": "Artifacts of Chin cultures", "latitude": 22.64520425138319, "longitude": 93.59455066002931},#22.64520425138319, 93.59455066002931
                {"name": "Rih Dil (Rik Lake)", "type": "Lake", "description": "Heart-shaped border lake", "latitude": 23.340389058836212, "longitude": 93.3853608496089},#23.340389058836212, 93.3853608496089
                {"name": "Mount Zion (Zion Tlang)", "type": "Viewpoint", "description": "Panoramic hill viewpoint", "latitude": 22.688656011368504, "longitude": 93.43413973049225},#22.688656011368504, 93.43413973049225
                {"name": "Bungtla Waterfall", "type": "Waterfall", "description": "Tall Chin Hills waterfall", "latitude": 22.445289622809884, "longitude": 92.9875702376935},#22.445289622809884, 92.9875702376935
            ],
            "Heho": [
                {"name": "Lay Thar Taung Pagoda", "type": "Pagoda", "description": "Hilltop pagoda near Heho", "latitude": 20.727927464063555, "longitude": 96.83049434891903},#20.727927464063555, 96.83049434891903
                {"name": "Inle Lake", "type": "Lake", "description": "Highland lake with floating villages", "latitude": 20.5550, "longitude": 96.9150},
                {"name": "Pindaya Caves", "type": "Cave", "description": "Limestone caves filled with Buddha images", "latitude": 20.925467740412643, "longitude": 96.65022625968813},#20.925467740412643, 96.65022625968813
            ],
            "Hinthada": [
                {"name": "Pyi Lone Chan Thar Pagoda", "type": "Pagoda", "description": "Hilltop pagoda overlooking town", "latitude": 17.638696580413487, "longitude": 95.45598400777024},#17.638696580413487, 95.45598400777024
                {"name": "Kyauk Taw Gyi Monastery", "type": "Monastery", "description": "Local monastery landmark", "latitude": 17.64322918025369, "longitude": 95.46056341578117},#17.64322918025369, 95.46056341578117
                {"name": "Hinthada Kayin Baptist Church", "type": "Religious Site", "description": "Notable local church", "latitude": 17.63207259347785, "longitude": 95.4554885016494},#17.63207259347785, 95.4554885016494
            ],
            "Hmawbi": [
                {"name": "Hlawga National Park", "type": "Park", "description": "Wildlife park and safari drive", "latitude": 17.046324366307044, "longitude": 96.0989503808019},#17.046324366307044, 96.0989503808019
                {"name": "Allied War Cemetery (Hmawbi)", "type": "Cemetery", "description": "WWII war cemetery", "latitude": 17.03574158411243, "longitude": 96.13220705127445},#17.03574158411243, 96.13220705127445
                {"name": "Hmawbi Market", "type": "Market", "description": "Local market", "latitude": 17.100551409890176, "longitude": 96.0428968820525},#17.100551409890176, 96.0428968820525
            ],
            "Hpa-An": [
                {"name": "Mount Zwegabin", "type": "Mountain", "description": "Karst peak with monastery", "latitude": 16.823610, "longitude": 97.669999},
                {"name": "Saddan Cave", "type": "Cave", "description": "Large cave with lake exit", "latitude": 16.743613, "longitude": 97.714716},
                {"name": "Kawgun Cave", "type": "Cave", "description": "Ancient rock reliefs", "latitude": 16.822956, "longitude": 97.585845},
                {"name": "Kyauk Kalap Pagoda", "type": "Pagoda", "description": "Pagoda on a limestone spire", "latitude": 16.818166, "longitude": 97.640441},
                {"name": "Bat Cave", "type": "Cave", "description": "Cave with evening bat exodus", "latitude": 16.848936, "longitude": 97.610722},
                {"name": "Shwe Yin Myaw Pagoda", "type": "Pagoda", "description": "Famous sunset point on Thanlwin riverbank", "latitude": 16.894431, "longitude": 97.631168},
                {"name": "Lumbini Garden", "type": "Park", "description": "Field of 1,000 identical Buddha statues at the base of Mt. Zwegabin", "latitude": 16.808390, "longitude": 97.673150},
                {"name": "Yathaypyan Cave", "type": "Cave", "description": "Cave with high-altitude views and ancient pagodas", "latitude": 16.831245, "longitude": 97.584321},
                {"name": "Kaw Ka Thaung Cave", "type": "Cave", "description": "Cave featuring a natural swimming pool and 145 monk statues", "latitude": 16.819455, "longitude": 97.712344},
                {"name": "Kan Thar Yar Lake", "type": "Lake", "description": "Scenic urban lake with a wooden bridge in the city center", "latitude": 16.879875, "longitude": 97.634385},
                {"name": "Bayin Nyi Cave", "type": "Cave", "description": "Monastery cave known for its natural hot springs", "latitude": 16.970523, "longitude": 97.493414},
                {"name": "Taung Wine Mountain", "type": "Mountain", "description": "Popular sunrise hiking spot with steep stairs", "latitude": 16.865432, "longitude": 97.678911},
                {"name": "Kayin State Cultural Museum", "type": "Museum", "description": "Showcases the history and traditional dress of the Kayin people", "latitude": 16.885622, "longitude": 97.635432},
                {"name": "Hpa-An Night Market", "type": "Market", "description": "Riverside hub for local Kayin street food", "latitude": 16.892344, "longitude": 97.632145},
                {"name": "Ruby Lake (Linno Cave)", "type": "Nature", "description": "Clear blue natural pool popular for local swimming", "latitude": 16.820122, "longitude": 97.715678},
                {"name": "Mawkhel Cave", "type": "Cave", "description": "Off-the-beaten-path cave with impressive stalactites", "latitude": 16.791244, "longitude": 97.698712},
                {"name": "Thanlwin Bridge (Hpa-An)", "type": "Bridge", "description": "Major bridge crossing the Salween River with scenic views", "latitude": 16.852344, "longitude": 97.601233},
                {"name": "Phar-Pu Mountain", "type": "Mountain", "description": "Located across the river, famous for quick evening hikes", "latitude": 16.898711, "longitude": 97.615432},
                {"name": "Kha Yon Cave", "type": "Cave", "description": "Roadside cave featuring ancient Buddha footprints", "latitude": 16.654321, "longitude": 97.689012},
                {"name": "Hpa-An Clock Tower", "type": "Landmark", "description": "The central landmark of Hpa-An town", "latitude": 16.888911, "longitude": 97.636789}
            ],
            "Hsipaw": [
                {"name": "Shan Palace (Hsipaw Palace)", "type": "Heritage", "description": "Residence of last Sawbwa", "latitude": 22.626510550452295, "longitude": 97.30529469066254},#22.626510550452295, 97.30529469066254
                {"name": "Little Bagan (Myauk Myo)", "type": "Ruins", "description": "Cluster of old stupas", "latitude": 22.631508625893428, "longitude": 97.29537186752238},#22.631508625893428, 97.29537186752238
                {"name": "Bawgyo Pagoda", "type": "Pagoda", "description": "Revered Shan-style pagoda", "latitude": 22.583860578315047, "longitude": 97.23376396984553},#22.583860578315047, 97.23376396984553
                {"name": "Madahya Monastery (Bamboo Buddha Monastery)", "type": "Monastery", "description": "Monastery with bamboo Buddha", "latitude": 22.630869632617227, "longitude": 97.29773554697857},#22.630869632617227, 97.29773554697857
                {"name": "Hsipaw Nam Doke Waterfall", "type": "Waterfall", "description": "Local waterfall", "latitude": 22.627457734101178, "longitude": 97.25710206945908},#22.627457734101178, 97.25710206945908
                {"name": "Hsipaw Hot Springs", "type": "Hot Spring", "description": "Natural hot springs", "latitude": 22.636739795608108, "longitude": 97.27134574516697},#22.636739795608108, 97.27134574516697
            ],
            "Kalaw": [
                {"name": "FairyLand Kalaw", "type": "Viewpoint", "description": "Scenic spot near Kalaw", "latitude": 20.609752098333857, "longitude": 96.5957123146982},#20.609752098333857, 96.5957123146982
                {"name": "Green Hill Valley Elephant Camp", "type": "Sanctuary", "description": "Elephant-friendly camp", "latitude": 20.731212066135377, "longitude": 96.49880292368098},#20.731212066135377, 96.49880292368098
                {"name": "Hnee Pagoda", "type": "Pagoda", "description": "Small pagoda with bamboo Buddha", "latitude": 20.62274301670928, "longitude": 96.5472502181889},#20.62274301670928, 96.5472502181889
                {"name": "Kalaw City View", "type": "Viewpoint", "description": "Town overlook", "latitude": 20.644399794841927, "longitude": 96.56291395800869},#20.644399794841927, 96.56291395800869
                {"name": "Kalaw Clock Tower", "type": "Landmark", "description": "Central town clock", "latitude": 20.629403938877996, "longitude": 96.56633561309806},#20.629403938877996, 96.56633561309806
                {"name": "Kalaw Myoma Market", "type": "Market", "description": "Main local market", "latitude": 20.635514477317187, "longitude": 96.56702646539844},#20.635514477317187, 96.56702646539844
                {"name": "Kalaw Railway Station", "type": "Railway", "description": "Colonial-era station", "latitude": 20.628984716977573, "longitude": 96.56875458893484},#20.628984716977573, 96.56875458893484
                {"name": "Shwe Oo Min Pagoda", "type": "Cave", "description": "Natural cave pagoda", "latitude": 20.63687445372626, "longitude": 96.49263223663174},#20.63687445372626, 96.49263223663174
                {"name": "Thein Taung Pagoda Monastery", "type": "Monastery", "description": "Hilltop monastery", "latitude": 20.63850061587042, "longitude": 96.5668575349358},#20.63850061587042, 96.5668575349358
                {"name": "Byite Mountain", "type": "Mountain", "description": "Local mountain trek", "latitude": 20.625455604369197, "longitude": 96.6084444544527},#20.625455604369197, 96.6084444544527
                { "name": "Christ the King Church", "type": "Architecture", "description": "Historical colonial-era church with Italian architectural influence", "latitude": 20.625569, "longitude": 96.565908 }, 
                { "name": "Myin Mahti Cave", "type": "Cave", "description": "Natural cave system housing hundreds of ancient Buddha statues", "latitude": 20.598214, "longitude": 96.581234 }, 
                { "name": "Kalaw Heritage Hotel", "type": "Landmark", "description": "Historic hotel established in 1903 during the British colonial era", "latitude": 20.621234, "longitude": 96.571456 }, 
                { "name": "Pinmagon Monastery", "type": "Monastery", "description": "Traditional monastery known for housing the original Bamboo Buddha", "latitude": 20.612455, "longitude": 96.549822 }, 
                { "name": "View Point Golf Club", "type": "Sport", "description": "High-altitude golf course with panoramic mountain views", "latitude": 20.640122, "longitude": 96.550344 }, 
                { "name": "Mingalar Lake", "type": "Nature", "description": "Peaceful lake on the outskirts of town, popular for morning walks", "latitude": 20.621890, "longitude": 96.558712 }, 
                { "name": "Kalaw Public Park", "type": "Park", "description": "Central town park featuring gardens and a local fountain", "latitude": 20.632144, "longitude": 96.565011 }
            ],
            "Kalay": [
                {"name": "Zi Chaung Dam", "type": "Dam", "description": "Reservoir and viewpoint", "latitude": 23.17744968469813, "longitude": 93.93515469435451},#23.17744968469813, 93.93515469435451
                {"name": "Tahan Market", "type": "Market", "description": "Bustling local market", "latitude": 23.199303713563676, "longitude": 94.01672042659216},#23.199303713563676, 94.01672042659216
                {"name": "Taungphila Hill", "type": "Hill", "description": "Scenic hill viewpoint", "latitude": 23.188738841429565, "longitude": 94.00002382635166},#23.188738841429565, 94.00002382635166
                {"name": "Shwe Bon Tha Pagoda", "type": "Pagoda", "description": "Prominent pagoda in Kalay", "latitude": 23.185718786292426, "longitude": 94.07035749701559},#23.185718786292426, 94.07035749701559
                {"name": "Dhat Taung Pagoda", "type": "Pagoda", "description": "Local pagoda", "latitude": 23.194146215537224, "longitude": 94.02344445932953},#23.194146215537224, 94.02344445932953
                {"name": "Shwe Ou Daung Pagoda", "type": "Pagoda", "description": "River confluence and creek", "latitude": 23.168547906117258, "longitude": 94.04966405705255},#23.168547906117258, 94.04966405705255
                {"name": "Kim Ngo Lake", "type": "Lake", "description": "Water reservoir", "latitude": 23.20566479950043, "longitude": 93.97940641999291},#23.20566479950043, 93.97940641999291
                {"name": "Kyar Inn Lake", "type": "Lake", "description": "Local landmark lake", "latitude": 23.068142944430623, "longitude": 94.01243830325078},#23.068142944430623, 94.01243830325078
            ],
            "Kawthaung": [
                {"name": "Nyaung Oo Phee Island", "type": "Island", "description": "Island with clear waters and reefs", "latitude": 10.072008627113984, "longitude": 97.98581593190634},#10.072008627113984, 97.98581593190634
                {"name": "Cockburn Island (Kanae Island)", "type": "Island", "description": "Island with snorkeling spots", "latitude": 10.199144076313338, "longitude": 97.97269546066158},#10.199144076313338, 97.97269546066158
                {"name": "9-Mile Beach", "type": "Beach", "description": "Local beach", "latitude": 10.06473198635231, "longitude": 98.52211529068757},#10.06473198635231, 98.52211529068757
                {"name": "Zedetkyi Kyun Island", "type": "Island", "description": "Island in Myeik Archipelago", "latitude": 9.966149309534462, "longitude": 98.18780302096893},#9.966149309534462, 98.18780302096893
                {"name": "Maliwun Waterfall", "type": "Waterfall", "description": "Popular waterfall near Kawthaung", "latitude": 10.261636581097013, "longitude": 98.59771801077174},#10.261636581097013, 98.59771801077174
                {"name": "Third Mile Pagoda (Pyi Daw Aye Pagoda)", "type": "Pagoda", "description": "Pagoda along main road", "latitude": 9.982525880849046, "longitude": 98.55327375069557},#9.982525880849046, 98.55327375069557
            ],
            "Labutta": [
                {"name": "Myoma Market", "type": "Market", "description": "Scenic island and beach", "latitude": 16.14557680454075, "longitude": 94.7584648093801},#16.526856329361184, 94.24093843875438
                {"name": "Sagin Bridge", "type": "Bridge", "description": "Mangrove sanctuary access point", "latitude": 16.13657022707831, "longitude": 94.74754720038149},#16.13657022707831, 94.74754720038149
                {"name": "Ywe River", "type": "River", "description": "River scenery", "latitude": 16.143061695823732, "longitude": 94.7678732121662},#16.143061695823732, 94.7678732121662
            ],
            "Letpadan": [
                {"name": "Law Ka Nandar Pagoda", "type": "Pagoda", "description": "Local pagoda", "latitude": 17.776058327416067, "longitude": 95.74751042401124},#17.776058327416067, 95.74751042401124
                {"name": "Letpadan Public Park", "type": "Park", "description": "Town park", "latitude": 17.78707471642762, "longitude": 95.75610167600304},#17.78707471642762, 95.75610167600304
            ],
            "Loikaw": [
                {"name": "Naungyar Lake", "type": "Lake", "description": "A famous lake in Loikaw", "latitude": 19.678462053292773, "longitude": 97.2065654359972},#19.678462053292773, 97.2065654359972
                {"name": "Kayah State Cultural Museum", "type": "Museum", "description": "Ethnic Kayah artifacts", "latitude": 19.692647861316043, "longitude": 97.20879310916865},#19.692647861316043, 97.20879310916865
                {"name": "Pan Pat Villages", "type": "Village", "description": "Padaung communities and weaving", "latitude": 19.605063512243824, "longitude": 96.98349640675994},#19.605063512243824, 96.98349640675994
                {"name": "Ngwe Taung Dam", "type": "Dam", "description": "Reservoir and picnic spot", "latitude": 19.546818143701692, "longitude": 97.16981280337923},#19.546818143701692, 97.16981280337923
                {"name": "Pilu River", "type": "River", "description": "Local river scenery", "latitude": 19.607241088050788, "longitude": 97.34666997379112},#19.607241088050788, 97.34666997379112
            ],
            "Magway": [
                {"name": "Myathalun Pagoda", "type": "Pagoda", "description": "Hilltop pagoda over Irrawaddy", "latitude": 20.169873, "longitude": 94.917442},
                {"name": "Yokesone Monastery", "type": "Monastery", "description": "Historic teak monastery", "latitude": 20.833394, "longitude": 94.745104},
                {"name": "Fort Min Hla", "type": "Fort", "description": "19th-century river fort", "latitude": 17.979095, "longitude": 95.706292},
                {"name": "Salay House", "type": "Heritage", "description": "Colonial-era riverside house", "latitude": 20.835118, "longitude": 94.740215},
                {"name": "Tantkyi Taung Pagoda", "type": "Pagoda", "description": "Hilltop pagoda across from Bagan", "latitude": 21.155207, "longitude": 94.787727},
                {"name": "Mann Shwe Settaw Pagoda", "type": "Pagoda", "description": "Famous pagoda featuring the upper and lower Buddha footprints", "latitude": 20.100350, "longitude": 94.527161},
                {"name": "Nagarpwat Taung (Mud Volcano)", "type": "Nature", "description": "Unique cold-mud volcanoes known as the Dragon Breath hills", "latitude": 20.174925, "longitude": 94.882012},
                {"name": "Beikthano Ancient City", "type": "UNESCO Site", "description": "Ruins of an ancient Pyu city dating back over 2,000 years", "latitude": 20.003889, "longitude": 95.381389},
                {"name": "Magway Bridge (Ayeyarwady Bridge)", "type": "Bridge", "description": "Major landmark bridge connecting Magway and Minbu", "latitude": 20.146731, "longitude": 94.894048},
                {"name": "Shin Pin Maha Laba Man Temple", "type": "Temple", "description": "Venerated temple located in the historic town of Salay", "latitude": 20.838200, "longitude": 94.735400},
                {"name": "Minbu Market", "type": "Market", "description": "Bustling local trade hub across the river from Magway city", "latitude": 20.174167, "longitude": 94.877222},
                {"name": "Fort Kway Chaung", "type": "Fort", "description": "Opposite bank counterpart to Min Hla Fort built for defense", "latitude": 19.389100, "longitude": 95.123400},
                {"name": "Thihoshin Pagoda", "type": "Pagoda", "description": "Historic pagoda in Pakokku known for its ancient Buddha image", "latitude": 21.332500, "longitude": 95.081100}
            ],
            "Mandalay": [
                {"name": "Mandalay Palace", "type": "Historical Site", "description": "Last royal palace of Myanmar", "latitude": 21.9886, "longitude": 96.0931},
                {"name": "Mandalay Hill", "type": "Natural Site", "description": "Hill with panoramic city views", "latitude": 22.0093, "longitude": 96.1010},
                {"name": "Kuthodaw Pagoda", "type": "Pagoda", "description": "World's largest book with stone slabs", "latitude": 22.0049, "longitude": 96.1120},
                {"name": "Mahamuni Buddha Temple", "type": "Temple", "description": "Highly venerated Mahamuni image", "latitude": 21.948162, "longitude": 96.082330},
                {"name": "Shwenandaw Monastery", "type": "Monastery", "description": "Teak monastery with carvings", "latitude": 22.000731, "longitude": 96.113769},
                {"name": "Zegyo Market", "type": "Market", "description": "Central market of Mandalay", "latitude": 21.982654, "longitude": 96.076298},
                {"name": "U Bein Bridge", "type": "Bridge", "description": "Teak bridge in Amarapura", "latitude": 21.8946, "longitude": 96.0515},
                {"name": "Mingun Pahtodawgyi", "type": "Historical Site", "description": "Massive unfinished pagoda ruins", "latitude": 22.052061, "longitude": 96.018611},
                {"name": "Hsinbyume Pagoda", "type": "Pagoda", "description": "Beautiful white wavy-terraced pagoda", "latitude": 22.053819, "longitude": 96.020474},
                {"name": "Kyauktawgyi Pagoda", "type": "Pagoda", "description": "Features a large Buddha carved from a single marble block", "latitude": 22.000624, "longitude": 96.106456},
                {"name": "Sandamuni Pagoda", "type": "Pagoda", "description": "Known for its many white stupas and iron Buddha", "latitude": 22.003421, "longitude": 96.109678},
                {"name": "Atumashi Monastery", "type": "Monastery", "description": "The Incomparable Monastery rebuilt in 1996", "latitude": 21.999653, "longitude": 96.111812},
                {"name": "Jade Market (Kyauk-sein)", "type": "Market", "description": "Global hub for jade trading and cutting", "latitude": 21.936655, "longitude": 96.075482},
                {"name": "Mandalay Marionettes Theater", "type": "Cultural", "description": "Traditional Myanmar puppet performance venue", "latitude": 21.991584, "longitude": 96.106842},
                {"name": "Su Taung Pyae Pagoda", "type": "Pagoda", "description": "The sparkling temple at the summit of Mandalay Hill", "latitude": 22.012541, "longitude": 96.105432}
            ],
            "Mawlamyine": [
                {"name": "Kyaikthanlan Pagoda", "type": "Pagoda", "description": "Hilltop pagoda with views", "latitude": 16.489513908086884, "longitude": 97.62865206928993},#16.489513908086884, 97.62865206928993
                {"name": "Win Sein Taw Ya", "type": "Reclining Buddha", "description": "Giant reclining Buddha", "latitude": 16.32363434470242, "longitude": 97.72497420471004},#16.32363434470242, 97.72497420471004
                {"name": "Santawshin Pagoda", "type": "Pagoda", "description": "Local pagoda", "latitude": 17.375628844764115, "longitude": 97.24043419771137},#17.375628844764115, 97.24043419771137
                {"name": "The Death Railway Museum", "type": "Museum", "description": "WWII history exhibit", "latitude": 15.955776745641737, "longitude": 97.72956548990427},#15.955776745641737, 97.72956548990427
                {"name": "Nwa La Bo Pagoda", "type": "Pagoda", "description": "Precariously balanced boulders pagoda", "latitude": 15.945486364750566, "longitude": 97.73341342491828},#15.945486364750566, 97.73341342491828
            ],
            "Meiktila": [
                {"name": "Meiktila Lake", "type": "Lake", "description": "Central lake with parks", "latitude": 20.889774756595635, "longitude": 95.85381777805523},#20.889774756595635, 95.85381777805523
                {"name": "Phaung Daw Oo Pagoda", "type": "Pagoda", "description": "Pagoda near the lake", "latitude": 20.877669315679206, "longitude": 95.85670078353789},#20.877669315679206, 95.85670078353789
                {"name": "General Aung San Park", "type": "Park", "description": "Lakeside park", "latitude": 20.877633751418873, "longitude": 95.85207679905452},#20.877633751418873, 95.85207679905452
                {"name": "Shwe Myin Tin Pagoda", "type": "Pagoda", "description": "Hilltop pagoda", "latitude": 20.872064288938144, "longitude": 95.86817769066361},#20.872064288938144, 95.86817769066361
                {"name": "Nagayon Pagoda", "type": "Pagoda", "description": "Serpent-hood Buddha pagoda", "latitude": 20.87816425674244, "longitude": 95.85234072375964},#20.87816425674244, 95.85234072375964
                {"name": "Dhamma Thukha Shwezigon Pagoda", "type": "Pagoda", "description": "Local pagoda", "latitude": 20.880692468845375, "longitude": 95.85674166825527},#20.880692468845375, 95.85674166825527
            ],
            "Monywa": [
                {"name": "Thanboddhay Pagoda", "type": "Pagoda", "description": "Pagoda with thousands of Buddha images", "latitude": 22.1167, "longitude": 95.1333},
                {"name": "Mahar Bodhi Ta Htaung", "type": "Religious Site", "description": "Standing Buddha and reclining Buddha park", "latitude": 22.08040318851829, "longitude": 95.28938090298868},#22.08040318851829, 95.28938090298868
                {"name": "Pho Win Taung", "type": "Cave", "description": "Sandstone cave complex with murals", "latitude": 22.04773053329477, "longitude": 94.98402480016958},#22.04773053329477, 94.98402480016958
            ],
            "Myaungmya": [
                {"name": "Buu Paya", "type": "Pagoda", "description": "Downtown pagoda", "latitude": 16.527051174984535, "longitude": 94.81821625828508},#16.527051174984535, 94.81821625828508
                {"name": "Kabalone Pagoda", "type": "Pagoda", "description": "City pagoda", "latitude": 22.163718742440356, "longitude": 95.2551695051036},#22.163718742440356, 95.2551695051036
                {"name": "Shwe Thalyaung Pagoda", "type": "Pagoda", "description": "Reclining Buddha pagoda", "latitude": 16.597816970885717, "longitude": 94.84763035849345},#16.597816970885717, 94.84763035849345
                {"name": "Tawatain Tha Pagoda", "type": "Pagoda", "description": "Local landmark", "latitude": 16.57042927604051, "longitude": 94.89974899273304},#16.57042927604051, 94.89974899273304
                {"name": "Shwe Boddhaw Pagoda", "type": "Pagoda", "description": "Pagoda near town", "latitude": 16.505580895929974, "longitude": 94.83374026567334},#16.505580895929974, 94.83374026567334
                {"name": "Mya Kan Thar Park", "type": "Park", "description": "City park with gardens", "latitude": 16.589701110348848, "longitude": 94.9130181545222},#16.589701110348848, 94.9130181545222
                {"name": "Bo Gyoke Aung San Park", "type": "Park", "description": "Park dedicated to Bogyoke Aung San", "latitude": 16.583773078152852, "longitude": 94.89042609035081},#16.583773078152852, 94.89042609035081
                #{"name": "Dee Dote U Ba Cho Park", "type": "Park", "description": "Recreational park", "latitude": None, "longitude": None},
            ],
            "Myeik": [
                {"name": "Thein Daw Gyi Pagoda", "type": "Pagoda", "description": "Downtown hill pagoda", "latitude": 12.440002010883335, "longitude": 98.59746569780476},#12.440002010883335, 98.59746569780476
                {"name": "Harris Island", "type": "Island", "description": "Coral and snorkeling spot", "latitude": 12.641089458758444, "longitude": 98.21666091435402},#12.641089458758444, 98.21666091435402
                {"name": "Frost Island", "type": "Island", "description": "White sand and coral", "latitude": 12.471351123618339, "longitude": 98.52636837985352},#12.471351123618339, 98.52636837985352
                {"name": "Phi Lar Island", "type": "Island", "description": "Uninhabited island with reefs", "latitude": 12.168776513373041, "longitude": 98.02570558369713},#12.168776513373041, 98.02570558369713
                {"name": "Lampi Island", "type": "Island", "description": "Marine national park", "latitude": 10.91009050740392, "longitude": 98.21469386698926},#10.91009050740392, 98.21469386698926
                {"name": "Nyaung Wee Island", "type": "Island", "description": "Moken villages island", "latitude": 10.539080401434962, "longitude": 98.2090070114291},#10.539080401434962, 98.2090070114291
            ],
            "Myitkyina": [
                {"name": "Myit-Sone (Irrawaddy Confluence)", "type": "Nature", "description": "Confluence of Maykha and Malikha", "latitude": 25.690390, "longitude": 97.516241},
                {"name": "Kachin National Manau Park", "type": "Park", "description": "Cultural park with manau poles", "latitude": 25.401946, "longitude": 97.405615},
                {"name": "Hsu Taung Pye Zedidaw Pagoda", "type": "Pagoda", "description": "Prominent riverside pagoda", "latitude": 25.397174, "longitude": 97.405151},
                {"name": "Kachin State Cultural Museum", "type": "Museum", "description": "Museum of Kachin heritage", "latitude": 25.392446, "longitude": 97.401963},
                {"name": "Sri Saraswati Temple", "type": "Temple", "description": "Colorful Hindu temple", "latitude": 25.381244, "longitude": 97.399822},
                {"name": "Geis Memorial Church", "type": "Church", "description": "Historic Baptist church", "latitude": 25.385567, "longitude": 97.398668},
                {"name": "Irrawaddy Riverbank", "type": "River", "description": "River views and gold panning", "latitude": 25.390863, "longitude": 97.404012},
                {"name": "Sutaungpyay Reclining Buddha", "type": "Pagoda", "description": "Large reclining Buddha near the river", "latitude": 25.397852, "longitude": 97.405891},
                {"name": "St. Columban's Cathedral", "type": "Church", "description": "Major Catholic cathedral in Myitkyina", "latitude": 25.378911, "longitude": 97.395432},
                {"name": "Myitkyina University", "type": "Education", "description": "Main higher education hub of Kachin State", "latitude": 25.419456, "longitude": 97.378912},
                {"name": "Myitkyina Railway Station", "type": "Transport", "description": "Northern terminus of the Myanmar railway", "latitude": 25.384231, "longitude": 97.391244},
                {"name": "Kachin Baptist Convention (KBC)", "type": "Church", "description": "Significant religious and social headquarters", "latitude": 25.394511, "longitude": 97.396782},
                {"name": "Myitkyina Myoma Market", "type": "Market", "description": "Bustling central market for local goods", "latitude": 25.386544, "longitude": 97.400122},
                {"name": "Balaminhtin Bridge", "type": "Bridge", "description": "Strategic bridge crossing the Irrawaddy", "latitude": 25.375622, "longitude": 97.412345},
                {"name": "Alam Bum Memorial Park", "type": "Park", "description": "Hilly memorial park with scenic views", "latitude": 25.432100, "longitude": 97.456700}
            ],
            "Naypyidaw": [
                {"name": "Uppatasanti Pagoda", "type": "Pagoda", "description": "99m replica of Shwedagon", "latitude": 19.771093, "longitude": 96.183070},
                {"name": "Gem Museum", "type": "Museum", "description": "Precious stones and jade exhibits", "latitude": 19.743829, "longitude": 96.116136},
                {"name": "Nay Pyi Taw Zoological Garden", "type": "Zoo", "description": "Large zoo with spacious enclosures", "latitude": 19.868189, "longitude": 96.260163},
                {"name": "National Landmark Garden", "type": "Park", "description": "Miniature landmarks of Myanmar", "latitude": 19.876707, "longitude": 96.270789},
                {"name": "National Herbal Park", "type": "Park", "description": "Garden of medicinal plants", "latitude": 19.751892, "longitude": 96.108969},
                {"name": "Water Fountain Garden", "type": "Park", "description": "Fountain park with night shows", "latitude": 19.749040, "longitude": 96.124160},
                {"name": "Nay Pyi Taw Safari Park", "type": "Safari", "description": "Drive-through wildlife park", "latitude": 19.871340, "longitude": 96.254852},
                {"name": "Thapyaygone Market", "type": "Market", "description": "Local market for food and goods", "latitude": 19.739018, "longitude": 96.118762},
                {"name": "Maravijaya Buddha", "type": "Pagoda", "description": "World's tallest sitting marble Buddha statue", "latitude": 19.712154, "longitude": 96.095432},
                {"name": "National Museum Naypyidaw", "type": "Museum", "description": "Modern museum showcasing Myanmar's history and art", "latitude": 19.733567, "longitude": 96.101234},
                {"name": "Hluttaw (Parliament Complex)", "type": "Government", "description": "The massive 31-building parliament complex", "latitude": 19.761234, "longitude": 96.065432},
                {"name": "Defense Services Museum", "type": "Museum", "description": "Massive military history museum with outdoor displays", "latitude": 19.902144, "longitude": 96.305678},
                {"name": "Ocean Super Center", "type": "Market", "description": "Popular modern shopping mall and supermarket", "latitude": 19.742311, "longitude": 96.121455},
                {"name": "Thatta Thattaha Maha Bawdi Pagoda", "type": "Pagoda", "description": "Replica of the Mahabodhi Temple in India", "latitude": 19.851244, "longitude": 96.256789},
                {"name": "Junction Centre Nay Pyi Taw", "type": "Market", "description": "Major shopping and cinema destination", "latitude": 19.741255, "longitude": 96.119822}
            ],
            "Nyaunglebin": [
                {"name": "Pa Ya Gyi Pagoda", "type": "Pagoda", "description": "Local revered pagoda", "latitude": 17.96010131852004, "longitude": 96.71878984550321},#17.96010131852004, 96.71878984550321
            ],
            "Pakokku": [
                {"name": "Shwe Ku Pagoda", "type": "Pagoda", "description": "Riverside pagoda", "latitude": 21.329915383299692, "longitude": 95.08537559613656}, #21.329915383299692, 95.08537559613656
                {"name": "Thi Ho Shin Pagoda", "type": "Pagoda", "description": "Important local pagoda", "latitude": 21.327029962985325, "longitude": 95.06818205750409}, #21.327029962985325, 95.06818205750409
                {"name": "Pakhangyi Archaeological Museum", "type": "Museum", "description": "Historic wooden monastery museum", "latitude": 21.539381750795886, "longitude": 95.2033003301181}, #21.539381750795886, 95.2033003301181
                {"name": "Shin-ma-taung Hill", "type": "Hill", "description": "Hill with viewpoints", "latitude": 21.57490888021464, "longitude": 95.10006189614283},#21.57490888021464, 95.10006189614283
            ],
            "Pathein": [
                {"name": "Phayarni Pagoda", "type": "Pagoda", "description": "Pagoda within Pathein", "latitude": 16.797797173749785, "longitude": 94.65647535064598},#16.797797173749785, 94.65647535064598
                {"name": "Ngwe Saung", "type": "Beach", "description": "Beach resort west of Pathein", "latitude": 16.8533, "longitude": 94.3589},
                {"name": "Shwe Sar Umbrella Workshop", "type": "Workshop", "description": "Traditional Pathein parasol making", "latitude": 16.792365738035677, "longitude": 94.7457379070002},#16.792365738035677, 94.7457379070002
                {"name": "Gaw Yin Gyi Island", "type": "Island", "description": "Scenic cliffs and beach", "latitude": 16.526896511798174, "longitude": 94.24097981467305},#16.526896511798174, 94.24097981467305
                {"name": "Chaung Thar", "type": "Beach", "description": "Popular beach near Pathein", "latitude": 16.96347923244583, "longitude": 94.44320391097601},#16.96347923244583, 94.44320391097601
            ],
            "Paungde": [
                {"name": "Myat Swetaw Buddhist Temple", "type": "Pagoda", "description": "Local revered temple", "latitude": 18.49222750657666, "longitude": 95.5076369459058},#18.49222750657666, 95.5076369459058
                {"name": "Min Lak Yar Pagoda", "type": "Pagoda", "description": "Hilltop pagoda", "latitude": 18.491754136439482, "longitude": 95.50742013504363},#18.491754136439482, 95.50742013504363
                {"name": "Nyein Chan Shwe Ti Public Park", "type": "Park", "description": "Town park", "latitude": 18.48689467266591, "longitude": 95.51013174274831},#18.48689467266591, 95.51013174274831
            ],
            "Pyay": [
                {"name": "Sri Ksetra (Tharaykhittaya) Ruins", "type": "Archaeological Site", "description": "UNESCO Pyu ancient city", "latitude": 18.805052, "longitude": 95.287427},
                {"name": "Akauk Taung", "type": "Cliff", "description": "River cliff with Buddha carvings", "latitude": 18.508424, "longitude": 95.095752},
                {"name": "Shwesandaw Paya", "type": "Pagoda", "description": "Hilltop pagoda in Pyay", "latitude": 18.818571, "longitude": 95.221000},
                {"name": "Shwe Myet Man Paya", "type": "Pagoda", "description": "Glasses-wearing Buddha in Shwedaung", "latitude": 18.703510, "longitude": 95.208466},
                {"name": "Hmawza Archaeological Museum", "type": "Museum", "description": "Artifacts from Sri Ksetra", "latitude": 18.809527, "longitude": 95.289693},
                {"name": "Sehtatgyi Buddha", "type": "Buddha Image", "description": "Large sitting Buddha", "latitude": 18.818062, "longitude": 95.222860},
                {"name": "Nawaday Bridge", "type": "Bridge", "description": "Bridge with river views", "latitude": 18.807967, "longitude": 95.210142},
                {"name": "Thone Pan Hla", "type": "Pagoda", "description": "Local religious site", "latitude": 18.786832, "longitude": 95.316357},
                {"name": "Bawbawgyi Stupa", "type": "Pagoda", "description": "Ancient 5th-century cylindrical Pyu stupa", "latitude": 18.786111, "longitude": 95.285556},
                {"name": "Payagyi Pagoda", "type": "Pagoda", "description": "One of the four ancient corner stupas of Sri Ksetra", "latitude": 18.824700, "longitude": 95.253600},
                {"name": "Bebe Pagoda", "type": "Pagoda", "description": "Unique cube-shaped ancient Pyu temple", "latitude": 18.788600, "longitude": 95.286100},
                {"name": "Shwebonthar Muni Pagoda", "type": "Pagoda", "description": "Located across the river in Padaung, highly revered", "latitude": 18.811389, "longitude": 95.196389},
                {"name": "Shwenattaung Pagoda", "type": "Pagoda", "description": "Famous 'Golden Spirit Mountain' pagoda in Shwedaung", "latitude": 18.683333, "longitude": 95.216667},
                {"name": "Phaya Mar Pagoda", "type": "Pagoda", "description": "Another of the four major ancient Pyu corner stupas", "latitude": 18.828889, "longitude": 95.226389},
                {"name": "Pyay Night Market", "type": "Market", "description": "Riverside hub for local food and evening atmosphere", "latitude": 18.823600, "longitude": 95.216500},
                {"name": "Phowintaung Cave (Pyay Branch)", "type": "Cave", "description": "Small complex of religious cave shrines", "latitude": 18.835400, "longitude": 95.241200}
            ],
            "Pyin Oo Lwin": [
                {"name": "National Kandawgyi Botanical Gardens", "type": "Garden", "description": "Heritage botanical garden", "latitude": 21.994038, "longitude": 96.469452},
                {"name": "Anisakan Falls (Dattawgyaik)", "type": "Waterfall", "description": "Tall waterfall in a gorge", "latitude": 21.980539, "longitude": 96.386958},
                {"name": "Peik Chin Myaung Cave", "type": "Cave", "description": "Limestone cave with Buddha images", "latitude": 22.096020, "longitude": 96.620231},
                {"name": "Pwe Kauk Waterfalls", "type": "Waterfall", "description": "Cascade picnic spot", "latitude": 22.064959, "longitude": 96.533912},
                {"name": "Purcell Tower", "type": "Clock Tower", "description": "Colonial clock tower landmark", "latitude": 22.026717, "longitude": 96.464074},
                {"name": "Maha Ant Htoo Kan Thar Pagoda", "type": "Pagoda", "description": "Hilltop pagoda", "latitude": 22.082801, "longitude": 96.521163},
                {"name": "Chan Tak Buddhist Temple", "type": "Temple", "description": "Chinese Buddhist temple", "latitude": 22.021704, "longitude": 96.478250},
                {"name": "The Governor's House", "type": "Historical Site", "description": "Reconstruction of the British Governor's residence", "latitude": 21.998455, "longitude": 96.471234},
                {"name": "December Garden", "type": "Garden", "description": "Strawberry farm and flower garden", "latitude": 22.062144, "longitude": 96.541011},
                {"name": "All Saints' Anglican Church", "type": "Church", "description": "Historic colonial-era church built in 1912", "latitude": 22.015622, "longitude": 96.465482},
                {"name": "Shwe Oo Min Cave Pagoda", "type": "Cave", "description": "Quiet cave temple with ancient Buddha statues", "latitude": 22.045611, "longitude": 96.491234},
                {"name": "Pyin Oo Lwin Myoma Market", "type": "Market", "description": "Central market for sweaters, jams, and wine", "latitude": 22.028455, "longitude": 96.463892},
                {"name": "Colonial House (Candacraig)", "type": "Historical Site", "description": "Tudor-style mansion now a heritage hotel", "latitude": 22.018911, "longitude": 96.475432},
                {"name": "National Landmarks Garden", "type": "Park", "description": "Miniature replicas of Myanmar's famous sites", "latitude": 21.996122, "longitude": 96.472144},
                {"name": "Mandalay Marionette Theater (Branch)", "type": "Cultural", "description": "Traditional puppet show performances", "latitude": 22.030144, "longitude": 96.461234},
                {"name": "Goteik Viaduct (Train Access)", "type": "Historical Site", "description": "Iconic railway bridge on the way to Hsipaw", "latitude": 22.589871, "longitude": 96.861214},
                {"name": "Rose Garden", "type": "Garden", "description": "Vibrant rose plantation near Kandawgyi", "latitude": 22.001255, "longitude": 96.467822},
                {"name": "Naung Kan Gyi Paya", "type": "Pagoda", "description": "Scenic hilltop pagoda overlooking the town", "latitude": 22.035622, "longitude": 96.452345},
                {"name": "Maymyo Botanical Garden Zoo", "type": "Zoo", "description": "Small wildlife exhibit within Kandawgyi", "latitude": 21.992144, "longitude": 96.468789},
                {"name": "Htoo Orange Farm", "type": "Nature", "description": "Large agro-tourism farm with mountain views", "latitude": 22.078911, "longitude": 96.567822}
            ],
            "Sagaing": [
                {"name": "Sagaing Hill", "type": "Hill", "description": "Hill dotted with monasteries", "latitude": 21.8941, "longitude": 95.9794},
                {"name": "Soon U Ponya Shin Pagoda", "type": "Pagoda", "description": "14th-century hilltop pagoda", "latitude": 21.902118075510863, "longitude": 95.99241224139317},#21.902118075510863, 95.99241224139317
                {"name": "U Min Thonze Pagoda", "type": "Pagoda", "description": "Crescent colonnade with Buddhas", "latitude": 21.911767175656834, "longitude": 95.99045782270169},#21.911767175656834, 95.99045782270169
                {"name": "Kaunghmudaw Pagoda", "type": "Pagoda", "description": "Massive dome stupa", "latitude": 21.93298230462632, "longitude": 95.93806305347705},#21.93298230462632, 95.93806305347705
                {"name": "Settawya Pagoda", "type": "Pagoda", "description": "Pagoda with Buddha footprint", "latitude": 22.04959369525332, "longitude": 96.01035997902625},#22.04959369525332, 96.01035997902625
                {"name": "Tilawkaguru", "type": "Cave Temple", "description": "Cave temple with murals", "latitude": 21.900268594164295, "longitude": 95.98997673498477},#21.900268594164295, 95.98997673498477
            ],
            "Shwebo": [
                {"name": "Shwebon Yadana Mingalar Palace", "type": "Palace", "description": "Reconstruction of Alaungpaya's palace", "latitude": 22.56584030478213, "longitude": 95.69346297382401},#22.56584030478213, 95.69346297382401
                {"name": "Maw Daw Myin Thar Pagoda", "type": "Pagoda", "description": "Historic 18th-century pagoda", "latitude":22.587229340454417, "longitude":95.69936919399049},#22.587229340454417, 95.69936919399049
                {"name": "Shwebo Railway Station", "type": "Station", "description": "UNESCO Pyu ancient city", "latitude": 22.5833249394463, "longitude": 95.69419738193837},#22.5833249394463, 95.69419738193837
            ],
            "Shwegyin": [
                {"name": "Phaya Gyi Pagoda", "type": "Pagoda", "description": "Local pagoda", "latitude": 17.921362848080474, "longitude": 96.8940022302827},#17.921362848080474, 96.8940022302827
                {"name": "Pyuntaza Lake", "type": "Lake", "description": "Lakeside relaxation", "latitude": 22.561170869218003, "longitude": 95.69456402461282},#22.561170869218003, 95.69456402461282
            ],
            "Sittwe": [
                {"name": "Sittwe Viewpoint", "type": "Viewpoint", "description": "Sunset point at river mouth", "latitude": 20.11307818131699, "longitude": 92.89799909610653},#20.11307818131699, 92.89799909610653
                {"name": "Law Ka Nandar Pagoda", "type": "Pagoda", "description": "Intricate patterned pagoda", "latitude": 20.13657219446773, "longitude": 92.88580159816412},#20.13657219446773, 92.88580159816412
                {"name": "Rakhine State Cultural Museum", "type": "Museum", "description": "Museum of Rakhine culture", "latitude": 20.14191486323318, "longitude": 92.899352926791},#20.14191486323318, 92.899352926791
                {"name": "Buddhist Museum", "type": "Museum", "description": "Ancient Buddha images collection", "latitude": 20.1389818031383, "longitude": 92.88061548216479},#20.1389818031383, 92.88061548216479
                {"name": "Central Market & Fish Market", "type": "Market", "description": "Morning market scene", "latitude": 20.14188094525268, "longitude": 92.9012995221573},#20.14188094525268, 92.9012995221573
                {"name": "Shwezedi Monastery", "type": "Monastery", "description": "Century-old monastery", "latitude": 20.13613181460687, "longitude": 92.88839003908267},#20.13613181460687, 92.88839003908267
                {"name": "Lay Shan Taung Lighthouse", "type": "Lighthouse", "description": "Hilltop lighthouse views", "latitude": 20.08582832355106, "longitude": 92.90038689610586},#20.08582832355106, 92.90038689610586
                {"name": "A Lo Taw Pyae Pagoda", "type": "Pagoda", "description": "Local pilgrimage pagoda", "latitude": 20.138587738588743, "longitude": 92.87654943862701},#20.138587738588743, 92.87654943862701
            ],
            "Tachileik": [
                {"name": "Tachileik Shwedagon Pagoda", "type": "Pagoda", "description": "Shwedagon replica on hill", "latitude": 20.45496086449752, "longitude": 99.88422295598737},#20.45496086449752, 99.88422295598737
                {"name": "Tachileik Market", "type": "Market", "description": "Border market hub", "latitude": 20.450263467300324, "longitude": 99.88208682636159},#20.450263467300324, 99.88208682636159
                {"name": "Golden Triangle Viewpoint", "type": "Viewpoint", "description": "View over Mekong tri-border", "latitude": 20.372048981304918, "longitude": 100.08866380746518},#20.372048981304918, 100.08866380746518
            ],
            "Taunggyi": [
                {"name": "Htem Sann Cave", "type": "Cave", "description": "Large limestone cave with natural stalactites", "latitude": 20.819040, "longitude": 97.335717},
                {"name": "Kakku Pagodas", "type": "Pagoda Complex", "description": "Over 2,000 ancient stupas in a tight cluster", "latitude": 20.444982, "longitude": 97.137052},
                {"name": "Kyaing Daw Pagoda", "type": "Pagoda", "description": "Prominent pagoda near the Inle gateway", "latitude": 20.658756, "longitude": 96.929325},
                {"name": "Main Ma Ye Tha Khin Ma Mountain", "type": "Mountain", "description": "Sacred mountain offering wide Shan landscape views", "latitude": 20.915917, "longitude": 96.559322},
                {"name": "Nga Phe Chaung Monastery", "type": "Monastery", "description": "Historical teak monastery on Inle Lake", "latitude": 20.516744, "longitude": 96.897802},
                {"name": "Nyaung Shwe", "type": "Town", "description": "The primary tourism hub for Inle Lake", "latitude": 20.661474, "longitude": 96.929833},
                {"name": "Shwe Bone Pwint Pagoda", "type": "Pagoda", "description": "Hilltop pagoda with a panorama of Taunggyi", "latitude": 20.777593, "longitude": 97.048770},
                {"name": "Sulamuni Lawka Chanthar Pagoda", "type": "Pagoda", "description": "Massive white stupa modeled after Ananda Temple", "latitude": 20.764522, "longitude": 97.046160},
                {"name": "Taunggyi View Point", "type": "Viewpoint", "description": "Highest point for city and Inle Lake views", "latitude": 20.784181, "longitude": 97.048337},
                {"name": "Taunggyi Myoma Market", "type": "Market", "description": "Bustling central market for local Shan produce", "latitude": 20.783648, "longitude": 97.035942},
                {"name": "Shan State Cultural Museum", "type": "Museum", "description": "Exhibits on Shan history and ethnic costumes", "latitude": 20.782100, "longitude": 97.031500},
                {"name": "St. Joseph's Cathedral", "type": "Church", "description": "Grand Catholic cathedral in the city center", "latitude": 20.785400, "longitude": 97.038200},
                {"name": "Aye Tharyar Golf Resort", "type": "Sports", "description": "Scenic golf course at the foot of Taunggyi hill", "latitude": 20.791200, "longitude": 96.975400},
                {"name": "Mway Taw Kakku", "type": "Religious Site", "description": "Sacred site for the Pa-O people", "latitude": 20.443000, "longitude": 97.135000},
                {"name": "Taunggyi University", "type": "Education", "description": "Major educational landmark of Shan State", "latitude": 20.758200, "longitude": 97.025400},
                {"name": "Red Mountain Estate Winery", "type": "Winery", "description": "Vineyard overlooking the valley (day trip)", "latitude": 20.655800, "longitude": 96.953100},
                {"name": "Sao San Tun Hospital", "type": "Landmark", "description": "Historic hospital and local landmark", "latitude": 20.780100, "longitude": 97.041200},
                {"name": "Taung-chun (The Spur)", "type": "Mountain", "description": "The 'Big Mountain' that gives the city its name", "latitude": 20.789100, "longitude": 97.058300},
                {"name": "Central Fire Station Statue", "type": "Landmark", "description": "Famous horse statue in the city center", "latitude": 20.784500, "longitude": 97.039800},
                {"name": "Balloon Festival Field", "type": "Festival Ground", "description": "Site of the world-famous Tazaungdaing festival", "latitude": 20.801200, "longitude": 97.045600}
            ],
            "Taungoo": [
                {"name": "Shwesandaw Pagoda", "type": "Pagoda", "description": "Towering golden pagoda", "latitude": 18.940281775978775, "longitude": 96.431466767608},#18.940281775978775, 96.431466767608
                {"name": "Myat Saw Nyi Naung Pagoda", "type": "Pagoda", "description": "Pagoda with glass tiles", "latitude": 18.915602936338093, "longitude": 96.51059710643884},#18.915602936338093, 96.51059710643884
                {"name": "Statue of Min Gyi Nyo", "type": "Statue", "description": "Monument to Taungoo king", "latitude": 18.92771507752175, "longitude": 96.44301812361341},#18.92771507752175, 96.44301812361341
                {"name": "Old City Moat/Walls", "type": "Heritage", "description": "Remains of Taungoo walls", "latitude": 18.952856464916678, "longitude": 96.43165997380335},#18.952856464916678, 96.43165997380335
                {"name": "Pho Kyar Elephant Camp", "type": "Sanctuary", "description": "Elephant camp in Bago Yoma", "latitude": 18.964242653878745, "longitude": 96.42711001978711},#18.964242653878745, 96.42711001978711
                {"name": "Kantawgyi Garden/Lake", "type": "Park", "description": "Artificial lake park", "latitude": 18.939741426478058, "longitude": 96.42402787449885},#18.939741426478058, 96.42402787449885
            ],
            "Thandwe": [
                {"name": "Ngapali Beach", "type": "Beach", "description": "Premier white sand beach", "latitude": 18.4159, "longitude": 94.2977},
                {"name": "Shwe San Daw Pagoda", "type": "Statue", "description": "Standing Buddha overlooking bay", "latitude": 18.457044242581695, "longitude": 94.37419058019368},#18.457044242581695, 94.37419058019368
                {"name": "Pao Wun Bridge", "type": "Bridge", "description": "Wooden bridge in mangroves", "latitude": 18.48582277944874, "longitude": 94.28912442973981},#18.48582277944874, 94.28912442973981
            ],
            "Tharrawaddy": [
                {"name": "Lawka Nandar Pagoda", "type": "Pagoda", "description": "Notable pagodas around Tharrawaddy", "latitude": 17.640910807076544, "longitude": 95.79160093572324},#17.640910807076544, 95.79160093572324
                {"name": "KoChan's Asparagus Farm", "type": "Farm", "description": "A farm with asparagus cultivation", "latitude": 17.640910807076544, "longitude": 95.79160093572324},#17.640910807076544, 95.79160093572324

            ],
            "Wakema": [
                {"name": "Maharsi Monastery", "type": "Monastery", "description": "Local pagoda", "latitude": 16.60188749130868, "longitude": 95.17310189691652},#16.60188749130868, 95.17310189691652
                {"name": "Thetkya Mahar Thiri Pagoda", "type": "Pagoda", "description": "Pagoda in Wakema", "latitude": 16.603618694081547, "longitude": 95.1743090018797},#16.603618694081547, 95.1743090018797
                {"name": "Kyon Sein", "type": "Bridge", "description": "Local religious site", "latitude": 16.59069155665345, "longitude": 95.16491269861231},#16.59069155665345, 95.16491269861231
            ],
            "Yangon": [
                {"name": "Bogyoke Aung San Market", "type": "Market", "description": "Colonial arcade market", "latitude": 16.7836, "longitude": 96.1565},
                {"name": "Bogyoke Aung San Museum", "type": "Museum", "description": "Home museum of Aung San", "latitude": 16.803879, "longitude": 96.163398},
                {"name": "Botataung Pagoda", "type": "Pagoda", "description": "Riverfront pagoda with reliquary", "latitude": 16.768306, "longitude": 96.172048},
                {"name": "Chaukhtatgyi Buddha Temple", "type": "Reclining Buddha", "description": "Huge reclining Buddha image", "latitude": 16.811719, "longitude": 96.163747},
                {"name": "Htauk Kyant War Memorial Cemetery", "type": "Cemetery", "description": "Allied war cemetery", "latitude": 17.035742, "longitude": 96.132205},
                {"name": "Inya Lake", "type": "Lake", "description": "Urban lake and promenade", "latitude": 16.838360, "longitude": 96.141599},
                {"name": "Kandawgyi Park", "type": "Park", "description": "Lake park with Karaweik barge", "latitude": 16.7987, "longitude": 96.1703},
                {"name": "Myanmar Plaza", "type": "Mall", "description": "Modern shopping mall", "latitude": 16.873034, "longitude": 96.186790},
                {"name": "National Museum of Myanmar", "type": "Museum", "description": "National collections and Lion Throne", "latitude": 16.7794, "longitude": 96.1433},
                {"name": "Shwedagon Pagoda", "type": "Pagoda", "description": "Gilded hilltop stupa", "latitude": 16.7983, "longitude": 96.1496},
                {"name": "The Secretariat Yangon", "type": "Heritage", "description": "Restored colonial secretariat", "latitude": 16.775342, "longitude": 96.165799},
                {"name": "Yangon Chinatown", "type": "District", "description": "19th Street food scene", "latitude": 16.773524, "longitude": 96.151045},
                {"name": "Yangon City Hall", "type": "Landmark", "description": "Colonial civic building", "latitude": 16.775004, "longitude": 96.159721},
                {"name": "Yangon Zoo", "type": "Zoo", "description": "Historic urban zoo", "latitude": 16.794407, "longitude": 96.159020},
                {"name": "The Pie Bar", "type": "Bar", "description": "A bar vibe within downtown Yangon", "latitude": 16.774940, "longitude": 96.164238},
                {"name": "Thanlyin Bridge", "type": "Bridge", "description": "A bridge over Thanlyin River", "latitude": 16.796369, "longitude": 96.229486},
                {"name": "Yangon-Dala Bridge", "type": "Bridge", "description": "A bridge over Yangon River", "latitude": 16.770698, "longitude": 96.144137},
                {"name": "Sule Pagoda", "type": "Pagoda", "description": "Octagonal pagoda at the city center landmark", "latitude": 16.774581, "longitude": 96.158869},
                {"name": "Yangon Central Railway Station", "type": "Transport", "description": "Grand architectural heritage rail hub", "latitude": 16.784231, "longitude": 96.160342},
                {"name": "Nga Htat Gyi Pagoda", "type": "Temple", "description": "Home to the massive five-story seated Buddha", "latitude": 16.810542, "longitude": 96.161244},
                {"name": "Musmeah Yeshua Synagogue", "type": "Heritage", "description": "The only Jewish house of worship in Myanmar", "latitude": 16.776122, "longitude": 16.776122},
                {"name": "People's Park", "type": "Park", "description": "Large urban park near Shwedagon Pagoda", "latitude": 16.796544, "longitude": 96.142311},
                {"name": "Kaba Aye Pagoda", "type": "Pagoda", "description": "World Peace Pagoda built for the 6th Buddhist Council", "latitude": 16.852144, "longitude": 96.155678},
                {"name": "Maha Bandula Park", "type": "Park", "description": "Public park featuring the Independence Monument", "latitude": 16.774822, "longitude": 96.159123}
            ]
        }

        created, updated = 0, 0
        for dest_name, items in attractions.items():
            destination = Destination.objects.filter(name__iexact=dest_name).first()
            if not destination:
                self.stdout.write(self.style.WARNING(f"Destination not found for attractions key: {dest_name}"))
                continue
            for item in items:
                lat = item.get("latitude", destination.latitude)
                lng = item.get("longitude", destination.longitude)
                attr, was_created = Attraction.objects.update_or_create(
                    destination=destination,
                    name=item["name"],
                    defaults={
                        "type": item.get("type", "Attraction"),
                        "description": item.get("description", ""),
                        "latitude": lat if lat is not None else destination.latitude,
                        "longitude": lng if lng is not None else destination.longitude,
                        "opens_at": item.get("opens_at", default_open),
                        "closes_at": item.get("closes_at", default_close),
                        "is_active": True,
                    },
                )
                created += int(was_created)
                updated += int(not was_created)

        self.stdout.write(self.style.SUCCESS(
            f"Attractions upserted: created {created}, updated {updated}"
        ))

    def populate_hotels(self):
        """Populate hotel data"""
        self.stdout.write('Populating hotels...')
        
        # Get destinations
        yangon = Destination.objects.get(name="Yangon")
        mandalay = Destination.objects.get(name="Mandalay")
        bagan = Destination.objects.get(name="Bagan")
        inle_lake = Destination.objects.get(name="Inle Lake")
        naypyidaw = Destination.objects.get(name="Naypyidaw")
        ngapali = Destination.objects.get(name="Ngapali Beach")
        pyin_oo_lwin = Destination.objects.get(name="Pyin Oo Lwin")
        kalaw = Destination.objects.get(name="Kalaw")
        hpa_an = Destination.objects.get(name="Hpa-An")
        HOTELS = [
            # Yangon Hotels
            {
                "name": "Sule Shangri-La",
                "destination": yangon,
                "address": "223 Sule Pagoda Road, Yangon 11182",
                "price_per_night": Decimal("180.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "restaurant", "gym", "bar"],
                "rating": Decimal("4.8"),
                "review_count": 1243,
                "latitude": 16.7785, "longitude": 96.1592
            },
            {
                "name": "Pan Pacific Yangon",
                "destination": yangon,
                "address": "Pyay Road, Yangon",
                "price_per_night": Decimal("150.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "restaurant", "gym", "spa"],
                "rating": Decimal("4.7"),
                "review_count": 892,
                "latitude": 16.8047, "longitude": 96.1353
            },
            {
                "name": "Hotel Grand United (21st Downtown)",
                "destination": yangon,
                "address": "21st Street, Downtown Yangon",
                "price_per_night": Decimal("50.00"),
                "category": "budget",
                "amenities": ["wifi", "restaurant", "airport shuttle"],
                "rating": Decimal("4.2"),
                "review_count": 567,
                "latitude": 16.7801, "longitude": 96.1603
            },
            
            # Mandalay Hotels
            {
                "name": "Royal Mandalay Hotel",
                "destination": mandalay,
                "address": "Mandalay City, Mandalay Region",
                "price_per_night": Decimal("95.00"),
                "category": "medium",
                "amenities": ["wifi", "pool", "restaurant", "garden"],
                "rating": Decimal("4.7"),
                "review_count": 1056,
                "latitude": 21.9811, "longitude": 96.0839
            },
            {
                "name": "Mandalay Hill Resort",
                "destination": mandalay,
                "address": "Near Mandalay Hill, Mandalay",
                "price_per_night": Decimal("120.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "restaurant", "hill view"],
                "rating": Decimal("4.6"),
                "review_count": 789,
                "latitude": 21.9542, "longitude": 96.1125
            },
            
            # Bagan Hotels
            {
                "name": "Bagan Lodge",
                "destination": bagan,
                "address": "Old Bagan, Bagan Archaeological Zone",
                "price_per_night": Decimal("120.00"),
                "category": "medium",
                "amenities": ["wifi", "pool", "restaurant", "garden", "bicycle rental"],
                "rating": Decimal("4.6"),
                "review_count": 892,
                "latitude": 21.1692, "longitude": 94.8594
            },
            {
                "name": "Aureum Palace Hotel & Resort Bagan",
                "destination": bagan,
                "address": "Bagan-Nyaung U Road, Bagan",
                "price_per_night": Decimal("200.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "golf", "restaurant", "pagoda view"],
                "rating": Decimal("4.8"),
                "review_count": 745,
                "latitude": 21.1558, "longitude": 94.8747
            },

            # Inle Lake Hotels
            {
                "name": "Novotel Inle Lake Myat Min",
                "destination": inle_lake,
                "address": "Maing Thauk Village, Inle Lake",
                "price_per_night": Decimal("140.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "lake view", "restaurant"],
                "rating": Decimal("4.7"),
                "review_count": 678,
                "latitude": 20.5601,
                "longitude": 96.9102
            },
            {
                "name": "Golden Island Cottages",
                "destination": inle_lake,
                "address": "Nyaung Shwe, Inle Lake",
                "price_per_night": Decimal("80.00"),
                "category": "medium",
                "amenities": ["wifi", "lake view", "restaurant", "boat service"],
                "rating": Decimal("4.5"),
                "review_count": 543,
                "latitude": 20.5512,
                "longitude": 96.9087
            },
            {
                "name": "Aureum Palace Hotel & Resort Inle",
                "destination": inle_lake,
                "address": "Nan Pan Village, Inle Lake",
                "price_per_night": Decimal("150.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "lake view", "restaurant"],
                "rating": Decimal("4.6"),
                "review_count": 389,
                "latitude": 20.4868,
                "longitude": 96.9062
            },
            {
                "name": "Inle Lake View Resort & Spa",
                "destination": inle_lake,
                "address": "Kaung Daing Village, Inle Lake",
                "price_per_night": Decimal("110.00"),
                "category": "medium",
                "amenities": ["wifi", "pool", "spa", "lake view", "restaurant"],
                "rating": Decimal("4.5"),
                "review_count": 412,
                "latitude": 20.6461,
                "longitude": 96.8614
            },
            {
                "name": "Pristine Lotus Resort",
                "destination": inle_lake,
                "address": "Khaung Daing Village, Inle Lake",
                "price_per_night": Decimal("120.00"),
                "category": "medium",
                "amenities": ["wifi", "pool", "spa", "lake view", "restaurant"],
                "rating": Decimal("4.4"),
                "review_count": 301,
                "latitude": 20.6426,
                "longitude": 96.8649
            },
            
            # Naypyidaw Hotels
            {
                "name": "Kempinski Hotel Naypyidaw",
                "destination": naypyidaw,
                "address": "Ottarathiri Township, Naypyidaw",
                "price_per_night": Decimal("160.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "golf", "restaurant", "conference"],
                "rating": Decimal("4.7"),
                "review_count": 432,
                "latitude": 19.7481,
                "longitude": 96.1158
            },
            {
                "name": "Hilton Nay Pyi Taw",
                "destination": naypyidaw,
                "address": "JV-001 Taw Win Thiri Road, Dekkhina Thiri Township",
                "price_per_night": Decimal("140.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "fitness center", "restaurant", "conference"],
                "rating": Decimal("4.5"),
                "review_count": 245,
                "latitude": 19.6984,
                "longitude": 96.0931
            },
            {
                "name": "PARKROYAL Nay Pyi Taw",
                "destination": naypyidaw,
                "address": "Hotel Zone, Dekkhina Thiri Township",
                "price_per_night": Decimal("135.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "restaurant", "garden"],
                "rating": Decimal("4.4"),
                "review_count": 210,
                "latitude": 19.6835,
                "longitude": 96.1087
            },
            {
                "name": "The Lake Garden Nay Pyi Taw - MGallery",
                "destination": naypyidaw,
                "address": "Dekkhina Thiri Road, Naypyidaw",
                "price_per_night": Decimal("150.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "restaurant", "lake view"],
                "rating": Decimal("4.6"),
                "review_count": 190,
                "latitude": 19.7065,
                "longitude": 96.1060
            },
            {
                "name": "Grand Amara Hotel",
                "destination": naypyidaw,
                "address": "Hotel Zone, Dekkhina Thiri Township",
                "price_per_night": Decimal("110.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "parking", "garden"],
                "rating": Decimal("4.3"),
                "review_count": 150,
                "latitude": 19.6905,
                "longitude": 96.1012
            },
            {
                "name": "Horizon Lake View Resort",
                "destination": naypyidaw,
                "address": "Taw Win Yadanar Road, Dekkhina Thiri Township",
                "price_per_night": Decimal("95.00"),
                "category": "medium",
                "amenities": ["wifi", "pool", "restaurant", "lake view"],
                "rating": Decimal("4.2"),
                "review_count": 132,
                "latitude": 19.6923,
                "longitude": 96.1045
            },
            {
                "name": "Hotel Royal ACE",
                "destination": naypyidaw,
                "address": "Taw Win Yadanar Road, Dekkhina Thiri Township",
                "price_per_night": Decimal("85.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "parking"],
                "rating": Decimal("4.1"),
                "review_count": 98,
                "latitude": 19.6948,
                "longitude": 96.1007
            },
            {
                "name": "Shwe San Eain Hotel",
                "destination": naypyidaw,
                "address": "Taw Win Yadanar Road, Naypyidaw",
                "price_per_night": Decimal("70.00"),
                "category": "budget",
                "amenities": ["wifi", "restaurant", "parking"],
                "rating": Decimal("3.9"),
                "review_count": 76,
                "latitude": 19.6894,
                "longitude": 96.1071
            },
            {
                "name": "Nirvana Hotel & Resort",
                "destination": naypyidaw,
                "address": "Hotel Zone 1, Dekkhina Thiri Township",
                "price_per_night": Decimal("90.00"),
                "category": "medium",
                "amenities": ["wifi", "pool", "restaurant", "garden"],
                "rating": Decimal("4.0"),
                "review_count": 85,
                "latitude": 19.6856,
                "longitude": 96.1122
            },
            {
                "name": "Excel Capital Hotel",
                "destination": naypyidaw,
                "address": "Dekkhina Thiri Township, Naypyidaw",
                "price_per_night": Decimal("65.00"),
                "category": "budget",
                "amenities": ["wifi", "restaurant", "parking"],
                "rating": Decimal("3.8"),
                "review_count": 60,
                "latitude": 19.6878,
                "longitude": 96.1095
            },
            
            # Ngapali Beach Hotels
            {
                "name": "Amata Resort & Spa",
                "destination": ngapali,
                "address": "Ngapali Beach, Rakhine State",
                "price_per_night": Decimal("130.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "beachfront", "restaurant"],
                "rating": Decimal("4.6"),
                "review_count": 389,
                "latitude": 18.4189, 
                "longitude": 94.3012
            },
            
            # Pyin Oo Lwin Hotels
            {
                "name": "Kandawgyi Hill Resort",
                "destination": pyin_oo_lwin,
                "address": "Kandawgyi Lake Area, Pyin Oo Lwin, Mandalay Region",
                "price_per_night": Decimal("75.00"),
                "category": "medium",
                "amenities": ["wifi", "garden", "restaurant", "mountain view"],
                "rating": Decimal("4.4"),
                "review_count": 267,
                "latitude": 22.0289,
                "longitude": 96.4583
            },
            {
                "name": "Aureum Palace Hotel & Resort Pyin Oo Lwin",
                "destination": pyin_oo_lwin,
                "address": "Governor's House Area, Pyin Oo Lwin",
                "price_per_night": Decimal("160.00"),
                "category": "luxury",
                "amenities": ["wifi", "pool", "spa", "restaurant", "garden"],
                "rating": Decimal("4.6"),
                "review_count": 180,
                "latitude": 22.0367,
                "longitude": 96.4678
            },
            {
                "name": "Hotel Pyin Oo Lwin",
                "destination": pyin_oo_lwin,
                "address": "Circular Road, Pyin Oo Lwin",
                "price_per_night": Decimal("60.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "parking"],
                "rating": Decimal("4.1"),
                "review_count": 198,
                "latitude": 22.0375,
                "longitude": 96.4662
            },
            {
                "name": "Hotel Maymyo",
                "destination": pyin_oo_lwin,
                "address": "Central Pyin Oo Lwin",
                "price_per_night": Decimal("55.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "garden"],
                "rating": Decimal("4.0"),
                "review_count": 154,
                "latitude": 22.0349,
                "longitude": 96.4705
            },
            {
                "name": "Shwe Pyi Thain Kha Hotel",
                "destination": pyin_oo_lwin,
                "address": "Pyin Oo Lwin Downtown",
                "price_per_night": Decimal("50.00"),
                "category": "budget",
                "amenities": ["wifi", "restaurant", "parking"],
                "rating": Decimal("3.9"),
                "review_count": 120,
                "latitude": 22.0325,
                "longitude": 96.4680
            },
            {
                "name": "Royal Parkview Hotel",
                "destination": pyin_oo_lwin,
                "address": "Lanthaya Street, Pyin Oo Lwin",
                "price_per_night": Decimal("70.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "parking", "garden"],
                "rating": Decimal("4.2"),
                "review_count": 140,
                "latitude": 22.0392,
                "longitude": 96.4693
            },
            {
                "name": "Thiha Bala Hotel",
                "destination": pyin_oo_lwin,
                "address": "Circular Road, Pyin Oo Lwin",
                "price_per_night": Decimal("45.00"),
                "category": "budget",
                "amenities": ["wifi", "parking"],
                "rating": Decimal("3.8"),
                "review_count": 95,
                "latitude": 22.0331,
                "longitude": 96.4634
            },
            {
                "name": "The View Resort & Restaurant",
                "destination": pyin_oo_lwin,
                "address": "Hilltop Area, Pyin Oo Lwin",
                "price_per_night": Decimal("85.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "mountain view", "garden"],
                "rating": Decimal("4.3"),
                "review_count": 160,
                "latitude": 22.0441,
                "longitude": 96.4762
            },
            {
                "name": "Hotel Sakura Pyin Oo Lwin",
                "destination": pyin_oo_lwin,
                "address": "Quarter 4, Pyin Oo Lwin",
                "price_per_night": Decimal("48.00"),
                "category": "budget",
                "amenities": ["wifi", "restaurant"],
                "rating": Decimal("3.9"),
                "review_count": 110,
                "latitude": 22.0363,
                "longitude": 96.4711
            },
            {
                "name": "Hsaung Thazin Hotel",
                "destination": pyin_oo_lwin,
                "address": "City Center, Pyin Oo Lwin",
                "price_per_night": Decimal("42.00"),
                "category": "budget",
                "amenities": ["wifi", "parking"],
                "rating": Decimal("3.7"),
                "review_count": 88,
                "latitude": 22.0318,
                "longitude": 96.4659
            },

            # Kalaw Hotel 
            {
                "name": "Sanctuary Kalaw",
                "destination": kalaw,
                "address": "Kalaw Town, Shan State",
                "price_per_night": Decimal("120.00"),
                "category": "luxury",
                "amenities": ["wifi", "garden", "restaurant", "spa"],
                "rating": Decimal("4.6"),
                "review_count": 245,
                "latitude": 20.6335,
                "longitude": 96.5897
            },
            {
                "name": "Kalaw Hill Lodge",
                "destination": kalaw,
                "address": "Kyein Chaung Road, Kalaw",
                "price_per_night": Decimal("70.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "garden", "mountain view"],
                "rating": Decimal("4.3"),
                "review_count": 180,
                "latitude": 20.6331,
                "longitude": 96.5862
            },
            {
                "name": "Santa Maria Resort",
                "destination": kalaw,
                "address": "Kalaw, Shan State",
                "price_per_night": Decimal("60.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "parking", "garden"],
                "rating": Decimal("4.1"),
                "review_count": 142,
                "latitude": 20.6308,
                "longitude": 96.5850
            },
            {
                "name": "Back Packers Guest House Kalaw",
                "destination": kalaw,
                "address": "Main Street, Kalaw",
                "price_per_night": Decimal("35.00"),
                "category": "budget",
                "amenities": ["wifi", "restaurant", "parking"],
                "rating": Decimal("4.0"),
                "review_count": 120,
                "latitude": 20.6320,
                "longitude": 96.5875
            },
            {
                "name": "The Kalaw Heritage Resort",
                "destination": kalaw,
                "address": "Kalaw Town, Shan State",
                "price_per_night": Decimal("95.00"),
                "category": "medium",
                "amenities": ["wifi", "garden", "restaurant", "mountain view"],
                "rating": Decimal("4.4"),
                "review_count": 168,
                "latitude": 20.6347,
                "longitude": 96.5882
            },
            {
                "name": "Pine Hill Hotel",
                "destination": kalaw,
                "address": "Near Kalaw Central, Shan State",
                "price_per_night": Decimal("50.00"),
                "category": "budget",
                "amenities": ["wifi", "parking", "restaurant"],
                "rating": Decimal("3.9"),
                "review_count": 102,
                "latitude": 20.6315,
                "longitude": 96.5848
            },
            {
                "name": "Kalaw Boutique Hotel",
                "destination": kalaw,
                "address": "Kyein Chaung Road, Kalaw",
                "price_per_night": Decimal("85.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "garden", "mountain view"],
                "rating": Decimal("4.2"),
                "review_count": 145,
                "latitude": 20.6350,
                "longitude": 96.5890
            },
            {
                "name": "Garden View Hotel Kalaw",
                "destination": kalaw,
                "address": "Near Central Kalaw",
                "price_per_night": Decimal("55.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "garden"],
                "rating": Decimal("4.1"),
                "review_count": 132,
                "latitude": 20.6328,
                "longitude": 96.5865
            },
            {
                "name": "Backpacker Inn Kalaw",
                "destination": kalaw,
                "address": "Main Street, Kalaw",
                "price_per_night": Decimal("30.00"),
                "category": "budget",
                "amenities": ["wifi", "parking"],
                "rating": Decimal("3.8"),
                "review_count": 95,
                "latitude": 20.6338,
                "longitude": 96.5870
            },
            {
                "name": "Kalaw Hilltop Resort",
                "destination": kalaw,
                "address": "Hill Area, Kalaw Town",
                "price_per_night": Decimal("100.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "mountain view", "garden"],
                "rating": Decimal("4.5"),
                "review_count": 172,
                "latitude": 20.6362,
                "longitude": 96.5903
            },
            
            # Hpa-An Hotels
            {
                "name": "Hotel Win Unity Hpa-An",
                "destination": hpa_an,
                "address": "Main Street, Hpa-An Town",
                "price_per_night": Decimal("60.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "parking"],
                "rating": Decimal("4.2"),
                "review_count": 145,
                "latitude": 16.8855,
                "longitude": 97.6340
            },
            {
                "name": "Royal Kayin Hotel",
                "destination": hpa_an,
                "address": "Near Thanlwin River, Hpa-An",
                "price_per_night": Decimal("70.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "parking", "garden"],
                "rating": Decimal("4.3"),
                "review_count": 120,
                "latitude": 16.8828,
                "longitude": 97.6365
            },
            {
                "name": "Hpa-An Hotel",
                "destination": hpa_an,
                "address": "Main Road, Downtown Hpa-An",
                "price_per_night": Decimal("50.00"),
                "category": "budget",
                "amenities": ["wifi", "parking", "restaurant"],
                "rating": Decimal("4.0"),
                "review_count": 98,
                "latitude": 16.8841,
                "longitude": 97.6352
            },
            {
                "name": "Kywe Oo Guesthouse",
                "destination": hpa_an,
                "address": "Shwe Taung San Road, Hpa-An",
                "price_per_night": Decimal("35.00"),
                "category": "budget",
                "amenities": ["wifi", "parking"],
                "rating": Decimal("3.9"),
                "review_count": 76,
                "latitude": 16.8832,
                "longitude": 97.6360
            },
            {
                "name": "Sae Taw Hotel",
                "destination": hpa_an,
                "address": "Near Hpa-An Market",
                "price_per_night": Decimal("55.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "parking"],
                "rating": Decimal("4.1"),
                "review_count": 85,
                "latitude": 16.8858,
                "longitude": 97.6371
            },
            {
                "name": "Bagan Guesthouse Hpa-An",
                "destination": hpa_an,
                "address": "Central Hpa-An",
                "price_per_night": Decimal("40.00"),
                "category": "budget",
                "amenities": ["wifi", "restaurant"],
                "rating": Decimal("4.0"),
                "review_count": 64,
                "latitude": 16.8820,
                "longitude": 97.6345
            },
            {
                "name": "River View Hotel",
                "destination": hpa_an,
                "address": "Near Thanlwin River, Hpa-An",
                "price_per_night": Decimal("75.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "river view", "parking"],
                "rating": Decimal("4.4"),
                "review_count": 110,
                "latitude": 16.8815,
                "longitude": 97.6378
            },
            {
                "name": "Green Hill Resort Hpa-An",
                "destination": hpa_an,
                "address": "Hill Area, Hpa-An",
                "price_per_night": Decimal("80.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "garden", "mountain view"],
                "rating": Decimal("4.5"),
                "review_count": 95,
                "latitude": 16.8871,
                "longitude": 97.6328
            },
            {
                "name": "Blue Sky Hotel Hpa-An",
                "destination": hpa_an,
                "address": "Downtown Hpa-An",
                "price_per_night": Decimal("65.00"),
                "category": "medium",
                "amenities": ["wifi", "restaurant", "parking"],
                "rating": Decimal("4.3"),
                "review_count": 88,
                "latitude": 16.8845,
                "longitude": 97.6368
            },
            {
                "name": "Sunset Guesthouse Hpa-An",
                "destination": hpa_an,
                "address": "Near Mount Zwegabin Base",
                "price_per_night": Decimal("50.00"),
                "category": "budget",
                "amenities": ["wifi", "restaurant", "parking"],
                "rating": Decimal("4.1"),
                "review_count": 72,
                "latitude": 16.8882,
                "longitude": 97.6391
            }
            
        ]
        
        for hotel_data in HOTELS:
            hotel, created = Hotel.objects.get_or_create(
                name=hotel_data["name"],
                destination=hotel_data["destination"],
                defaults={
                    "address": hotel_data["address"],
                    "price_per_night": hotel_data["price_per_night"],
                    "category": hotel_data["category"],
                    "amenities": hotel_data["amenities"],
                    "rating": hotel_data["rating"],
                    "review_count": hotel_data["review_count"],
                    "latitude": hotel_data.get("latitude"),
                    "longitude": hotel_data.get("longitude"),
                    "is_active": True
                }
            )
            if created:
                self.stdout.write(f"Created hotel: {hotel.name} in {hotel.destination.name}")
        
        self.stdout.write(self.style.SUCCESS(f'Hotels populated: {Hotel.objects.count()} hotels'))
    
    def populate_comprehensive_transport(self):
        """Populate COMPREHENSIVE transport data for ALL destinations"""
        self.stdout.write('=' * 60)
        self.stdout.write('POPULATING COMPREHENSIVE TRANSPORT DATA')
        self.stdout.write('=' * 60)
        
        # Create airlines
        airlines_data = [
            {'name': 'Air KBZ', 'code': 'K7', 'is_default_for_domestic': True},
            {'name': 'Myanmar National Airlines', 'code': 'UB', 'is_default_for_domestic': True},
            {'name': 'Golden Myanmar Airlines', 'code': 'Y5', 'is_default_for_domestic': False},
            {'name': 'Mann Yadanarpon Airlines', 'code': '7Y', 'is_default_for_domestic': False},
        ]
        
        airlines = {}
        for airline_data in airlines_data:
            airline, created = Airline.objects.get_or_create(
                code=airline_data['code'],
                defaults=airline_data
            )
            airlines[airline.code] = airline
            self.stdout.write(f"{'Created' if created else 'Found'} airline: {airline.name}")
        
        # Get major destinations with airports
        airport_destinations = [
            'Yangon', 'Mandalay', 'Naypyidaw', 'Bagan', 'Heho', 'Thandwe',
            'Sittwe', 'Myitkyina', 'Tachileik', 'Kawthaung', 'Dawei', 'Myeik'
        ]
        
        destinations_map = {}
        for dest_name in airport_destinations:
            # Prefer exact name match; fall back to icontains; pick first non-region if ties
            dest_qs = Destination.objects.filter(name__iexact=dest_name).order_by('is_region', 'name')
            if not dest_qs.exists():
                dest_qs = Destination.objects.filter(name__icontains=dest_name).order_by('is_region', 'name')
            dest = dest_qs.first()

            if dest:
                destinations_map[dest_name] = dest
            else:
                self.stdout.write(self.style.WARNING(f"Destination '{dest_name}' not found, skipping..."))
                continue
        
        self.stdout.write(f"Found {len(destinations_map)} airport destinations")
        
        # ========== POPULATE FLIGHTS BETWEEN ALL AIRPORT CITIES ==========
        self.stdout.write('\nCreating flights between all airport cities...')
        flight_count = 0
        dest_list = list(destinations_map.values())
        
        for i, departure in enumerate(dest_list):
            for j, arrival in enumerate(dest_list):
                if departure != arrival:
                    # Create 1-2 flights per route
                    for flight_num in range(1, random.randint(2, 3)):
                        airline = random.choice(list(airlines.values()))
                        
                        # Generate flight times
                        departure_hour = random.choice([6, 8, 10, 12, 14, 16, 18])
                        departure_time_obj = time(departure_hour, random.choice([0, 15, 30, 45]))
                        
                        # Flight duration (1-3 hours)
                        duration_hours = random.randint(1, 3)
                        arrival_hour = (departure_hour + duration_hours) % 24
                        arrival_time_obj = time(arrival_hour, random.choice([0, 15, 30, 45]))
                        
                        # Price based on distance and class
                        base_price = random.randint(50000, 250000)
                        
                        flight_class = random.choice(['low', 'medium', 'high'])
                        if flight_class == 'low':
                            price = Decimal(str(base_price * 0.8))
                            total_seats = random.randint(150, 200)
                        elif flight_class == 'medium':
                            price = Decimal(str(base_price))
                            total_seats = random.randint(120, 180)
                        else:  # high
                            price = Decimal(str(base_price * 1.5))
                            total_seats = random.randint(80, 120)
                        
                        available_seats = int(total_seats * random.uniform(0.6, 0.9))
                        
                        flight_number = f"{airline.code} {random.randint(100, 999)}"
                        
                        flight, created = Flight.objects.get_or_create(
                            airline=airline,
                            flight_number=flight_number,
                            departure=departure,
                            arrival=arrival,
                            defaults={
                                'departure_time': departure_time_obj,
                                'arrival_time': arrival_time_obj,
                                'duration': timedelta(hours=duration_hours, minutes=random.randint(0, 45)),
                                'price': price,
                                'category': flight_class,
                                'total_seats': total_seats,
                                'available_seats': available_seats,
                                'description': f"Flight from {departure.name} to {arrival.name} operated by {airline.name}",
                                'is_active': True
                            }
                        )
                        
                        if created:
                            flight_count += 1
                            if flight_count % 10 == 0:
                                self.stdout.write(f"  Created {flight_count} flights...")
        
        self.stdout.write(self.style.SUCCESS(f'Created {flight_count} flights total'))
        
        # ========== POPULATE BUS SERVICES ON MAJOR ROUTES ==========
        self.stdout.write('\nCreating bus services on major routes...')
        
        bus_companies = ['JJ Express', 'Elite Express', 'Shwe Mandalar', 'Lumbini Bus', 
                        'Mandalar Express', 'Asia Express', 'Shwe Pyi', 'Aung Gabar']
        
        # Major bus routes in Myanmar
        major_bus_routes = [
            ('Yangon', 'Mandalay'),
            ('Yangon', 'Bagan'),
            ('Yangon', 'Naypyidaw'),
            ('Mandalay', 'Bagan'),
            ('Mandalay', 'Naypyidaw'),
            ('Yangon', 'Taunggyi'),
            ('Mandalay', 'Taunggyi'),
            ('Yangon', 'Hpa-An'),
            ('Yangon', 'Mawlamyine'),
            ('Mandalay', 'Monywa'),
            ('Yangon', 'Pyin Oo Lwin'),
            ('Mandalay', 'Pyin Oo Lwin'),
            ('Yangon', 'Pathein'),
            ('Yangon', 'Sittwe'),
            ('Mandalay', 'Loikaw'),
        ]
        
        bus_count = 0
        for route in major_bus_routes:
            from_city_name, to_city_name = route
            
            # Resolve departure/arrival deterministically to avoid MultipleObjectsReturned
            dep_qs = Destination.objects.filter(name__iexact=from_city_name).order_by('is_region', 'name')
            if not dep_qs.exists():
                dep_qs = Destination.objects.filter(name__icontains=from_city_name).order_by('is_region', 'name')
            arr_qs = Destination.objects.filter(name__iexact=to_city_name).order_by('is_region', 'name')
            if not arr_qs.exists():
                arr_qs = Destination.objects.filter(name__icontains=to_city_name).order_by('is_region', 'name')

            departure = dep_qs.first()
            arrival = arr_qs.first()
            if not departure or not arrival:
                continue
            
            # Create 1-2 bus services per route
            for bus_num in range(1, random.randint(2, 3)):
                company = random.choice(bus_companies)
                
                # Bus types and corresponding prices
                bus_types = ['standard', 'vip', 'luxury']
                bus_type = random.choice(bus_types)
                
                if bus_type == 'standard':
                    price = Decimal(str(random.randint(15000, 25000)))
                    total_seats = random.randint(40, 50)
                elif bus_type == 'vip':
                    price = Decimal(str(random.randint(25000, 40000)))
                    total_seats = random.randint(30, 40)
                else:  # luxury
                    price = Decimal(str(random.randint(40000, 60000)))
                    total_seats = random.randint(20, 30)
                
                available_seats = int(total_seats * random.uniform(0.5, 0.8))
                
                # Departure time (evening buses for overnight journeys)
                departure_hour = random.choice([18, 19, 20, 21, 22])
                departure_time_obj = time(departure_hour, random.choice([0, 15, 30, 45]))
                
                # Duration (7-12 hours for most routes)
                duration_hours = random.randint(7, 12)
                
                bus, created = BusService.objects.get_or_create(
                    company=company,
                    departure=departure,
                    arrival=arrival,
                    bus_type=bus_type,
                    defaults={
                        'departure_time': departure_time_obj,
                        'duration': timedelta(hours=duration_hours),
                        'price': price,
                        'total_seats': total_seats,
                        'available_seats': available_seats,
                        'bus_number': f"BUS{random.randint(1000, 9999)}",
                        'description': f"{bus_type.upper()} bus service from {departure.name} to {arrival.name}",
                        'is_active': True
                    }
                )
                
                if created:
                    bus_count += 1
                    if bus_count % 5 == 0:
                        self.stdout.write(f"  Created {bus_count} buses...")
        
        self.stdout.write(self.style.SUCCESS(f'Created {bus_count} bus services'))
        
        # ========== POPULATE CAR RENTALS IN MAJOR CITIES ==========
        self.stdout.write('\nCreating car rentals in major cities...')
        
        car_companies = ['City Car Rental', 'Premium Rentals', 'Luxury Wheels', 
                        'Myanmar Rent-a-Car', 'Avis Myanmar', 'Hertz Myanmar', 
                        'Local Car Hire', 'Express Rentals']
        
        car_models = [
            {'model': 'Toyota Vios', 'type': 'economy', 'seats': 4, 'base_price': 35000},
            {'model': 'Toyota Corolla', 'type': 'economy', 'seats': 5, 'base_price': 40000},
            {'model': 'Honda City', 'type': 'economy', 'seats': 5, 'base_price': 38000},
            {'model': 'Toyota Fortuner', 'type': 'suv', 'seats': 7, 'base_price': 70000},
            {'model': 'Mitsubishi Pajero', 'type': 'suv', 'seats': 7, 'base_price': 75000},
            {'model': 'Suzuki Ertiga', 'type': 'suv', 'seats': 7, 'base_price': 55000},
            {'model': 'Mercedes E-Class', 'type': 'luxury', 'seats': 5, 'base_price': 150000},
            {'model': 'BMW 5 Series', 'type': 'luxury', 'seats': 5, 'base_price': 160000},
            {'model': 'Toyota Hiace', 'type': 'van', 'seats': 12, 'base_price': 90000},
        ]
        
        # Major cities for car rentals
        car_cities = ['Yangon', 'Mandalay', 'Naypyidaw', 'Bagan', 'Taunggyi', 
                     'Mawlamyine', 'Pyin Oo Lwin', 'Ngapali Beach']
        
        car_count = 0
        for city_name in car_cities:
            loc_qs = Destination.objects.filter(name__iexact=city_name).order_by('is_region', 'name')
            if not loc_qs.exists():
                loc_qs = Destination.objects.filter(name__icontains=city_name).order_by('is_region', 'name')
            location = loc_qs.first()
            if not location:
                continue
            
            # Create 2-4 car rentals per city
            for rental_num in range(random.randint(2, 5)):
                company = random.choice(car_companies)
                car_model_data = random.choice(car_models)
                
                # Price variation
                price_variation = random.uniform(0.8, 1.2)
                price_per_day = Decimal(str(int(car_model_data['base_price'] * price_variation)))
                
                # Features based on car type
                base_features = ['AC']
                if car_model_data['type'] == 'economy':
                    features = base_features + ['Manual', 'Radio']
                elif car_model_data['type'] == 'suv':
                    features = base_features + ['Automatic', 'GPS', 'Bluetooth']
                elif car_model_data['type'] == 'luxury':
                    features = base_features + ['Automatic', 'GPS', 'Leather Seats', 'Sunroof', 'Premium Sound']
                else:  # van
                    features = base_features + ['Manual', 'Spacious']
                
                transmission = 'Automatic' if 'Automatic' in features else 'Manual'
                
                car, created = CarRental.objects.get_or_create(
                    company=company,
                    car_model=car_model_data['model'],
                    location=location,
                    defaults={
                        'car_type': car_model_data['type'],
                        'seats': car_model_data['seats'],
                        'price_per_day': price_per_day,
                        'features': features,
                        'is_available': True,
                        'transmission': transmission,
                        'fuel_type': random.choice(['Petrol', 'Diesel']),
                        'year': random.randint(2018, 2023),
                        'description': f"{car_model_data['type'].title()} car rental in {location.name}",
                    }
                )
                
                if created:
                    car_count += 1
                    if car_count % 5 == 0:
                        self.stdout.write(f"  Created {car_count} cars...")
        
        self.stdout.write(self.style.SUCCESS(f'Created {car_count} car rentals'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Transport Summary: {flight_count} flights, {bus_count} buses, {car_count} cars'
        ))
    
    def create_transport_schedules(self):
        """Create schedules for next 30 days for all transport"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('CREATING TRANSPORT SCHEDULES FOR NEXT 30 DAYS')
        self.stdout.write('=' * 60)
        
        # Get all transport
        flights = Flight.objects.filter(is_active=True)
        buses = BusService.objects.filter(is_active=True)
        cars = CarRental.objects.filter(is_available=True)
        
        self.stdout.write(f"Found: {flights.count()} flights, {buses.count()} buses, {cars.count()} cars")
        
        # Create schedules for next 30 days
        today = timezone.now().date()
        schedule_count = 0
        
        # Flights schedules
        self.stdout.write('Creating flight schedules...')
        for flight in flights:
            for day in range(30):
                schedule_date = today + timedelta(days=day)
                
                # Calculate dynamic price (higher on weekends)
                is_weekend = schedule_date.weekday() >= 5
                price_multiplier = 1.2 if is_weekend else 1.0
                schedule_price = Decimal(str(float(flight.price) * price_multiplier))
                
                # Calculate dynamic availability
                base_available = flight.available_seats
                if is_weekend:
                    available_seats = max(5, int(base_available * 0.7))
                else:
                    available_seats = max(10, int(base_available * 0.9))
                
                # Random booking simulation
                booked_seats = random.randint(0, int(available_seats * 0.3))
                final_available = available_seats - booked_seats
                
                schedule, created = TransportSchedule.objects.get_or_create(
                    transport_type='flight',
                    transport_id=flight.id,
                    travel_date=schedule_date,
                    defaults={
                        'departure_time': flight.departure_time,
                        'arrival_time': flight.arrival_time,
                        'total_seats': flight.total_seats,
                        'available_seats': final_available,
                        'price': schedule_price,
                        'is_active': True
                    }
                )
                
                if created:
                    schedule_count += 1
        
        self.stdout.write(f"Created {schedule_count} flight schedules")
        total_schedules = schedule_count
        
        # Bus schedules
        self.stdout.write('Creating bus schedules...')
        bus_schedule_count = 0
        for bus in buses:
            for day in range(30):
                schedule_date = today + timedelta(days=day)
                
                # Dynamic pricing
                is_weekend = schedule_date.weekday() >= 5
                price_multiplier = 1.15 if is_weekend else 1.0
                schedule_price = Decimal(str(float(bus.price) * price_multiplier))
                
                # Dynamic availability
                base_available = bus.available_seats
                if is_weekend:
                    available_seats = max(3, int(base_available * 0.6))
                else:
                    available_seats = max(5, int(base_available * 0.8))
                
                # Random booking
                booked_seats = random.randint(0, int(available_seats * 0.4))
                final_available = available_seats - booked_seats
                
                schedule, created = TransportSchedule.objects.get_or_create(
                    transport_type='bus',
                    transport_id=bus.id,
                    travel_date=schedule_date,
                    defaults={
                        'departure_time': bus.departure_time,
                        'total_seats': bus.total_seats,
                        'available_seats': final_available,
                        'price': schedule_price,
                        'is_active': True
                    }
                )
                
                if created:
                    bus_schedule_count += 1
        
        self.stdout.write(f"Created {bus_schedule_count} bus schedules")
        total_schedules += bus_schedule_count
        
        # Car schedules
        self.stdout.write('Creating car schedules...')
        car_schedule_count = 0
        for car in cars:
            for day in range(30):
                schedule_date = today + timedelta(days=day)
                
                # Dynamic pricing (higher on weekends)
                is_weekend = schedule_date.weekday() >= 5
                price_multiplier = 1.25 if is_weekend else 1.0
                schedule_price = Decimal(str(float(car.price_per_day) * price_multiplier))
                
                # Car availability (less available on weekends)
                if is_weekend:
                    available_seats = random.choice([0, 1])
                else:
                    available_seats = random.choice([1, 1, 1, 0])
                
                schedule, created = TransportSchedule.objects.get_or_create(
                    transport_type='car',
                    transport_id=car.id,
                    travel_date=schedule_date,
                    defaults={
                        'total_seats': car.seats,
                        'available_seats': available_seats,
                        'price': schedule_price,
                        'is_active': True
                    }
                )
                
                if created:
                    car_schedule_count += 1
        
        self.stdout.write(f"Created {car_schedule_count} car schedules")
        total_schedules += car_schedule_count
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Schedules created: {total_schedules} total schedules for next 30 days'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   - Flight schedules: {schedule_count}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   - Bus schedules: {bus_schedule_count}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'   - Car schedules: {car_schedule_count}'
        ))