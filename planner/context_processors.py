# C:\Users\ASUS\MyanmarTravelPlanner\planner\context_processors.py
# Create this file if it doesn't exist

from django.conf import settings

def leaflet_config(request):
    """Add Leaflet configuration to template context"""
    return {
        'LEAFLET_CONFIG': settings.LEAFLET_CONFIG,
        'USE_GOOGLE_MAPS': False,
        'MAP_PROVIDER': 'leaflet'
    }