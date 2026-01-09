"""
Simple Weather Service for Myanmar Travel Planner
If API key is not working, it will use mock data
"""

import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
import random

class WeatherService:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENWEATHER_API_KEY', '')
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_weather_by_city(self, city_name, country_code='MM'):
        """Get current weather for a city"""
        if not self.api_key:
            return self._get_mock_weather(city_name)
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': f"{city_name},{country_code}",
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'en'
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get('cod') == 200:
                return {
                    'city': data.get('name', city_name),
                    'temperature': round(data['main']['temp']),
                    'description': data['weather'][0]['description'].title(),
                    'icon': data['weather'][0]['icon'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'is_mock': False
                }
            else:
                print(f"Weather API error for {city_name}: {data.get('message')}")
                return self._get_mock_weather(city_name)
                
        except Exception as e:
            print(f"Error fetching weather for {city_name}: {e}")
            return self._get_mock_weather(city_name)
    
    def get_weather_forecast(self, city_name, start_date, end_date, country_code='MM'):
        """Get weather forecast for multiple days"""
        # Always use mock data for forecast to simplify
        return self._get_mock_forecast(city_name, start_date, end_date)
    
    def _get_mock_weather(self, city_name):
        """Generate mock weather data for Myanmar"""
        conditions = [
            {'desc': 'Sunny', 'icon': '01d', 'temp_range': (28, 35)},
            {'desc': 'Partly Cloudy', 'icon': '02d', 'temp_range': (26, 32)},
            {'desc': 'Cloudy', 'icon': '03d', 'temp_range': (24, 30)},
            {'desc': 'Light Rain', 'icon': '10d', 'temp_range': (23, 28)},
        ]
        
        condition = random.choice(conditions)
        temp = random.randint(condition['temp_range'][0], condition['temp_range'][1])
        
        return {
            'city': city_name,
            'temperature': temp,
            'description': condition['desc'],
            'icon': condition['icon'],
            'humidity': random.randint(50, 80),
            'wind_speed': round(random.uniform(1.0, 5.0), 1),
            'is_mock': True
        }
    
    def _get_mock_forecast(self, city_name, start_date, end_date):
        """Generate mock forecast data for Myanmar"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            days = (end - start).days + 1
        except:
            # Default to 3 days if date parsing fails
            start = datetime.now()
            days = 3
        
        forecasts = {}
        current_date = start
        
        # Myanmar weather patterns
        weather_patterns = [
            {'desc': 'Sunny', 'icon': '01d', 'temp_range': (28, 35)},
            {'desc': 'Partly Cloudy', 'icon': '02d', 'temp_range': (26, 32)},
            {'desc': 'Cloudy', 'icon': '03d', 'temp_range': (24, 30)},
            {'desc': 'Light Rain', 'icon': '10d', 'temp_range': (23, 28)},
        ]
        
        for i in range(days):
            date_str = current_date.strftime('%Y-%m-%d')
            day_name = current_date.strftime('%A')
            
            # Select weather pattern
            pattern = random.choice(weather_patterns)
            base_temp = random.randint(pattern['temp_range'][0], pattern['temp_range'][1])
            
            # Generate hourly forecasts
            hourly_forecasts = []
            for hour in [8, 12, 16, 20]:
                hour_temp = base_temp + random.randint(-2, 2)
                hourly_forecasts.append({
                    'time': f"{hour:02d}:00",
                    'temperature': hour_temp,
                    'description': pattern['desc'],
                    'icon': pattern['icon'],
                    'feels_like': hour_temp + random.randint(-1, 1),
                    'humidity': random.randint(50, 80),
                    'wind_speed': round(random.uniform(1.0, 5.0), 1),
                })
            
            # Calculate min/max temps
            temps = [h['temperature'] for h in hourly_forecasts]
            min_temp = min(temps)
            max_temp = max(temps)
            
            # Use noon as daily summary
            noon_forecast = hourly_forecasts[1] if len(hourly_forecasts) > 1 else hourly_forecasts[0]
            
            forecasts[date_str] = {
                'date': date_str,
                'day_name': day_name,
                'daily_summary': {
                    'temperature': noon_forecast['temperature'],
                    'description': noon_forecast['description'],
                    'icon': noon_forecast['icon'],
                },
                'hourly_forecasts': hourly_forecasts,
                'min_temp': min_temp,
                'max_temp': max_temp,
                'is_mock': True,
            }
            
            current_date += timedelta(days=1)
        
        return forecasts


# Create a singleton instance
weather_service = WeatherService()