import requests
from django.conf import settings
import random
from datetime import datetime, timedelta

class WeatherService:
    def __init__(self):
        self.api_key = getattr(settings, 'OPENWEATHER_API_KEY', '')
    
    def get_weather_by_city(self, city_name, country_code='MM'):
        """Get current weather for a city"""
        if not self.api_key:
            return self.get_mock_weather(city_name)
        
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name},{country_code}&appid={self.api_key}&units=metric"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get('cod') == 200:
                return {
                    'city': city_name,
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'is_mock': False
                }
        except Exception as e:
            print(f"Weather API error: {e}")
        
        # Fall back to mock data
        return self.get_mock_weather(city_name)
    
    def get_weather_forecast(self, city_name, start_date_str, end_date_str):
        """Get weather forecast for a date range"""
        # For now, return mock forecast
        return self.get_mock_forecast(start_date_str, end_date_str, city_name)
    
    def get_mock_weather(self, city_name):
        """Generate realistic mock weather data for Myanmar cities"""
        # Average temperatures for Myanmar cities (in Celsius)
        city_temps = {
            'yangon': (25, 35),
            'mandalay': (20, 37),
            'bagan': (22, 38),
            'inle': (15, 28),
            'naypyidaw': (23, 36),
            'pyin oo lwin': (15, 25),
            'ngapali': (24, 32),
            'hsipaw': (18, 30),
            'kyaiktiyo': (20, 30),
            'kalawe': (22, 33)
        }
        
        # Find matching city
        city_lower = city_name.lower()
        temp_range = (25, 35)  # Default range
        
        for city_key, city_temp in city_temps.items():
            if city_key in city_lower:
                temp_range = city_temp
                break
        
        # Generate weather
        conditions = ['Clear', 'Partly Cloudy', 'Cloudy', 'Light Rain', 'Sunny']
        condition = random.choice(conditions)
        
        # Assign appropriate icon
        icon_map = {
            'Clear': '01d',
            'Sunny': '01d',
            'Partly Cloudy': '02d',
            'Cloudy': '03d',
            'Light Rain': '10d'
        }
        
        return {
            'city': city_name,
            'temperature': random.randint(temp_range[0], temp_range[1]),
            'description': condition,
            'icon': icon_map.get(condition, '01d'),
            'humidity': random.randint(50, 85),
            'wind_speed': round(random.uniform(1.0, 5.0), 1),
            'is_mock': True
        }
    
    def get_mock_forecast(self, start_date_str, end_date_str, city_name):
        """Generate mock weather forecast"""
        from datetime import datetime, timedelta
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        days = (end_date - start_date).days + 1
        forecasts = {}
        
        # Get base weather for the city
        base_weather = self.get_mock_weather(city_name)
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            day_name = current_date.strftime('%A')
            
            # Vary temperature slightly each day
            daily_temp = base_weather['temperature'] + random.randint(-2, 2)
            
            # Generate hourly forecasts
            hourly_forecasts = []
            time_slots = [8, 12, 16, 20]
            
            for hour in time_slots:
                hour_temp = daily_temp + random.randint(-1, 1)
                hourly_forecasts.append({
                    'time': f"{hour:02d}:00",
                    'temperature': hour_temp,
                    'description': base_weather['description'],
                    'icon': base_weather['icon'],
                    'feels_like': hour_temp + random.randint(-1, 1),
                    'humidity': random.randint(50, 80),
                    'wind_speed': round(random.uniform(1.0, 5.0), 1),
                })
            
            # Get min and max temps
            hourly_temps = [h['temperature'] for h in hourly_forecasts]
            min_temp = min(hourly_temps)
            max_temp = max(hourly_temps)
            
            # Noon forecast as daily summary
            noon_forecast = hourly_forecasts[1]  # 12:00
            
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
        
        return forecasts

# Create global instance
weather_service = WeatherService()