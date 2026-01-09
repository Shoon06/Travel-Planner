import sys
import os

# Add the project to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')

import django
django.setup()

# Test weather service
try:
    from planner.weather_service import weather_service
    print("✓ Weather service imported successfully!")
    
    # Test current weather
    print("\n1. Testing current weather for Yangon:")
    current = weather_service.get_weather_by_city("Yangon")
    print(f"   Temperature: {current['temperature']}°C")
    print(f"   Description: {current['description']}")
    print(f"   Is mock data: {current.get('is_mock', True)}")
    
    # Test forecast
    print("\n2. Testing forecast for Yangon:")
    forecast = weather_service.get_weather_forecast("Yangon", "2025-01-10", "2025-01-12")
    print(f"   Forecast days: {len(forecast)}")
    
    if forecast:
        first_date = list(forecast.keys())[0]
        print(f"   First day ({first_date}):")
        print(f"     Day: {forecast[first_date]['day_name']}")
        print(f"     Temp: {forecast[first_date]['daily_summary']['temperature']}°C")
        print(f"     Weather: {forecast[first_date]['daily_summary']['description']}")
    
    print("\n✓ All weather tests passed!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure weather_service.py is in the planner folder")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()