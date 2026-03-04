from django.core.management.base import BaseCommand
from planner.models import Destination
import os
from django.conf import settings
from django.core.files import File


class Command(BaseCommand):
    help = 'Populate complete destination data (text, images, latitude & longitude) for all 37 destinations'

    def handle(self, *args, **kwargs):

        destination_data = {

            # 1. Yangon
            'Yangon': {
                'latitude': 16.8409,
                'longitude': 96.1735,
                'history': 'Former capital of Myanmar until 2005, Yangon (formerly Rangoon) was founded by King Alaungpaya in the 18th century. It became the British colonial capital in 1885 and remains the country\'s commercial and cultural hub with beautiful colonial architecture mixed with modern developments.',
                'attractions': '• Shwedagon Pagoda (2,500 years old, covered in gold)\n• Sule Pagoda (2,000 years old, city center landmark)\n• Bogyoke Aung San Market (Scott Market)\n• Chaukhtatgyi Buddha Temple (70-meter reclining Buddha)\n• Kandawgyi Lake and Karaweik Palace\n• National Museum of Myanmar',
                'activities': '• Visit golden pagodas at sunrise or sunset\n• Explore colonial architecture in downtown\n• Shop at local markets for handicrafts\n• Enjoy Burmese tea at traditional tea shops\n• Take a cruise on Yangon River\n• Experience nightlife in Chinatown',
                'cultural_info': 'Mix of British colonial architecture and traditional Burmese culture. Major Buddhist center with over 2,000 pagodas. Vibrant street life with diverse ethnic communities including Indian and Chinese influences.',
                'best_time_to_visit': 'November to February (cool and dry season)',
                'local_cuisine': '• Mohinga (national dish - fish noodle soup)\n• Burmese tea leaf salad (Lahpet Thoke)\n• Shan noodles\n• Burmese curries with rice\n• Street food in Chinatown',
                'tips': '• Visit Shwedagon Pagoda at sunset for magical lighting\n• Dress modestly when visiting religious sites\n• Try street food but be cautious with hygiene\n• Use Grab app for taxis\n• Exchange money at authorized money changers',
                'folder_name': 'Yangon'
            },

            # 2. Mandalay
            'Mandalay': {
                'latitude': 21.9588,
                'longitude': 96.0891,
                'history': 'Last royal capital of the Burmese monarchy before British annexation in 1885. Founded by King Mindon in 1857 as a new capital to fulfill a Buddhist prophecy. The palace was destroyed in WWII but reconstructed.',
                'attractions': '• Mandalay Palace (reconstructed royal palace)\n• Kuthodaw Pagoda (World\'s Largest Book - 729 marble slabs)\n• Mahamuni Buddha Temple (highly revered Buddha image)\n• U Bein Bridge (1.2km teak bridge over Taungthaman Lake)\n• Mandalay Hill (panoramic city views)\n• Shwenandaw Monastery (golden teak monastery)',
                'activities': '• Watch sunset from Mandalay Hill\n• Take boat trip on Irrawaddy River\n• Visit traditional craft workshops (gold leaf, marble, silk)\n• See Moustache Brothers comedy show\n• Explore ancient capitals nearby (Sagaing, Ava, Amarapura)',
                'cultural_info': 'Center of Burmese culture, traditional arts, and Buddhism. Known as the cultural heart of Myanmar. Home to most of the country\'s monks and traditional craftspeople.',
                'best_time_to_visit': 'November to February (pleasant weather)',
                'local_cuisine': '• Mandalay Mont Di (rice noodles with chicken curry)\n• Shan tofu salads\n• Burmese sweets and snacks\n• Traditional Burmese tea shops',
                'tips': '• Hire a guide to understand historical significance\n• Visit gold leaf workshops to see traditional craft\n• Take comfortable shoes for pagoda visits\n• Bargain at jade markets',
                'folder_name': 'Mandalay'
            },

            # 3. Bagan
            'Bagan': {
                'latitude': 21.1717,
                'longitude': 94.8585,
                'history': 'Ancient capital of the Pagan Kingdom from 9th to 13th centuries. Once contained over 10,000 Buddhist temples, pagodas and monasteries. UNESCO World Heritage Site since 2019.',
                'attractions': '• Ananda Temple (most beautiful temple)\n• Shwesandaw Pagoda (best sunset views)\n• Dhammayangyi Temple (largest temple)\n• Thatbyinnyu Temple (tallest temple)\n• Mount Popa (volcanic peak with monastery)\n• Archaeological Museum',
                'activities': '• Hot air balloon rides at sunrise\n• E-bike exploration of temple plains\n• Sunset viewing from temple tops\n• Traditional lacquerware workshops\n• Visit local villages',
                'cultural_info': 'One of the world\'s greatest archaeological sites representing the peak of Buddhist art and architecture in Myanmar.',
                'best_time_to_visit': 'November to February (balloon season)',
                'local_cuisine': '• Bagan traditional dishes\n• Local palm toddy\n• Temple area restaurants',
                'tips': '• Get Bagan archaeological zone pass\n• Respect temple rules (no climbing some temples)\n• Hire licensed guide\n• Bring sunscreen and hat',
                'folder_name': 'Bagan'
            },

            # 4. Inle Lake
            'Inle Lake': {
                'latitude': 20.5860,
                'longitude': 96.9100,
                'history': 'Freshwater lake at 880m altitude, home to Intha people known for unique leg-rowing technique. Traditional floating villages and gardens.',
                'attractions': '• Floating villages (Ywama, In Paw Khon)\n• Phaung Daw Oo Pagoda (most sacred site)\n• Nga Hpe Chaung Monastery (jumping cat monastery)\n• Indein Village with ancient stupas\n• Local markets rotating between villages\n• Vineyard and winery',
                'activities': '• Boat tours of floating villages\n• Visit traditional handicraft workshops (silver, weaving, cigars)\n• Trekking to hill tribe villages\n• Cooking classes\n• Bicycle rides around lake',
                'cultural_info': 'Intha people with unique culture, leg-rowing fishermen, floating gardens. Mix of Shan, Pa-O and other ethnic groups.',
                'best_time_to_visit': 'September to March',
                'local_cuisine': '• Inle Lake fish dishes\n• Shan noodles\n• Local tomato dishes\n• Fresh vegetables from floating gardens',
                'tips': '• Take boat tour early morning\n• Visit rotating markets\n• Respect local fishing communities\n• Stay in overwater bungalows',
                'folder_name': 'Inle Lake'
            },

            # 5. Naypyidaw
            'Naypyidaw': {
                'latitude': 19.7633,
                'longitude': 96.0785,
                'history': 'Capital city of Myanmar since 2005, built from scratch in a remote location. Name means "Royal Capital" or "Abode of Kings". One of the world\'s largest capital cities by area.',
                'attractions': '• Uppatasanti Pagoda (replica of Shwedagon)\n• National Landmark Garden\n• Myanmar Parliament complex\n• Water Fountain Garden\n• Zoological Gardens\n• Gem Museum',
                'activities': '• Visit impressive government buildings\n• Explore wide, empty boulevards\n• Shopping at Junction Center\n• Golfing at international courses',
                'cultural_info': 'Planned city with unique urban design, extremely low population density. Showcase of modern Myanmar architecture.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Government district restaurants\n• International cuisine options\n• Local Myanmar dishes',
                'tips': '• Private transport needed due to distances\n• Photography restrictions in government areas\n• Visit during working days for activity',
                'folder_name': 'Naypyidaw'
            },

            # 6. 
            'Ngapali Beach': {
                'latitude': 18.4607,
                'longitude': 94.3001,
                'history': 'Ngapali Beach is Myanmar\'s premier beach destination, named after Italian city Napoli by a homesick Italian. Pristine beaches with palm trees stretching along Bay of Bengal.',
                'attractions': '• Ngapali Beach (8km white sandy beach)\n• Traditional fishing villages\n• Pearl Island\n• Lin Thar Island\n• Local seafood markets',
                'activities': '• Beach relaxation and swimming\n• Snorkeling and diving\n• Boat trips to nearby islands\n• Visiting fishing villages\n• Seafood dining',
                'cultural_info': 'Mix of Rakhine fishing culture and beach tourism. Traditional fishing methods still used. Relaxed, uncrowded atmosphere.',
                'best_time_to_visit': 'October to May (dry season)',
                'local_cuisine': '• Fresh seafood and lobsters\n• Rakhine fish curry\n• Coconut-based dishes\n• Beachside barbecues',
                'tips': '• Book resorts in advance during peak season\n• Support local fishermen\n• Respect marine conservation areas\n• Try sunset seafood dinners',
                'folder_name': 'Ngapali Beach'
            },

            # 7. Ngwe Saung Beach
            'Ngwe Saung Beach': {
                'latitude': 16.8570,
                'longitude': 94.3865,
                'history': 'Ngwe Saung means "Silver Beach" - a 15km stretch of pristine white sand beach on Bay of Bengal. More relaxed alternative to Ngapali.',
                'attractions': '• Ngwe Saung Beach\n• Lover\'s Island\n• Fishing villages\n• Elephant Camp\n• Local markets',
                'activities': '• Swimming and sunbathing\n• Water sports\n• Island hopping\n• Visiting fishing communities\n• Horse riding on beach',
                'cultural_info': 'Developing beach destination with mix of tourism and local fishing communities. More backpacker-friendly than Ngapali.',
                'best_time_to_visit': 'November to April',
                'local_cuisine': '• Beachfront seafood restaurants\n• Fresh grilled fish\n• Local Rakhine dishes\n• Tropical fruits',
                'tips': '• Bring cash as ATMs limited\n• Book accommodation in advance\n• Try beachfront dining\n• Respect local fishing areas',
                'folder_name': 'Ngwe Saung Beach'
            },

            # 8. Kawthaung
            'Kawthaung': {
                'latitude': 9.9824,
                'longitude': 98.5500,
                'history': 'Southernmost town in Myanmar, opposite Thailand\'s Ranong. Historical trading port and gateway to Mergui Archipelago.',
                'attractions': '• Andaman Club Resort & Casino\n• Maliwan Island\n• Victoria Point\n• Local markets\n• Border crossing point',
                'activities': '• Island hopping to Mergui Archipelago\n• Diving and snorkeling\n• Fishing trips\n• Border shopping\n• Visiting Moken sea gypsy villages',
                'cultural_info': 'Mix of Burmese, Thai, and sea gypsy cultures. Important fishing and trading port.',
                'best_time_to_visit': 'November to April',
                'local_cuisine': '• Fresh seafood\n• Thai-influenced dishes\n• Southern Myanmar curries\n• Tropical fruits',
                'tips': '• Arrange boat tours for islands\n• Check border crossing requirements\n• Bring enough cash\n• Respect Moken communities',
                'folder_name': 'Kawthaung'
            },

            # 9. Tachileik
            'Tachileik': {
                'latitude': 20.4475,
                'longitude': 99.8808,
                'history': 'Border town with Thailand (Mae Sai) in Golden Triangle region. Important trading post between Myanmar and Thailand.',
                'attractions': '• Border market\n• Shan-style temples\n• Hill tribe villages nearby\n• Golden Triangle area\n• Local markets',
                'activities': '• Cross-border shopping\n• Visiting hill tribe villages\n• Exploring Golden Triangle\n• Local market visits\n• Cultural tours',
                'cultural_info': 'Shan majority with strong Thai influence. Trading hub with diverse ethnic groups.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Shan noodles\n• Thai street food\n• Local Shan dishes\n• Border market snacks',
                'tips': '• Day trips to Thailand possible\n• Bargain at markets\n• Respect photography restrictions\n• Check visa requirements',
                'folder_name': 'Tachileik'
            },

            # 10. Myitkyina
            'Myitkyina': {
                'latitude': 25.3836,
                'longitude': 97.3964,
                'history': 'Capital of Kachin State, strategic location on Ledo Road during WWII. Center of jade mining and Kachin culture.',
                'attractions': '• Mali Hka and Nmai Hka rivers confluence\n• Kachin Manaw Festival grounds\n• Local jade markets\n• War Memorial\n• Kachin cultural sites',
                'activities': '• River cruises\n• Visiting Kachin villages\n• Jade market exploration\n• Cultural festivals\n• Trekking in surrounding hills',
                'cultural_info': 'Kachin ethnic majority with distinct traditions, clothing, and festivals. Center of jade trade with China.',
                'best_time_to_visit': 'November to March',
                'local_cuisine': '• Kachin bamboo shoot dishes\n• Fermented foods\n• Local herbs and vegetables\n• Traditional stews',
                'tips': '• Travel with guide to remote areas\n• Respect local customs\n• Check travel advisories\n• Visit during Manaw Festival',
                'folder_name': 'Myitkyina'
            },

            # 11. Lashio
            'Lashio': {
                'latitude': 22.9359,
                'longitude': 97.7498,
                'history': 'Largest town in northern Shan State, end of Burma Road from China. Important trading and transportation hub.',
                'attractions': '• Lashio market (largest in region)\n• Hot springs\n• Buddhist temples\n• Shan cultural sites\n• Colonial-era buildings',
                'activities': '• Market shopping\n• Hot spring bathing\n• Visiting temples\n• Exploring surrounding countryside\n• Cultural tours',
                'cultural_info': 'Mix of Shan, Chinese, and other ethnic groups. Important trading center for goods from China.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Shan-Chinese fusion cuisine\n• Noodle dishes\n• Local street food\n• Traditional Shan dishes',
                'tips': '• Bargain at market\n• Visit hot springs\n• Check travel permissions\n• Try local tea shops',
                'folder_name': 'Lashio'
            },

            # 12. Monywa
            'Monywa': {
                'latitude': 22.1086,
                'longitude': 95.1358,
                'history': 'City on Chindwin River, known for Thanboddhay Pagoda and giant Buddha statues. Important agricultural and trading center.',
                'attractions': '• Thanboddhay Pagoda (with thousands of Buddha images)\n• Bodhi Tataung (129m standing Buddha)\n• Shwe Ba Hill caves\n• Local markets\n• Chindwin River',
                'activities': '• Pagoda visits\n• River trips\n• Cave exploration\n• Photography tours\n• Cultural visits',
                'cultural_info': 'Buddhist pilgrimage site with impressive religious monuments. Mix of Burmese and Shan cultures.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Local river fish dishes\n• Shan-style food\n• Traditional snacks\n• Market food stalls',
                'tips': '• Visit Thanboddhay Pagoda in morning\n• Climb Shwe Ba Hill for views\n• Take boat trip on river\n• Respect religious sites',
                'folder_name': 'Monywa'
            },

            # 13. Sagaing
            'Sagaing': {
                'latitude': 21.8787,
                'longitude': 95.9797,
                'history': 'Ancient capital of Sagaing Kingdom (14th century). Now a major Buddhist meditation center with hundreds of monasteries.',
                'attractions': '• Sagaing Hill with numerous pagodas\n• Soon U Ponya Shin Pagoda\n• Kaunghmudaw Pagoda (huge dome-shaped)\n• Ava Bridge (oldest in Myanmar)\n• Meditation centers',
                'activities': '• Monastery visits\n• Meditation retreats\n• Photography\n• Pilgrimage tours\n• River views',
                'cultural_info': 'Spiritual center of Myanmar with thousands of monks and nuns. Important site for Buddhist studies and meditation.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Monastery vegetarian food\n• Simple Burmese dishes\n• Local snacks\n• Traditional sweets',
                'tips': '• Dress modestly\n• Respect meditation silence\n• Visit at sunrise or sunset\n• Donations appreciated',
                'folder_name': 'Sagaing'
            },

            # 14. Magway
            'Magway': {
                'latitude': 20.1496,
                'longitude': 94.9320,
                'history': 'Capital of Magway Region, center of Myanmar\'s oil industry. Important agricultural area along Irrawaddy River.',
                'attractions': '• Myathalon Pagoda\n• Local markets\n• Oil fields\n• Irrawaddy River\n• Traditional villages',
                'activities': '• Pagoda visits\n• Market exploration\n• Countryside tours\n• River trips\n• Cultural experiences',
                'cultural_info': 'Agricultural heartland and oil-producing region. Traditional Burmese rural culture.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Local oilseed dishes\n• Traditional Burmese curries\n• River fish\n• Agricultural products',
                'tips': '• Visit during local festivals\n• Explore rural areas\n• Try local snacks\n• Respect farming communities',
                'folder_name': 'Magway'
            },

            # 15. Pakokku
            'Pakokku': {
                'latitude': 21.3349,
                'longitude': 95.0844,
                'history': 'Town on Irrawaddy River between Bagan and Mandalay. Famous for thanakha production and cheroot making.',
                'attractions': '• Irrawaddy River\n• Thanakha plantations\n• Local markets\n• Traditional workshops\n• Riverside views',
                'activities': '• River boat trips\n• Visiting thanakha farms\n• Market shopping\n• Cheroot workshop tours\n• Photography',
                'cultural_info': 'Center of thanakha (cosmetic paste) production. Traditional cheroot making industry.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• River fish dishes\n• Local snacks\n• Traditional sweets\n• Market food',
                'tips': '• Visit thanakha plantations\n• Try local cheroots\n• Take boat trip\n• Buy authentic thanakha',
                'folder_name': 'Pakokku'
            },

            # 16. Minbu
            'Minbu': {
                'latitude': 20.1814,
                'longitude': 94.8759,
                'history': 'Town on Irrawaddy River known for salt production. Agricultural center in Magway Region.',
                'attractions': '• Irrawaddy River\n• Salt fields\n• Local pagodas\n• Traditional villages\n• Agricultural areas',
                'activities': '• River trips\n• Visiting salt production\n• Pagoda visits\n• Countryside exploration\n• Cultural tours',
                'cultural_info': 'Riverine culture with traditional salt production methods. Agricultural community.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• River fish\n• Salt-preserved foods\n• Local vegetables\n• Traditional dishes',
                'tips': '• Visit salt fields\n• Take boat trip\n• Try salt-preserved dishes\n• Respect local customs',
                'folder_name': 'Minbu'
            },

            # 17. Pathein
            'Pathein': {
                'latitude': 16.7792,
                'longitude': 94.7321,
                'history': 'Capital of Ayeyarwady Region, famous for handmade umbrella production since colonial times. Important river port.',
                'attractions': '• Shwemokhtaw Pagoda\n• Umbrella workshops\n• Pathein River\n• Local markets\n• Nearby beaches (Chaungtha)',
                'activities': '• Umbrella workshop tours\n• River cruises\n• Pagoda visits\n• Beach trips\n• Market shopping',
                'cultural_info': 'Famous for colorful handmade paper umbrellas. Riverine culture with strong Mon influence.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Fresh river fish\n• Pathein mont (rice cakes)\n• Local sweets\n• Traditional curries',
                'tips': '• Buy authentic handmade umbrellas\n• Take river boat trip\n• Visit early morning market\n• Try local sweets',
                'folder_name': 'Pathein'
            },

            # 18. Dawei
            'Dawei': {
                'latitude': 14.0823,
                'longitude': 98.1915,
                'history': 'Capital of Tanintharyi Region, developing deep sea port and special economic zone. Known for beautiful beaches.',
                'attractions': '• Maungmagan Beach\n• Sin Htaw Beach\n• Dawei town\n• Local pagodas\n• Rubber plantations',
                'activities': '• Beach relaxation\n• Visiting local markets\n• Exploring countryside\n• Photography\n• Cultural tours',
                'cultural_info': 'Southern Burmese culture with Thai influences. Known for rubber, cashew, and fruit production.',
                'best_time_to_visit': 'November to April',
                'local_cuisine': '• Southern curries\n• Fresh seafood\n• Tropical fruits\n• Cashew-based dishes',
                'tips': '• Visit beaches outside town\n• Try local cashews\n• Check travel permissions\n• Respect local communities',
                'folder_name': 'Dawei'
            },

            # 19. Myeik
            'Myeik': {
                'latitude': 12.4395,
                'longitude': 98.6003,
                'history': 'Gateway to Mergui Archipelago, historic port city with Portuguese, Dutch, and British influences. Center of pearl industry.',
                'attractions': '• Myeik town\n• Pearl Island\n• Nearby islands\n• Pearl farms\n• Colonial architecture',
                'activities': '• Island hopping\n• Diving and snorkeling\n• Visiting pearl farms\n• Exploring town\n• Photography',
                'cultural_info': 'Mix of Burmese, Thai, and sea gypsy cultures. Famous for pearl industry and island life.',
                'best_time_to_visit': 'November to April',
                'local_cuisine': '• Fresh seafood\n• Pearl farm oysters\n• Thai-influenced dishes\n• Island cuisine',
                'tips': '• Arrange boat tours in advance\n• Visit pearl farms\n• Respect Moken communities\n• Bring diving gear',
                'folder_name': 'Myeik'
            },

            # 20. Ye
            'Ye': {
                'latitude': 15.2500,
                'longitude': 97.8500,
                'history': 'Coastal town in Mon State, known for fishing and nearby beaches. Less developed tourism destination.',
                'attractions': '• Ye town\n• Nearby beaches\n• Fishing villages\n• Local markets\n• Mon cultural sites',
                'activities': '• Beach visits\n• Fishing village tours\n• Seafood dining\n• Market exploration\n• Cultural tours',
                'cultural_info': 'Mon coastal culture with fishing traditions. More authentic local experience.',
                'best_time_to_visit': 'November to April',
                'local_cuisine': '• Fresh seafood\n• Mon-style fish dishes\n• Local vegetables\n• Traditional Mon food',
                'tips': '• Bring cash\n• Respect fishing communities\n• Try local seafood\n• Visit during festivals',
                'folder_name': 'Ye'
            },

            # 21. Taunggyi
            'Taunggyi': {
                'latitude': 20.7883,
                'longitude': 97.0337,
                'history': 'Capital of Shan State at 1,436m altitude. Famous for Tazaungdaing Hot Air Balloon Festival. Former British hill station.',
                'attractions': '• Kakku Pagodas (thousands of stupas)\n• Shwe Phone Pwint Cave\n• Local markets\n• Viewpoint\n• Vineyards',
                'activities': '• Festival participation (November)\n• Trekking to Kakku\n• Visiting vineyards\n• Cultural tours\n• Photography',
                'cultural_info': 'Shan, Pa-O, and other ethnic groups. Center for Shan culture and festivals.',
                'best_time_to_visit': 'November for festival, otherwise November-February',
                'local_cuisine': '• Shan noodles\n• Tofu dishes\n• Local wines\n• Traditional Shan food',
                'tips': '• Book accommodation during festival\n• Visit Kakku early morning\n• Dress warmly at night\n• Try local wine',
                'folder_name': 'Taunggyi'
            },

            # 22. Heho
            'Heho': {
                'latitude': 20.7460,
                'longitude': 96.7920,
                'history': 'Main airport gateway to Inle Lake and Shan State. Small town that grew with tourism development.',
                'attractions': '• Nearby Inle Lake\n• Pindaya Caves\n• Kakku Pagodas\n• Local markets\n• Shan villages',
                'activities': '• Airport transfers to Inle\n• Local market visits\n• Starting point for treks\n• Cultural stops\n• Photography',
                'cultural_info': 'Shan ethnic area with Pa-O communities nearby. Agricultural and tourism gateway.',
                'best_time_to_visit': 'October to March',
                'local_cuisine': '• Shan noodles\n• Local vegetables\n• Tea leaf salad\n• Simple dishes',
                'tips': '• Organize transport to Inle in advance\n• Can stay overnight if flights require\n• Visit local markets\n• Try Shan food',
                'folder_name': 'Heho'
            },

            # 23. Kalaw
            'Kalaw': {
                'latitude': 20.6256,
                'longitude': 96.5633,
                'history': 'Hill station founded by British as summer retreat. Starting point for multi-day treks to Inle Lake.',
                'attractions': '• British colonial buildings\n• Local markets\n• Pine forests\n• Nearby villages\n• Viewpoints',
                'activities': '• Trekking to Inle Lake (2-3 days)\n• Village visits\n• Market shopping\n• Photography\n• Cultural tours',
                'cultural_info': 'Mix of Nepali, Indian, Shan, and Burmese communities. Cool climate hill station.',
                'best_time_to_visit': 'November to March for trekking',
                'local_cuisine': '• Trekker food\n• Local vegetables\n• Shan dishes\n• Simple meals',
                'tips': '• Book treks with reputable guides\n• Dress in layers\n• Start treks early morning\n• Bring trekking gear',
                'folder_name': 'Kalaw'
            },

            # 24. Hsipaw
            'Hsipaw': {
                'latitude': 22.6206,
                'longitude': 97.3066,
                'history': 'Former Shan princely state. Trekking center to Shan and Palaung villages. Made famous by Mr. Charles Guest House.',
                'attractions': '• Hsipaw Palace\n• Local markets\n• Nearby waterfalls\n• Tea plantations\n• Shan villages',
                'activities': '• Trekking to villages\n• Visiting tea plantations\n• Exploring countryside\n• Cultural tours\n• Photography',
                'cultural_info': 'Shan culture with palace heritage. Gateway to authentic Shan village experiences.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Shan noodles\n• Tea leaf salad\n• Local vegetables\n• Traditional Shan food',
                'tips': '• Get trekking info from Mr. Charles\n• Visit local tea shops\n• Respect palace area\n• Hire local guides',
                'folder_name': 'Hsipaw'
            },

            # 25. Pyin Oo Lwin
            'Pyin Oo Lwin': {
                'latitude': 22.0350,
                'longitude': 96.4560,
                'history': 'Former British hill station called Maymyo. Known for colonial architecture, botanical gardens, and temperate climate.',
                'attractions': '• National Kandawgyi Botanical Gardens\n• Pwe Kauk Waterfall\n• Colonial buildings\n• Purcell Tower\n• Strawberry farms',
                'activities': '• Horse carriage rides\n• Garden visits\n• Waterfall trips\n• Strawberry picking\n• Photography',
                'cultural_info': 'British colonial heritage mixed with Shan and Burmese cultures. Famous for flowers and cool climate.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Strawberry dishes\n• Local jams\n• British-influenced baked goods\n• Traditional food',
                'tips': '• Take horse carriage tour\n• Visit gardens early\n• Try local strawberries\n• Dress for cool weather',
                'folder_name': 'Pyin Oo Lwin'
            },

            # 26. Kyaukme
            'Kyaukme': {
                'latitude': 22.5460,
                'longitude': 96.9430,
                'history': 'Town in northern Shan State, trading center for tea and agricultural products. Gateway to trekking areas.',
                'attractions': '• Local markets\n• Tea plantations\n• Nearby villages\n• Buddhist temples\n• Countryside',
                'activities': '• Tea plantation visits\n• Trekking\n• Market exploration\n• Cultural tours\n• Photography',
                'cultural_info': 'Shan and Palaung ethnic groups. Center of tea production and trade.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Shan tea dishes\n• Local vegetables\n• Traditional stews\n• Tea-based food',
                'tips': '• Visit tea plantations\n• Trek to nearby villages\n• Try local tea\n• Respect farming communities',
                'folder_name': 'Kyaukme'
            },

            # 27. Kengtung
            'Kengtung': {
                'latitude': 21.2867,
                'longitude': 99.6110,
                'history': 'Historical Shan city near Thailand and Laos borders in Golden Triangle. Known as "City of Three Mountains".',
                'attractions': '• Kengtung town\n• Wat Jong Kham\n• Hill tribe villages\n• Local markets\n• Mountain views',
                'activities': '• Hill tribe village visits\n• Trekking\n• Cultural tours\n• Photography\n• Market shopping',
                'cultural_info': 'Diverse ethnic groups including Akha, Lahu, and Shan. Unique architecture and traditions.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Shan specialties\n• Hill tribe foods\n• Local teas\n• Traditional dishes',
                'tips': '• Requires special permit\n• Hire local guide for villages\n• Respect ethnic traditions\n• Check travel permissions',
                'folder_name': 'Kengtung'
            },

            # 28. Sittwe
            'Sittwe': {
                'latitude': 20.1470,
                'longitude': 92.8980,
                'history': 'Capital of Rakhine State on Bay of Bengal. Important port city and British colonial administrative center.',
                'attractions': '• Viewpoint\n• Sittwe Beach\n• Buddhist monasteries\n• Colonial buildings\n• Local markets',
                'activities': '• Boat trips to Mrauk U\n• Beach walks\n• Visiting monasteries\n• Photography\n• Cultural tours',
                'cultural_info': 'Rakhine Buddhist culture with distinct architecture. Mix of Rakhine, Burmese, and Indian influences.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Rakhine fish curries\n• Ngapi (fermented fish paste)\n• Seafood\n• Local specialties',
                'tips': '• Gateway to Mrauk U\n• Book boat tickets in advance\n• Respect local sensitivities\n• Visit during festivals',
                'folder_name': 'Sittwe'
            },

            # 29. Mrauk U
            'Mrauk U': {
                'latitude': 20.5956,
                'longitude': 93.1930,
                'history': 'Ancient capital of Arakan Kingdom (15th-18th centuries). Archaeological site with hundreds of temples, often called "second Bagan".',
                'attractions': '• Shittaung Temple\n• Htukkanthein Temple\n• Kothaung Temple\n• Archaeological zone\n• Local villages',
                'activities': '• Temple exploration\n• Photography\n• Boat trips\n• Village visits\n• Cultural tours',
                'cultural_info': 'Rakhine Buddhist kingdom heritage. Similar to Bagan but less visited with unique architectural style.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Rakhine fish dishes\n• Local specialties\n• Traditional food\n• Simple meals',
                'tips': '• Travel by boat from Sittwe\n• Hire guide for temples\n• Bring cash\n• Respect archaeological sites',
                'folder_name': 'Mrauk U'
            },

            # 30. Kyaukpyu
            'Kyaukpyu': {
                'latitude': 19.4264,
                'longitude': 93.5490,
                'history': 'Town on Ramree Island in Rakhine State. Site of China-Myanmar oil and gas pipelines. Important port.',
                'attractions': '• Kyaukpyu town\n• Nearby islands\n• Beaches\n• Local markets\n• Pipeline area',
                'activities': '• Island visits\n• Beach relaxation\n• Exploring town\n• Photography\n• Cultural tours',
                'cultural_info': 'Rakhine coastal culture with recent Chinese investment. Traditional fishing communities.',
                'best_time_to_visit': 'November to April',
                'local_cuisine': '• Seafood\n• Rakhine curries\n• Local fish dishes\n• Traditional food',
                'tips': '• Check travel permissions\n• Visit nearby islands\n• Try local seafood\n• Respect local communities',
                'folder_name': 'Kyaukpyu'
            },

            # 31. Ann
            'Ann': {
                'latitude': 19.7825,
                'longitude': 94.0261,
                'history': 'Town in Rakhine State, administrative center and agricultural area. Stopover point between major towns.',
                'attractions': '• Ann town\n• Local markets\n• Nearby villages\n• Buddhist temples\n• Countryside',
                'activities': '• Market exploration\n• Village visits\n• Countryside tours\n• Photography\n• Cultural stops',
                'cultural_info': 'Rakhine agricultural community. Traditional farming and fishing practices.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Rakhine agricultural products\n• Local dishes\n• Fresh produce\n• Traditional food',
                'tips': '• Stop while traveling in Rakhine\n• Visit local farms\n• Try fresh produce\n• Respect local customs',
                'folder_name': 'Ann'
            },

            # 32. Mawlamyine
            'Mawlamyine': {
                'latitude': 16.4540,
                'longitude': 97.6440,
                'history': 'Capital of Mon State, first capital of British Burma. Famous in literature through George Orwell and Rudyard Kipling.',
                'attractions': '• Kyaikthanlan Pagoda\n• Uzina Pagoda (reclining Buddha)\n• Bilu Island\n• Mon Cultural Museum\n• Colonial architecture',
                'activities': '• River cruises\n• Visiting Mon villages\n• Colonial architecture tours\n• Photography\n• Cultural tours',
                'cultural_info': 'Mon culture center with distinct language and traditions. Strong British colonial heritage.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Mon curry\n• Fermented fish dishes\n• Local sweets\n• Traditional Mon food',
                'tips': '• Visit viewpoints at sunset\n• Take ferry to Bilu Island\n• Try Mon cuisine\n• Explore colonial area',
                'folder_name': 'Mawlamyine'
            },

            # 33. Mudon
            'Mudon': {
                'latitude': 16.2570,
                'longitude': 97.7240,
                'history': 'Town in Mon State between Mawlamyine and Ye. Agricultural center with Mon cultural influence.',
                'attractions': '• Local markets\n• Nearby villages\n• Mon cultural sites\n• Buddhist temples\n• Countryside',
                'activities': '• Village visits\n• Market exploration\n• Countryside tours\n• Cultural stops\n• Photography',
                'cultural_info': 'Mon culture with traditional farming practices. Less touristy authentic experience.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Mon curries\n• Local vegetables\n• Traditional sweets\n• Simple dishes',
                'tips': '• Stop while traveling between cities\n• Visit local workshops\n• Try Mon desserts\n• Respect local customs',
                'folder_name': 'Mudon'
            },

            # 34. Thaton
            'Thaton': {
                'latitude': 16.9160,
                'longitude': 97.3670,
                'history': 'Ancient capital of Mon Kingdom before Bago. Historical importance in Mon history and Buddhism.',
                'attractions': '• Shwezayan Pagoda\n• Ancient city walls\n• Local museums\n• Buddhist sites\n• Historical ruins',
                'activities': '• Historical exploration\n• Pagoda visits\n• Cultural tours\n• Photography\n• Educational visits',
                'cultural_info': 'Ancient Mon heritage with historical significance. Important Buddhist site.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Traditional Mon dishes\n• Local specialties\n• Historical recipes\n• Simple food',
                'tips': '• Visit with historical guide\n• Explore ruins\n• Respect archaeological sites\n• Learn about Mon history',
                'folder_name': 'Thaton'
            },

            # 35. Hpa-An
            'Hpa-An': {
                'latitude': 16.8900,
                'longitude': 97.6340,
                'history': 'Capital of Kayin State surrounded by limestone karst mountains and caves. Natural beauty and cultural sites.',
                'attractions': '• Mount Zwegabin\n• Sadan Cave\n• Kawgun Cave\n• Kyauk Kalap Pagoda\n• Local villages',
                'activities': '• Cave exploration\n• Mountain climbing\n• River trips\n• Visiting Buddhist sites\n• Photography',
                'cultural_info': 'Kayin (Karen) culture with Buddhist cave monasteries. Beautiful natural scenery.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Kayin bamboo shoot dishes\n• River fish\n• Local vegetables\n• Traditional food',
                'tips': '• Climb Mount Zwegabin early morning\n• Visit caves with guide\n• Respect religious sites\n• Try local food',
                'folder_name': 'Hpa-An'
            },

            # 36. Loikaw
            'Loikaw': {
                'latitude': 19.6770,
                'longitude': 97.2090,
                'history': 'Capital of Kayah State, known for Kayan "long-neck" women. Recently opened to tourism.',
                'attractions': '• Kayan villages\n• Taung Kwe Pagoda\n• Local markets\n• Kayah cultural sites\n• Hill tribe areas',
                'activities': '• Visiting Kayan villages\n• Trekking\n• Cultural tours\n• Photography\n• Educational visits',
                'cultural_info': 'Kayah and Kayan ethnic groups. Famous for women wearing brass neck coils. Unique traditions.',
                'best_time_to_visit': 'November to February',
                'local_cuisine': '• Kayah bamboo shoot dishes\n• Fermented foods\n• Traditional stews\n• Local specialties',
                'tips': '• Respectful village visits only\n• Ask permission before photos\n• Support community tourism\n• Learn about culture',
                'folder_name': 'Loikaw'
            },

            # 37. Hakha
            'Hakha': {
                'latitude': 22.6500,
                'longitude': 93.6100,
                'history': 'Capital of Chin State in remote western mountains. Strong Christian influence and traditional tattoo culture.',
                'attractions': '• Mount Victoria (Nat Ma Taung)\n• Chin villages\n• Local churches\n• Traditional houses\n• Mountain views',
                'activities': '• Mountain trekking\n• Visiting Chin villages\n• Cultural tours\n• Photography\n• Educational visits',
                'cultural_info': 'Chin ethnic groups with facial tattoo traditions for women. Predominantly Christian with unique customs.',
                'best_time_to_visit': 'November to March',
                'local_cuisine': '• Chin cuisine with smoked meats\n• Local vegetables\n• Corn-based dishes\n• Traditional food',
                'tips': '• Requires special permit\n• Hire local guide\n• Respect cultural traditions\n• Check travel advisories',
                'folder_name': 'Hakha'
            }

        }

        base_dir = os.path.join(settings.MEDIA_ROOT, 'destinations')

        for dest_name, data in destination_data.items():
            try:
                destination = Destination.objects.get(name=dest_name)
                self.stdout.write(f'\n🔍 Processing {dest_name}...')

                # Text fields
                for field in [
                    'history', 'attractions', 'activities',
                    'cultural_info', 'best_time_to_visit',
                    'local_cuisine', 'tips'
                ]:
                    if field in data:
                        setattr(destination, field, data[field])

                # ✅ Coordinates (CRITICAL FOR REAL WEATHER)
                destination.latitude = data.get('latitude')
                destination.longitude = data.get('longitude')

                # Images
                folder_name = data.get('folder_name')
                if folder_name:
                    folder_path = os.path.join(base_dir, folder_name)
                    self.stdout.write(f'📁 Folder path: {folder_path}')

                    if os.path.exists(folder_path):
                        self.stdout.write(f'✅ Folder exists')
                        
                        # Check what files exist
                        files = os.listdir(folder_path)
                        self.stdout.write(f'📄 Files in folder: {files}')
                        
                        # Main image
                        main_image = os.path.join(folder_path, 'main.jpg')
                        if os.path.exists(main_image):
                            self.stdout.write(f'✅ Found main.jpg at: {main_image}')
                            
                            # Save to main_image field
                            with open(main_image, 'rb') as f:
                                destination.main_image.save(
                                    f'{folder_name}/main.jpg',
                                    File(f),
                                    save=False
                                )
                            self.stdout.write(f'📸 Saved to main_image field')
                            
                            # ALSO save to image field (for backward compatibility)
                            with open(main_image, 'rb') as f:
                                destination.image.save(
                                    f'{folder_name}/main.jpg',
                                    File(f),
                                    save=False
                                )
                            self.stdout.write(f'📸 Also saved to image field')
                        else:
                            self.stdout.write(f'❌ main.jpg not found at: {main_image}')
                        
                        # Gallery images with detailed logging
                        for i in range(1, 5):
                            gallery_image = os.path.join(folder_path, f'gallery{i}.jpg')
                            field_name = f'gallery_image{i}'
                            
                            self.stdout.write(f'🔍 Checking gallery{i}.jpg...')
                            self.stdout.write(f'   Path: {gallery_image}')
                            
                            if os.path.exists(gallery_image):
                                self.stdout.write(f'   ✅ File exists')
                                if hasattr(destination, field_name):
                                    self.stdout.write(f'   ✅ Field {field_name} exists in model')
                                    
                                    # Check if field already has a value
                                    current_value = getattr(destination, field_name)
                                    if current_value:
                                        self.stdout.write(f'   ⚠️ Field already has value: {current_value}')
                                    
                                    try:
                                        with open(gallery_image, 'rb') as f:
                                            getattr(destination, field_name).save(
                                                f'{folder_name}/gallery{i}.jpg',
                                                File(f),
                                                save=False
                                            )
                                        self.stdout.write(f'   ✅ Gallery image {i} saved successfully')
                                    except Exception as e:
                                        self.stdout.write(f'   ❌ Error saving gallery {i}: {str(e)}')
                                else:
                                    self.stdout.write(f'   ❌ Field {field_name} does NOT exist in Destination model!')
                            else:
                                self.stdout.write(f'   ❌ File does not exist')
                    else:
                        self.stdout.write(f'❌ Folder does not exist: {folder_path}')

                destination.save()
                self.stdout.write(self.style.SUCCESS(f'✅ Updated {dest_name}'))

            except Destination.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Destination {dest_name} not found'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error updating {dest_name}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('\n🎉 ALL 37 DESTINATIONS UPDATED WITH FULL DATA + COORDINATES!'))
        self.stdout.write(f'📊 Total destinations processed: {len(destination_data)}')