import googlemaps
from django.conf import settings

class GoogleMapsService:
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        if self.api_key and self.api_key != 'YOUR_API_KEY_HERE':
            self.client = googlemaps.Client(key=self.api_key)
        else:
            self.client = None
            print("WARNING: Google Maps API key not configured or using default")
    
    def geocode_address(self, address):
        """Convert address to coordinates"""
        if not self.client:
            return None
        
        try:
            geocode_result = self.client.geocode(address)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                return {
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'formatted_address': geocode_result[0]['formatted_address']
                }
        except Exception as e:
            print(f"Geocoding error: {e}")
        return None
    
    def search_nearby_hotels(self, latitude, longitude, radius=5000):
        """Search for hotels near a location using Places API"""
        if not self.client:
            print("Google Maps client not initialized")
            return []
        
        try:
            places_result = self.client.places_nearby(
                location=(latitude, longitude),
                radius=radius,
                type='lodging',
                language='en'
            )
            
            hotels = []
            for place in places_result.get('results', []):
                # Get estimated price based on price level
                price_level = place.get('price_level', 2)  # 0-4 scale
                estimated_price = {
                    0: 30000,  # Very cheap
                    1: 50000,  # Cheap
                    2: 80000,  # Moderate
                    3: 150000, # Expensive
                    4: 300000  # Very expensive
                }.get(price_level, 80000)
                
                hotel = {
                    'name': place.get('name', ''),
                    'place_id': place.get('place_id', ''),
                    'address': place.get('vicinity', ''),
                    'latitude': place['geometry']['location']['lat'],
                    'longitude': place['geometry']['location']['lng'],
                    'rating': place.get('rating', 4.0),
                    'user_ratings_total': place.get('user_ratings_total', 0),
                    'price': estimated_price,
                    'price_level': price_level,
                    'types': place.get('types', [])
                }
                hotels.append(hotel)
            
            return hotels[:15]  # Limit to 15 results
        except Exception as e:
            print(f"Places API error: {e}")
            # Return sample data for testing
            return self.get_sample_hotels(latitude, longitude)
    
    def get_sample_hotels(self, latitude, longitude):
        """Return sample hotels for testing when API fails"""
        sample_hotels = [
            {
                'name': 'Test Hotel 1',
                'address': f'Near location',
                'latitude': latitude + 0.001,
                'longitude': longitude + 0.001,
                'rating': 4.2,
                'price': 50000,
                'price_level': 2
            },
            {
                'name': 'Test Hotel 2',
                'address': f'City center',
                'latitude': latitude - 0.001,
                'longitude': longitude - 0.001,
                'rating': 3.8,
                'price': 30000,
                'price_level': 1
            }
        ]
        return sample_hotels
    
    def get_place_details(self, place_id):
        """Get detailed information about a place"""
        if not self.client:
            return None
        
        try:
            place_details = self.client.place(
                place_id=place_id,
                fields=['name', 'formatted_address', 'geometry', 
                       'rating', 'user_ratings_total', 'price_level', 
                       'website', 'formatted_phone_number']
            )
            return place_details.get('result', {})
        except Exception as e:
            print(f"Place details error: {e}")
            return None

maps_service = GoogleMapsService()