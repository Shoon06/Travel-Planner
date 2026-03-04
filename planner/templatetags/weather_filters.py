from django import template
from datetime import datetime, timedelta
import re

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def get_day_name(forecast, index):
    """Get day name for a specific index"""
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    if isinstance(forecast, dict):
        keys = list(forecast.keys())
        if index < len(keys):
            date_str = keys[index]
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                return date_obj.strftime('%A')
            except ValueError:
                return days[index % 7]
    return days[index % 7]

@register.filter
def get_hourly_weather(forecast, time_arg):
    """Get hourly weather for specific date and time"""
    try:
        if not forecast or not isinstance(forecast, dict):
            return None
        
        # Parse the time_arg which should be in format "2024-01-10:09:00AM"
        parts = str(time_arg).split(':')
        if len(parts) < 2:  # Changed from < 3 to handle simpler formats
            return None
        
        date_str = parts[0]
        time_str = parts[1] if len(parts) > 1 else "12:00"
        
        # Handle AM/PM if present
        if len(parts) > 2:
            time_str += f":{parts[2]}"
        
        # Check if date exists in forecast
        if date_str not in forecast:
            # Try to find any date in forecast
            dates = list(forecast.keys())
            if dates:
                date_str = dates[0]  # Use first available date
        
        date_forecast = forecast.get(date_str, {})
        
        # Get the target hour
        time_match = re.search(r'(\d+):', time_str)
        if not time_match:
            return None
            
        target_hour = int(time_match.group(1))
        
        # Handle AM/PM
        time_str_upper = time_str.upper()
        if 'PM' in time_str_upper and target_hour < 12:
            target_hour += 12
        elif 'AM' in time_str_upper and target_hour == 12:
            target_hour = 0
        
        # Find closest hourly forecast
        closest = None
        min_diff = 24
        
        hourly_forecasts = date_forecast.get('hourly_forecasts', [])
        for hourly in hourly_forecasts:
            hour_time_str = hourly.get('time', '00:00')
            hour_time = int(hour_time_str.split(':')[0])
            diff = abs(hour_time - target_hour)
            
            if diff < min_diff:
                min_diff = diff
                closest = hourly
        
        # If no hourly forecast found, return daily summary
        if not closest and 'daily_summary' in date_forecast:
            closest = date_forecast['daily_summary']
        
        return closest
        
    except Exception as e:
        print(f"Error in get_hourly_weather: {e}")
        return None

@register.filter
def weather_icon_url(icon_code):
    """Generate OpenWeatherMap icon URL"""
    return f"https://openweathermap.org/img/wn/{icon_code}.png"

@register.filter
def format_temperature(temp):
    """Format temperature with degree symbol"""
    return f"{temp}°C" if temp is not None else "N/A"