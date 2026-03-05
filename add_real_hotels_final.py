# C:\Users\ASUS\MyanmarTravelPlanner\add_real_hotels_final.py
import os
import sys
import django
import json
import random
from datetime import time
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
django.setup()

from planner.models import Destination, Hotel
from planner.models_room import RoomType, Room

# ============================================================================
# DELETE ALL EXISTING HOTELS AND ROOMS
# ============================================================================
def delete_all_hotels_and_rooms():
    """Delete all existing hotels and rooms from the database"""
    print("=" * 70)
    print("DELETING ALL EXISTING HOTELS AND ROOMS")
    print("=" * 70)
    
    # Delete all rooms first (due to foreign key constraints)
    rooms_deleted = Room.objects.count()
    Room.objects.all().delete()
    
    # Then delete all hotels
    hotels_deleted = Hotel.objects.count()
    Hotel.objects.all().delete()
    
    print(f"✅ Deleted {rooms_deleted} existing rooms")
    print(f"✅ Deleted {hotels_deleted} existing hotels")
    print()
    return hotels_deleted, rooms_deleted

# ============================================================================
# COMPREHENSIVE HOTEL DATA WITH RANDOMIZED FIELDS
# ============================================================================
DESTINATION_HOTELS = {
    "Amarapura": [
        {
            "name": "Royal Mingalar Hotel",
            "lat": 21.8943,
            "lng": 96.0624
        },
        {
            "name": "Pullman Mandalay Mingalar",
            "lat": 21.9317,
            "lng": 96.0967
        },
        {
            "name": "Hotel Sagaing",
            "lat": 21.8845,
            "lng": 95.9754
        },
        {
            "name": "Win Star Hotel",
            "lat": 21.9423,
            "lng": 96.0821
        },
        {
            "name": "AD1 Hotel",
            "lat": 21.9741,
            "lng": 96.0725
        }
    ],
    "Bagan": [
        {
            "name": "Aureum Palace Hotel & Resort",
            "lat": 21.1711,
            "lng": 94.8965
        },
        {
            "name": "The Hotel @ Tharabar Gate",
            "lat": 21.1747,
            "lng": 94.8622
        },
        {
            "name": "Heritage Bagan Hotel",
            "lat": 21.1895,
            "lng": 94.9145
        },
        {
            "name": "Bagan Thiripyitsaya Sanctuary Resort",
            "lat": 21.1664,
            "lng": 94.8541
        },
        {
            "name": "Ruby True Hotel",
            "lat": 21.1325,
            "lng": 94.8583
        }
    ],
    "Bago": [
        {
            "name": "Kanbawza Hinthar Hotel",
            "lat": 17.3347,
            "lng": 96.4851
        },
        {
            "name": "Famous Hotel Bago",
            "lat": 17.3025,
            "lng": 96.4442
        },
        {
            "name": "The Pegu Lodge",
            "lat": 17.3361,
            "lng": 96.4789
        },
        {
            "name": "KMA Shwe Pyi Bago Resort",
            "lat": 17.3912,
            "lng": 96.4355
        },
        {
            "name": "Jade Garden Hotel",
            "lat": 17.3328,
            "lng": 96.4812
        }
    ],
    "Bogale": [
        {
            "name": "Chatrium Hotel Royal Lake (Nearby hub)",
            "lat": 16.7954,
            "lng": 96.1631
        },
        {
            "name": "Pan Pacific Yangon (Nearby hub)",
            "lat": 16.7797,
            "lng": 96.1558
        },
        {
            "name": "Rose Garden Hotel (Nearby hub)",
            "lat": 16.7915,
            "lng": 96.1656
        },
        {
            "name": "Governor's Residence (Nearby hub)",
            "lat": 16.7910,
            "lng": 96.1415
        },
        {
            "name": "The Strand Yangon (Nearby hub)",
            "lat": 16.7698,
            "lng": 96.1627
        }
    ],
    "Dawei": [
        {
            "name": "Golden Guest Hotel",
            "lat": 14.0754,
            "lng": 98.1945
        },
        {
            "name": "Hotel Dawei",
            "lat": 14.0847,
            "lng": 98.1965
        },
        {
            "name": "Garden Hotel",
            "lat": 14.0722,
            "lng": 98.1894
        },
        {
            "name": "Diamond Crown Hotel",
            "lat": 14.0788,
            "lng": 98.2012
        },
        {
            "name": "Zayar Htet San Hotel",
            "lat": 14.0911,
            "lng": 98.1876
        }
    ],
    "Hakha": [
        {
            "name": "Grace Guest House",
            "lat": 22.6451,
            "lng": 93.6067
        },
        {
            "name": "Mountain View Hill Resort",
            "lat": 22.6394,
            "lng": 93.6112
        },
        {
            "name": "Pine Wood Villa",
            "lat": 22.6480,
            "lng": 93.6095
        },
        {
            "name": "Sky Palace Hotel (Hakha)",
            "lat": 22.6425,
            "lng": 93.6058
        },
        {
            "name": "Se Naing Family Guest House (Monica)",
            "lat": 22.6463,
            "lng": 93.6101
        }
    ],
    "Heho": [
        {
            "name": "Royal Airstrip Hotel",
            "lat": 20.7258,
            "lng": 96.7942
        },
        {
            "name": "Hotel Heho",
            "lat": 20.7314,
            "lng": 96.8015
        },
        {
            "name": "Inlay Palace Hotel",
            "lat": 20.6263,
            "lng": 96.9512
        },
        {
            "name": "Heho Valley Hotel",
            "lat": 20.7225,
            "lng": 96.7989
        },
        {
            "name": "Royal Airstrip Hotel by Phyu Zin",
            "lat": 20.7265,
            "lng": 96.7935
        }
    ],
    "Hinthada": [
        {
            "name": "Family Hotel",
            "lat": 17.6534,
            "lng": 95.4528
        },
        {
            "name": "Lucky Guest House",
            "lat": 17.6492,
            "lng": 95.4495
        },
        {
            "name": "Gandamar Hotel",
            "lat": 17.6488,
            "lng": 95.4512
        },
        {
            "name": "Shwe Mi Hotel",
            "lat": 17.6515,
            "lng": 95.4540
        },
        {
            "name": "Royal Pine Hill Resort",
            "lat": 17.6602,
            "lng": 95.4487
        }
    ],
    "Hmawbi": [
        {
            "name": "Pandora Motel",
            "lat": 17.1125,
            "lng": 96.0642
        },
        {
            "name": "Yaewaddy Motel",
            "lat": 17.1084,
            "lng": 96.0597
        },
        {
            "name": "Agga@9mile Hotel (Nearby)",
            "lat": 16.9012,
            "lng": 96.1245
        },
        {
            "name": "Royal Pavilion Hotel",
            "lat": 17.1150,
            "lng": 96.0685
        },
        {
            "name": "Spring Line Hotel",
            "lat": 17.1102,
            "lng": 96.0614
        }
    ],
    "Hpa-An": [
        {
            "name": "Keinnara Hpa-An (Hpa-An Lodge)",
            "lat": 16.8152,
            "lng": 97.6428
        },
        {
            "name": "Galaxy Motel Hpa-an",
            "lat": 16.8864,
            "lng": 97.6341
        },
        {
            "name": "Hotel Gabana",
            "lat": 16.8795,
            "lng": 97.6254
        },
        {
            "name": "Hpa-An River View Hotel",
            "lat": 16.8921,
            "lng": 97.6285
        },
        {
            "name": "Zwekapin Valley Resort & Spa",
            "lat": 16.8247,
            "lng": 97.6682
        }
    ],
    "Hsipaw": [
        {
            "name": "Tai House Resort",
            "lat": 22.6229,
            "lng": 97.2996
        },
        {
            "name": "Mr. Charles Hotel",
            "lat": 22.6171,
            "lng": 97.3024
        },
        {
            "name": "Hotel Thipaw",
            "lat": 22.6222,
            "lng": 97.3003
        },
        {
            "name": "Riverside @ Hsipaw Resort",
            "lat": 22.6155,
            "lng": 97.3051
        },
        {
            "name": "Red Dragon Hotel",
            "lat": 22.6198,
            "lng": 97.3015
        }
    ],
    "Kalaw": [
        {
            "name": "The Hotel-Kalaw Hill Lodge",
            "lat": 20.6186,
            "lng": 96.5458
        },
        {
            "name": "Pinn Pinn Kalaw Hotel",
            "lat": 20.6275,
            "lng": 96.5512
        },
        {
            "name": "Hillock Villa",
            "lat": 20.6241,
            "lng": 96.5495
        },
        {
            "name": "Kalaw Heritage Hotel",
            "lat": 20.6312,
            "lng": 96.5614
        },
        {
            "name": "Pine Breeze Hotel",
            "lat": 20.6358,
            "lng": 96.5642
        }
    ],
    "Kalay": [
        {
            "name": "Hotel Moe",
            "lat": 23.1945,
            "lng": 94.0256
        },
        {
            "name": "Majesty Hotel",
            "lat": 23.1972,
            "lng": 94.0211
        },
        {
            "name": "Hotel GBH Kale",
            "lat": 23.1815,
            "lng": 94.0428
        },
        {
            "name": "Taung Za Lat Hotel",
            "lat": 23.1958,
            "lng": 94.0234
        },
        {
            "name": "Ararat Hotel - Kalay",
            "lat": 23.1894,
            "lng": 94.0315
        }
    ],
    "Kawthaung": [
        {
            "name": "Victoria Cliff Hotel & Resort",
            "lat": 9.9925,
            "lng": 98.5412
        },
        {
            "name": "Mingalar Boutique Hotel",
            "lat": 9.9814,
            "lng": 98.5528
        },
        {
            "name": "Penguin Hotel",
            "lat": 9.9756,
            "lng": 98.5541
        },
        {
            "name": "Garden Hotel",
            "lat": 9.9789,
            "lng": 98.5515
        },
        {
            "name": "Grand Andaman Hotel",
            "lat": 9.9721,
            "lng": 98.5084
        }
    ],
    "Labutta": [
        {
            "name": "Grand Hotel Labutta",
            "lat": 16.1458,
            "lng": 94.7562
        },
        {
            "name": "Ayeyarwady Guest House",
            "lat": 16.1482,
            "lng": 94.7591
        },
        {
            "name": "Shwe Labutta Hotel",
            "lat": 16.1421,
            "lng": 94.7544
        },
        {
            "name": "Pyi Myo Thu Guest House",
            "lat": 16.1465,
            "lng": 94.7612
        },
        {
            "name": "River View Hotel",
            "lat": 16.1439,
            "lng": 94.7578
        }
    ],
    "Letpadan": [
        {
            "name": "Royal Pine Hill Resort",
            "lat": 17.7852,
            "lng": 95.7514
        },
        {
            "name": "Family Hotel",
            "lat": 17.7910,
            "lng": 95.7582
        },
        {
            "name": "Gandamar Hotel",
            "lat": 17.7885,
            "lng": 95.7550
        },
        {
            "name": "Shwe Mi Hotel",
            "lat": 17.7867,
            "lng": 95.7533
        },
        {
            "name": "Letpadan Guest House",
            "lat": 17.7898,
            "lng": 95.7561
        }
    ],
    "Loikaw": [
        {
            "name": "Loikaw Lodge by the Lake",
            "lat": 19.6824,
            "lng": 97.2156
        },
        {
            "name": "Keinnara Loikaw",
            "lat": 19.6645,
            "lng": 97.2082
        },
        {
            "name": "Kayah Land Hotel",
            "lat": 19.6738,
            "lng": 97.2115
        },
        {
            "name": "Gold Hotel",
            "lat": 19.6781,
            "lng": 97.2142
        },
        {
            "name": "Famous Hotel Loikaw",
            "lat": 19.6582,
            "lng": 97.2215
        }
    ],
    "Magway": [
        {
            "name": "Nan Htike Thu Hotel",
            "lat": 20.1465,
            "lng": 94.9284
        },
        {
            "name": "Royal Magway Hotel",
            "lat": 20.1522,
            "lng": 94.9315
        },
        {
            "name": "Kaung Kaung Hotel Magway",
            "lat": 20.1438,
            "lng": 94.9352
        },
        {
            "name": "Htein Htein Thar Hotel",
            "lat": 20.1412,
            "lng": 94.9256
        },
        {
            "name": "Royal Palace Hotel",
            "lat": 20.1498,
            "lng": 94.9387
        }
    ],
    "Mandalay": [
        {
            "name": "Mingalar Mandalay Hotel",
            "lat": 21.9482,
            "lng": 96.0914
        },
        {
            "name": "Hotel by the Red Canal",
            "lat": 22.0015,
            "lng": 96.1023
        },
        {
            "name": "Eastern Palace Hotel",
            "lat": 21.9856,
            "lng": 96.1245
        },
        {
            "name": "Bagan King Hotel",
            "lat": 21.9724,
            "lng": 96.0958
        },
        {
            "name": "Mandalay Hill Resort",
            "lat": 22.0084,
            "lng": 96.1112
        }
    ],
    "Mawlamyine": [
        {
            "name": "Cinderella Hotel",
            "lat": 16.4856,
            "lng": 97.6324
        },
        {
            "name": "Ngwe Moe Hotel",
            "lat": 16.4912,
            "lng": 97.6215
        },
        {
            "name": "Hotel Strand Mawlamyine",
            "lat": 16.4884,
            "lng": 97.6198
        },
        {
            "name": "Mawlamyine Hotel",
            "lat": 16.4752,
            "lng": 97.6385
        },
        {
            "name": "Attran Hotel",
            "lat": 16.4955,
            "lng": 97.6241
        }
    ],
    "Monywa": [
        {
            "name": "Win Unity Resort Hotel",
            "lat": 22.1054,
            "lng": 95.1228
        },
        {
            "name": "Chindwin Hotel",
            "lat": 22.1152,
            "lng": 95.1314
        },
        {
            "name": "Hotel Chindwin",
            "lat": 22.1128,
            "lng": 95.1325
        },
        {
            "name": "Jade Royal Hotel",
            "lat": 22.1089,
            "lng": 95.1292
        },
        {
            "name": "King & Queen Hotel",
            "lat": 22.1141,
            "lng": 95.1356
        }
    ],
    "Myaungmya": [
        {
            "name": "Myaungmya Hotel",
            "lat": 16.5982,
            "lng": 94.9214
        },
        {
            "name": "Shwe Hin Thar Guest House",
            "lat": 16.5956,
            "lng": 94.9245
        },
        {
            "name": "Golden Guest House",
            "lat": 16.6012,
            "lng": 94.9198
        },
        {
            "name": "Kyi Thar Guest House",
            "lat": 16.5975,
            "lng": 94.9231
        },
        {
            "name": "River View Guest House",
            "lat": 16.5994,
            "lng": 94.9222
        }
    ],
    "Myeik": [
        {
            "name": "Hotel Grand Jade",
            "lat": 12.4412,
            "lng": 98.6025
        },
        {
            "name": "Myeik Hotel",
            "lat": 12.4385,
            "lng": 98.5994
        },
        {
            "name": "White Pearl Guest House",
            "lat": 12.4456,
            "lng": 98.6052
        },
        {
            "name": "Sea View Condo Hotel",
            "lat": 12.4341,
            "lng": 98.5912
        },
        {
            "name": "Hotel Kyal Pyan",
            "lat": 12.4498,
            "lng": 98.6124
        }
    ],
    "Myitkyina": [
        {
            "name": "Palm Spring Resort",
            "lat": 25.3852,
            "lng": 97.3914
        },
        {
            "name": "Hotel Myitkyina",
            "lat": 25.3741,
            "lng": 97.4012
        },
        {
            "name": "Wun Tawp Garden Hotel",
            "lat": 25.3925,
            "lng": 97.3856
        },
        {
            "name": "The Grand Hotel",
            "lat": 25.3812,
            "lng": 97.3985
        },
        {
            "name": "Pansun Hotel",
            "lat": 25.3789,
            "lng": 97.4056
        }
    ],
    "Naypyidaw": [
        {
            "name": "Kempinski Hotel Nay Pyi Taw",
            "lat": 19.7412,
            "lng": 96.1154
        },
        {
            "name": "The Lake Garden Nay Pyi Taw - MGallery",
            "lat": 19.7256,
            "lng": 96.1285
        },
        {
            "name": "Hilton Nay Pyi Taw",
            "lat": 19.7345,
            "lng": 96.1092
        },
        {
            "name": "Parkroyal Nay Pyi Taw",
            "lat": 19.7485,
            "lng": 96.1214
        },
        {
            "name": "The Aureum Palace Hotel",
            "lat": 19.7552,
            "lng": 96.1328
        }
    ],
    "Nyaunglebin": [
        {
            "name": "Kanbawza Hinthar Hotel (Regional hub)",
            "lat": 17.3347,
            "lng": 96.4851
        },
        {
            "name": "KMA Shwe Pyi Bago Resort (Regional hub)",
            "lat": 17.3912,
            "lng": 96.4355
        },
        {
            "name": "Jade Garden Hotel (Regional hub)",
            "lat": 17.3328,
            "lng": 96.4812
        },
        {
            "name": "Famous Hotel Bago (Regional hub)",
            "lat": 17.3025,
            "lng": 96.4442
        },
        {
            "name": "Hotel Bago (Regional hub)",
            "lat": 17.3250,
            "lng": 96.4800
        }
    ],
    "Pakokku": [
        {
            "name": "Hotel Juno",
            "lat": 21.3411,
            "lng": 95.0782
        },
        {
            "name": "Thiri Yatanar Hotel",
            "lat": 21.3445,
            "lng": 95.0814
        },
        {
            "name": "Thu Kha Hotel",
            "lat": 21.3392,
            "lng": 95.0756
        },
        {
            "name": "Yatanar Sin Motel",
            "lat": 21.3428,
            "lng": 95.0795
        },
        {
            "name": "Taw Win Nan Hotel",
            "lat": 21.3456,
            "lng": 95.0831
        }
    ],
    "Pathein": [
        {
            "name": "The First Hotel",
            "lat": 16.7787,
            "lng": 94.7303
        },
        {
            "name": "Golden Princess Hotel",
            "lat": 16.7849,
            "lng": 94.7565
        },
        {
            "name": "Htike Myat San Hotel",
            "lat": 16.7812,
            "lng": 94.7356
        },
        {
            "name": "Shekinah Hotel",
            "lat": 16.7834,
            "lng": 94.7412
        },
        {
            "name": "Pathein Hotel",
            "lat": 16.7905,
            "lng": 94.7289
        }
    ],
    "Paungde": [
        {
            "name": "Lucky Dragon Hotel (Nearby hub)",
            "lat": 18.8214,
            "lng": 95.2235
        },
        {
            "name": "Mingalar Garden Resort (Nearby hub)",
            "lat": 18.8256,
            "lng": 95.2312
        },
        {
            "name": "Hotel Pyay (Nearby hub)",
            "lat": 18.8189,
            "lng": 95.2154
        },
        {
            "name": "Nawaday Hotel (Nearby hub)",
            "lat": 18.8142,
            "lng": 95.2105
        },
        {
            "name": "Golden Dragon Hotel (Nearby hub)",
            "lat": 18.8228,
            "lng": 95.2287
        }
    ],
    "Pyay": [
        {
            "name": "Lucky Dragon Hotel",
            "lat": 18.8234,
            "lng": 95.2212
        },
        {
            "name": "Mingalar Garden Resort",
            "lat": 18.8275,
            "lng": 95.2298
        },
        {
            "name": "Hotel Pyay",
            "lat": 18.8167,
            "lng": 95.2145
        },
        {
            "name": "Nawaday Hotel",
            "lat": 18.8125,
            "lng": 95.2112
        },
        {
            "name": "Smile Hotel",
            "lat": 18.8201,
            "lng": 95.2245
        }
    ],
    "Pyin Oo Lwin": [
        {
            "name": "The Hotel @ Tharabar Gate (Branch)",
            "lat": 22.0315,
            "lng": 96.4628
        },
        {
            "name": "Kandawgyi Hill Resort",
            "lat": 21.9942,
            "lng": 96.4715
        },
        {
            "name": "Hotel Pyin Oo Lwin",
            "lat": 22.0125,
            "lng": 96.4684
        },
        {
            "name": "Aureum Palace Hotel (Pyin Oo Lwin)",
            "lat": 22.0256,
            "lng": 96.4741
        },
        {
            "name": "Royal Parkview Hotel",
            "lat": 22.0345,
            "lng": 96.4612
        }
    ],
    "Sagaing": [
        {
            "name": "Hotel Sagaing",
            "lat": 21.8845,
            "lng": 95.9754
        },
        {
            "name": "Happy Hotel",
            "lat": 21.8912,
            "lng": 95.9685
        },
        {
            "name": "Shwe Pyi Thar Hotel",
            "lat": 21.8878,
            "lng": 95.9712
        },
        {
            "name": "Myaing Hay Wun Hotel",
            "lat": 21.8941,
            "lng": 95.9701
        },
        {
            "name": "Sagaing Hill Villa",
            "lat": 21.8905,
            "lng": 95.9624
        }
    ],
    "Shwebo": [
        {
            "name": "Shwebo Hotel",
            "lat": 22.5714,
            "lng": 95.6985
        },
        {
            "name": "Hotel Shwe Phyu",
            "lat": 22.5689,
            "lng": 95.7021
        },
        {
            "name": "Pyi Shwe Bo Guest House",
            "lat": 22.5742,
            "lng": 95.6954
        },
        {
            "name": "Winner Hotel",
            "lat": 22.5655,
            "lng": 95.7058
        },
        {
            "name": "Nan Htike Taw Win",
            "lat": 22.5721,
            "lng": 95.7011
        }
    ],
    "Shwegyin": [
        {
            "name": "Hinn Thar Guest House",
            "lat": 17.9152,
            "lng": 96.7784
        },
        {
            "name": "River View Guest House",
            "lat": 17.9201,
            "lng": 96.7825
        },
        {
            "name": "Shwegyin Motel",
            "lat": 17.9134,
            "lng": 96.7741
        },
        {
            "name": "Kyar Phyu Guest House",
            "lat": 17.9185,
            "lng": 96.7798
        },
        {
            "name": "Green Land Guest House",
            "lat": 17.9112,
            "lng": 96.7715
        }
    ],
    "Sittwe": [
        {
            "name": "Hotel Memory",
            "lat": 20.1441,
            "lng": 92.8945
        },
        {
            "name": "Noble Hotel",
            "lat": 20.1385,
            "lng": 92.9012
        },
        {
            "name": "Shwe Thazin Hotel",
            "lat": 20.1412,
            "lng": 92.8984
        },
        {
            "name": "Kissi Panadi Hotel",
            "lat": 20.1478,
            "lng": 92.8911
        },
        {
            "name": "Riverview Hotel",
            "lat": 20.1356,
            "lng": 92.9054
        }
    ],
    "Tachileik": [
        {
            "name": "1G1 Hotel",
            "lat": 20.4452,
            "lng": 99.8814
        },
        {
            "name": "Tachileik Hotel",
            "lat": 20.4412,
            "lng": 99.8856
        },
        {
            "name": "Hotel Platinum",
            "lat": 20.4485,
            "lng": 99.8789
        },
        {
            "name": "Golden Cherry Hotel",
            "lat": 20.4431,
            "lng": 99.8825
        },
        {
            "name": "Mekong River Hotel",
            "lat": 20.4501,
            "lng": 99.8892
        }
    ],
    "Taunggyi": [
        {
            "name": "Hotel Taunggyi",
            "lat": 20.7854,
            "lng": 97.0341
        },
        {
            "name": "Mountain Star Hotel",
            "lat": 20.7912,
            "lng": 97.0385
        },
        {
            "name": "KMA Taunggyi Hotel",
            "lat": 20.7821,
            "lng": 97.0312
        },
        {
            "name": "Riddim Hostel & Hotel",
            "lat": 20.7885,
            "lng": 97.0364
        },
        {
            "name": "True Treasure Hotel",
            "lat": 20.7942,
            "lng": 97.0401
        }
    ],
    "Taungoo": [
        {
            "name": "KMA Kaytumadi Hotel",
            "lat": 18.9324,
            "lng": 96.4358
        },
        {
            "name": "Global Grace Hotel",
            "lat": 18.9412,
            "lng": 96.4425
        },
        {
            "name": "Myanmar Beauty Hotel 1 (Downtown)",
            "lat": 18.9385,
            "lng": 96.4312
        },
        {
            "name": "Pathi Hotel",
            "lat": 18.9456,
            "lng": 96.4489
        },
        {
            "name": "Hotel Amazing Kaytu",
            "lat": 18.9298,
            "lng": 96.4374
        }
    ],
    "Thandwe": [
        {
            "name": "Ngapali Paradise Hotel",
            "lat": 18.4084,
            "lng": 94.3326
        },
        {
            "name": "Amata Resort & Spa, Ngapali Beach",
            "lat": 18.3874,
            "lng": 94.3378
        },
        {
            "name": "Memento Resort",
            "lat": 18.4071,
            "lng": 94.3337
        },
        {
            "name": "Blue Oceanic Bay",
            "lat": 18.4421,
            "lng": 94.3186
        },
        {
            "name": "Seasons Hotels and Resorts-Ngapali",
            "lat": 18.4189,
            "lng": 94.3299
        }
    ],
    "Wakema": [
        {
            "name": "Aung Kaday Hotel",
            "lat": 16.6022,
            "lng": 95.1825
        },
        {
            "name": "Shwe Hin Thar Guest House",
            "lat": 16.6054,
            "lng": 95.1856
        },
        {
            "name": "Wakema River View Hotel",
            "lat": 16.6010,
            "lng": 95.1802
        },
        {
            "name": "Golden Guest House",
            "lat": 16.6038,
            "lng": 95.1841
        },
        {
            "name": "Family Inn Wakema",
            "lat": 16.5985,
            "lng": 95.1795
        }
    ],
    "Yangon": [
        {
            "name": "The Strand Hotel Yangon",
            "lat": 16.7698,
            "lng": 96.1627
        },
        {
            "name": "LOTTE HOTEL YANGON",
            "lat": 16.8324,
            "lng": 96.1415
        },
        {
            "name": "Pan Pacific Yangon",
            "lat": 16.7797,
            "lng": 96.1558
        },
        {
            "name": "Hotel G Yangon",
            "lat": 16.7825,
            "lng": 96.1592
        },
        {
            "name": "Grand Laurel Hotel",
            "lat": 16.7764,
            "lng": 96.1645
        }
    ]
}

# ============================================================================
# UTILITY FUNCTIONS FOR RANDOM DATA GENERATION
# ============================================================================
def get_random_category():
    """Return a random category weighted towards medium and budget"""
    categories = ['budget', 'budget', 'medium', 'medium', 'medium', 'luxury', 'luxury', 'high']
    return random.choice(categories)

def get_random_phone():
    """Generate a random Myanmar phone number"""
    prefix = random.choice(['09', '+95 9'])
    if prefix == '09':
        return f"09{random.randint(10000000, 99999999)}"
    else:
        return f"+95 9 {random.randint(10000000, 99999999)}"

def get_random_address(city_name):
    """Generate a random address for the city"""
    streets = ['Main Road', 'Strand Road', 'Bogyoke Road', 'University Avenue', 
               'Market Street', 'Pagoda Road', 'River Front', 'Downtown',
               'City Center', 'Airport Road', 'Hill Station Road', 'Beach Road']
    return f"{random.choice(streets)}, {city_name}"

def get_random_amenities(category):
    """Generate amenities based on category"""
    base_amenities = ['wifi']
    
    if category in ['luxury', 'high']:
        all_amenities = ['wifi', 'pool', 'spa', 'restaurant', 'gym', 'room_service', 
                         'minibar', 'concierge', 'business_center', 'parking', 
                         'breakfast', 'bar', 'massage', 'air_conditioning', 'laundry']
        count = random.randint(8, 14)
    elif category == 'medium':
        all_amenities = ['wifi', 'restaurant', 'parking', 'breakfast', 'air_conditioning', 
                         'room_service', 'laundry', 'tv', 'gym', 'bar']
        count = random.randint(5, 9)
    else:  # budget
        all_amenities = ['wifi', 'air_conditioning', 'breakfast', 'parking', 'tv']
        count = random.randint(3, 5)
    
    return random.sample(all_amenities, min(count, len(all_amenities)))

def get_random_price(category):
    """Generate random price in MMK based on category"""
    ranges = {
        'budget': (20000, 50000),
        'medium': (50000, 120000),
        'luxury': (120000, 250000),
        'high': (250000, 500000)
    }
    min_price, max_price = ranges.get(category, (40000, 100000))
    return random.randint(min_price, max_price)

def get_random_rating(category):
    """Generate random rating based on category"""
    ranges = {
        'budget': (3.0, 4.0),
        'medium': (3.5, 4.3),
        'luxury': (4.0, 4.7),
        'high': (4.2, 4.9)
    }
    min_rating, max_rating = ranges.get(category, (3.5, 4.3))
    return round(random.uniform(min_rating, max_rating), 1)

def get_random_review_count():
    """Generate random review count"""
    return random.randint(50, 500)

def get_random_description(name, city_name, category):
    """Generate a random description"""
    templates = [
        f"{name} offers comfortable accommodation with excellent service in {city_name}.",
        f"Experience the best of {city_name} at {name}, known for its hospitality.",
        f"{name} is conveniently located in the heart of {city_name} with modern amenities.",
        f"Stay at {name} for a memorable experience in {city_name}.",
        f"{name} provides top-notch amenities and friendly service in {city_name}.",
        f"Discover the charm of {city_name} while staying at {name}.",
        f"{name} features {'luxurious' if category in ['luxury','high'] else 'comfortable'} rooms and excellent facilities."
    ]
    return random.choice(templates)

def get_random_note(name, city_name, category):
    """Generate a random note"""
    notes = [
        f"Popular hotel in {city_name}",
        f"Well-reviewed by travelers",
        f"Great location for exploring {city_name}",
        f"Known for excellent service",
        f"Comfortable stay in {city_name}",
        f"Recommended for business and leisure",
        f"Good value for money"
    ]
    if category in ['luxury', 'high']:
        notes.append(f"Premium {category} hotel in {city_name}")
    return random.choice(notes)

def get_check_in_time():
    """Get random check-in time"""
    hours = random.choice([14, 15])
    return time(hours, 0)

def get_check_out_time():
    """Get random check-out time"""
    hours = random.choice([11, 12])
    return time(hours, 0)

# ============================================================================
# ROOM CREATION FUNCTION
# ============================================================================
def create_rooms_for_hotel(hotel):
    """Create rooms for a hotel with random configuration"""
    try:
        room_types = list(RoomType.objects.all())
        if not room_types:
            print("⚠ No room types found. Skipping room creation.")
            return 0
        
        # Random number of rooms: between 10 and 50
        num_rooms = random.randint(10, 50)
        rooms_created = 0
        
        for i in range(1, num_rooms + 1):
            # Random room type
            room_type = random.choice(room_types)
            
            # Generate room number
            floor = random.randint(1, 5)
            room_number = f"{floor}{i:02d}"
            
            # Random features
            has_window = random.choice([True, False])
            has_balcony = random.choice([True, False]) if hotel.category in ['luxury', 'high'] else random.choice([True, False, False])
            
            # Random bed type
            bed_types = ['King', 'Queen', 'Double', 'Twin', 'Single']
            bed_type = random.choice(bed_types)
            
            # Square feet based on room type
            sqft_ranges = {
                'SINGLE': (180, 250),
                'DOUBLE': (250, 350),
                'TRIPLE': (350, 450),
                'SUITE': (450, 800)
            }
            min_sqft, max_sqft = sqft_ranges.get(room_type.code, (200, 400))
            square_feet = random.randint(min_sqft, max_sqft)
            
            # Custom price (20% chance of having custom price)
            custom_price = None
            if random.random() < 0.2:
                custom_price = get_random_price(hotel.category) * random.uniform(0.8, 1.5)
                custom_price = int(custom_price)
            
            # Room features
            room_features = get_random_amenities(hotel.category)[:3]
            
            # Create the room
            room = Room.objects.create(
                hotel=hotel,
                room_type=room_type,
                room_number=room_number,
                floor=floor,
                custom_price=custom_price,
                features=room_features,
                is_active=True,
                needs_maintenance=False,
                bed_type=bed_type,
                has_window=has_window,
                has_balcony=has_balcony,
                square_feet=square_feet
            )
            rooms_created += 1
        
        return rooms_created
        
    except Exception as e:
        print(f"      ❌ Error creating rooms: {str(e)}")
        return 0

# ============================================================================
# MAIN HOTEL ADDITION FUNCTION
# ============================================================================
def add_real_hotels():
    """Add all real hotels to the database with room support"""
    
    print("=" * 70)
    print("ADDING REAL HOTELS FOR ALL DESTINATIONS WITH ROOM SUPPORT")
    print("=" * 70)
    
    total_hotels_added = 0
    total_rooms_created = 0
    destinations_processed = 0
    destinations_with_hotels = 0
    
    # Get all active destinations
    all_destinations = Destination.objects.filter(is_active=True)
    print(f"Found {all_destinations.count()} destinations in database\n")
    
    for destination in all_destinations:
        dest_name = destination.name
        
        # Find matching hotel data
        hotel_data = DESTINATION_HOTELS.get(dest_name)
        
        if not hotel_data:
            print(f"⚠ No hotel data for: {dest_name}")
            continue
        
        print(f"📍 {dest_name} ({destination.region}):")
        hotels_added = 0
        rooms_created_for_dest = 0
        
        for hotel_info in hotel_data:
            hotel_name = hotel_info['name']
            lat = hotel_info['lat']
            lng = hotel_info['lng']
            
            # Generate random data
            category = get_random_category()
            phone = get_random_phone()
            address = get_random_address(dest_name)
            amenities = get_random_amenities(category)
            price_per_night = get_random_price(category)
            rating = get_random_rating(category)
            review_count = get_random_review_count()
            description = get_random_description(hotel_name, dest_name, category)
            note = get_random_note(hotel_name, dest_name, category)
            check_in = get_check_in_time()
            check_out = get_check_out_time()
            
            # Determine if it's a real hotel (90% chance)
            is_real = random.random() < 0.9
            
            try:
                # Create hotel
                hotel = Hotel.objects.create(
                    name=hotel_name,
                    destination=destination,
                    address=address,
                    phone_number=phone,
                    category=category,
                    price_per_night=Decimal(str(price_per_night)),
                    rating=Decimal(str(rating)),
                    review_count=review_count,
                    amenities=amenities,
                    is_active=True,
                    is_real_hotel=is_real,
                    latitude=Decimal(str(lat)),
                    longitude=Decimal(str(lng)),
                    description=description,
                    website=f"http://www.{hotel_name.lower().replace(' ', '').replace('&', '').replace('.', '').replace('-', '')}.com",
                    check_in_time=check_in,
                    check_out_time=check_out
                )
                
                print(f"   ✅ Added: {hotel_name}")
                print(f"      Category: {category}, Price: {hotel.price_in_mmk()}, Rating: {hotel.rating}")
                
                # Create rooms for this hotel
                rooms_created = create_rooms_for_hotel(hotel)
                rooms_created_for_dest += rooms_created
                print(f"      🏨 Created {rooms_created} rooms")
                
                hotels_added += 1
                total_hotels_added += 1
                total_rooms_created += rooms_created
                
            except Exception as e:
                print(f"   ❌ Error adding {hotel_name}: {str(e)}")
                continue
        
        if hotels_added > 0:
            print(f"   📊 Added {hotels_added} hotels with {rooms_created_for_dest} rooms to {dest_name}")
            destinations_with_hotels += 1
        else:
            print(f"   ℹ No hotels added to {dest_name}")
        
        destinations_processed += 1
        print()
    
    return total_hotels_added, total_rooms_created, destinations_processed, destinations_with_hotels

# ============================================================================
# VERIFICATION FUNCTION
# ============================================================================
def verify_hotels_and_rooms():
    """Verify that hotels and rooms were added correctly"""
    
    print("\n" + "=" * 70)
    print("VERIFYING HOTEL AND ROOM ADDITION")
    print("=" * 70)
    
    total_hotels = Hotel.objects.count()
    total_rooms = Room.objects.count()
    hotels_with_coords = Hotel.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    
    print(f"\n✅ Total hotels in database: {total_hotels}")
    print(f"✅ Total rooms in database: {total_rooms}")
    print(f"✅ Hotels with coordinates: {hotels_with_coords.count()}")
    
    # Calculate average rooms per hotel
    if total_hotels > 0:
        avg_rooms = total_rooms / total_hotels
        print(f"✅ Average rooms per hotel: {avg_rooms:.1f}")
    
    # Count by category
    print(f"\n📊 Hotels by category:")
    categories = Hotel.objects.values_list('category', flat=True).distinct()
    for category in categories:
        if category:
            count = Hotel.objects.filter(category=category).count()
            rooms_count = Room.objects.filter(hotel__category=category).count()
            print(f"   {category.capitalize()}: {count} hotels, {rooms_count} rooms")
    
    # Count by destination
    print(f"\n📊 Top 10 destinations by hotels:")
    from django.db.models import Count
    dest_counts = Hotel.objects.values('destination__name').annotate(
        hotel_count=Count('id'),
        room_count=Count('rooms')
    ).order_by('-hotel_count')[:10]
    
    for item in dest_counts:
        print(f"   {item['destination__name']}: {item['hotel_count']} hotels, {item['room_count']} rooms")
    
    # Sample check
    print(f"\n🔍 Sample hotels with rooms:")
    sample_hotels = Hotel.objects.order_by('?')[:3]
    for hotel in sample_hotels:
        room_count = Room.objects.filter(hotel=hotel).count()
        print(f"  📍 {hotel.name} in {hotel.destination.name}")
        print(f"     Price: {hotel.price_in_mmk()}, Rating: {hotel.rating}")
        print(f"     Rooms: {room_count} rooms")
        print(f"     Location: {hotel.latitude:.4f}, {hotel.longitude:.4f}")
        print()

# ============================================================================
# MAIN FUNCTION
# ============================================================================
def main():
    """Main function"""
    
    print("\n" + "=" * 70)
    print("MYANMAR TRAVEL PLANNER - HOTEL DATABASE POPULATION")
    print("WITH ROOM SUPPORT")
    print("=" * 70)
    
    # Step 1: Delete all existing hotels and rooms
    deleted_hotels, deleted_rooms = delete_all_hotels_and_rooms()
    
    # Step 2: Verify RoomTypes exist
    room_types = RoomType.objects.all()
    if not room_types.exists():
        print("\n⚠ No RoomTypes found! Please run the room type creation script first.")
        print("Run this in Django shell:")
        print("""
from planner.models_room import RoomType
room_types = [
    {'name': 'Single', 'code': 'SINGLE', 'max_occupancy': 1, 'base_price_multiplier': 0.8},
    {'name': 'Double', 'code': 'DOUBLE', 'max_occupancy': 2, 'base_price_multiplier': 1.0},
    {'name': 'Triple', 'code': 'TRIPLE', 'max_occupancy': 3, 'base_price_multiplier': 1.3},
    {'name': 'Suite', 'code': 'SUITE', 'max_occupancy': 4, 'base_price_multiplier': 2.0},
]
for rt in room_types:
    RoomType.objects.get_or_create(code=rt['code'], defaults=rt)
""")
        return
    
    print(f"\n✅ Found {room_types.count()} RoomTypes:")
    for rt in room_types:
        print(f"   - {rt.name} (Code: {rt.code}, Max: {rt.max_occupancy}, Multiplier: {rt.base_price_multiplier})")
    
    # Step 3: Add all real hotels with rooms
    added_hotels, added_rooms, dest_processed, dest_with_hotels = add_real_hotels()
    
    # Step 4: Verify the addition
    verify_hotels_and_rooms()
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ HOTEL POPULATION COMPLETE!")
    print("=" * 70)
    print(f"Deleted existing hotels: {deleted_hotels}")
    print(f"Deleted existing rooms: {deleted_rooms}")
    print(f"Added new hotels: {added_hotels}")
    print(f"Added new rooms: {added_rooms}")
    print(f"Destinations processed: {dest_processed}")
    print(f"Destinations with hotels: {dest_with_hotels}")
    print(f"Total hotels in database: {Hotel.objects.count()}")
    print(f"Total rooms in database: {Room.objects.count()}")
    
    if added_rooms > 0:
        print("\n🎉 ALL REAL HOTELS WITH ROOMS HAVE BEEN ADDED!")
        print("\nYour system now has comprehensive hotel data with room support.")
        print("Users can now select individual rooms for booking!")

if __name__ == '__main__':
    main()