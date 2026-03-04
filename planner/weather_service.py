import requests
from django.conf import settings
import random
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENWEATHER_API_KEY', '')
        self.base_url = "https://api.openweathermap.org/data/2.5"

    # =========================================================
    # ✅ COORDINATE-BASED WEATHER (PRIMARY – USE THIS)
    # =========================================================
    def get_weather_by_coords(self, latitude, longitude, city_name=None):
        """Get current weather using latitude & longitude (MOST RELIABLE)"""
        if not self.api_key:
            logger.warning("OpenWeather API key not configured. Using mock data.")
            return self.get_mock_weather(city_name or "Unknown")

        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'en'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                return {
                    'city': city_name or data.get('name', 'Unknown'),
                    'temperature': round(data['main']['temp'], 1),
                    'feels_like': round(data['main']['feels_like'], 1),
                    'description': data['weather'][0]['description'].capitalize(),
                    'icon': data['weather'][0]['icon'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': round(data['wind']['speed'] * 3.6, 1),
                    'pressure': data['main']['pressure'],
                    'visibility': data.get('visibility', 10000) / 1000,
                    'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                    'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
                    'is_real': True,
                    'is_mock': False,
                    'api_response': 'success'
                }

            logger.warning("Coordinate weather API error – falling back to mock")
            return self.get_mock_weather(city_name or "Unknown", is_fallback=True)

        except Exception as e:
            logger.error(f"Weather API (coords) error: {e}")
            return self.get_mock_weather(city_name or "Unknown", is_fallback=True)

    # =========================================================
    # CITY-BASED WEATHER (FALLBACK ONLY)
    # =========================================================
    def get_weather_by_city(self, city_name, country_code='MM'):
        """Get current weather for a city (less reliable for Myanmar)"""
        if not self.api_key:
            logger.warning("OpenWeather API key not configured. Using mock data.")
            return self.get_mock_weather(city_name)

        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': f"{city_name},{country_code}",
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'en'
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                return {
                    'city': city_name,
                    'temperature': round(data['main']['temp'], 1),
                    'feels_like': round(data['main']['feels_like'], 1),
                    'description': data['weather'][0]['description'].capitalize(),
                    'icon': data['weather'][0]['icon'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': round(data['wind']['speed'] * 3.6, 1),
                    'pressure': data['main']['pressure'],
                    'visibility': data.get('visibility', 10000) / 1000,
                    'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                    'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
                    'is_real': True,
                    'is_mock': False,
                    'api_response': 'success'
                }

            return self.get_mock_weather(city_name, is_fallback=True)

        except Exception as e:
            logger.error(f"Weather API (city) error: {e}")
            return self.get_mock_weather(city_name, is_fallback=True)

    # =========================================================
    # MOCK WEATHER (SAFE FALLBACK)
    # =========================================================
    def get_mock_weather(self, city_name, is_fallback=False):
        """Generate realistic mock weather data"""
        city_temps = {
            'yangon': (25, 35),
            'mandalay': (20, 37),
            'bagan': (22, 38),
            'inle': (15, 28),
            'naypyidaw': (23, 36),
        }

        city_lower = city_name.lower()
        temp_range = city_temps.get(city_lower, (25, 35))

        conditions = ['Clear', 'Partly Cloudy', 'Cloudy', 'Light Rain', 'Sunny']
        condition = random.choice(conditions)

        icon_map = {
            'Clear': '01d',
            'Sunny': '01d',
            'Partly Cloudy': '02d',
            'Cloudy': '03d',
            'Light Rain': '10d'
        }

        return {
            'city': city_name,
            'temperature': random.randint(*temp_range),
            'description': condition,
            'icon': icon_map.get(condition, '01d'),
            'humidity': random.randint(50, 85),
            'wind_speed': round(random.uniform(1.0, 5.0), 1),
            'is_real': False,
            'is_mock': True,
            'api_response': 'fallback' if is_fallback else 'mock_only'
        }


# ✅ GLOBAL INSTANCE (IMPORTANT)
weather_service = WeatherService()
