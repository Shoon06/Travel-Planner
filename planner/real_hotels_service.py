# C:\Users\ASUS\MyanmarTravelPlanner\planner\real_hotels_service.py
# MINIMAL VERSION - No external dependencies

import random

class RealHotelsService:
    @staticmethod
    def search_nearby_hotels(latitude, longitude, radius=5000):
        sample_hotels = []
        for i in range(5):
            sample_hotels.append({
                'id': f"real_{i+1}",
                'name': f"Sample Hotel {i+1}",
                'address': f"Near location, Myanmar",
                'latitude': latitude + random.uniform(-0.01, 0.01),
                'longitude': longitude + random.uniform(-0.01, 0.01),
                'price': random.choice([35000, 45000, 60000, 90000, 120000, 200000]),
                'rating': round(random.uniform(3.5, 4.8), 1),
                'category': random.choice(['budget', 'medium', 'luxury']),
                'amenities': random.sample(['wifi', 'parking', 'restaurant', 'pool', 'spa', 'gym', 'breakfast'], 3),
                'source': 'Sample',
                'is_real': True,
                'can_book': True,
            })
        return sample_hotels
    
    @staticmethod
    def geocode_location(query):
        default_locations = {
            'yangon': {'latitude': 16.8409, 'longitude': 96.1735, 'display_name': 'Yangon, Myanmar'},
            'mandalay': {'latitude': 21.9750, 'longitude': 96.0833, 'display_name': 'Mandalay, Myanmar'},
            'bagan': {'latitude': 21.1722, 'longitude': 94.8603, 'display_name': 'Bagan, Myanmar'},
            'inle lake': {'latitude': 20.5500, 'longitude': 96.9167, 'display_name': 'Inle Lake, Myanmar'},
        }
        
        query_lower = query.lower()
        for location, coords in default_locations.items():
            if location in query_lower:
                return coords
        
        return default_locations['yangon']

real_hotels_service = RealHotelsService()