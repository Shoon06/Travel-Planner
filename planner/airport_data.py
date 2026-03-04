"""
AIRPORT DATA FOR MYANMAR DESTINATIONS
"""

MYANMAR_AIRPORTS = {
    # Major International/Regional Airports
    'Yangon': {
        'airport_name': 'Yangon International Airport',
        'iata_code': 'RGN',
        'has_airport': True,
        'type': 'international',
        'coordinates': {'lat': 16.9073, 'lng': 96.1332}
    },
    'Mandalay': {
        'airport_name': 'Mandalay International Airport',
        'iata_code': 'MDL',
        'has_airport': True,
        'type': 'international',
        'coordinates': {'lat': 21.7022, 'lng': 95.9779}
    },
    'Naypyidaw': {
        'airport_name': 'Naypyidaw International Airport',
        'iata_code': 'NYT',
        'has_airport': True,
        'type': 'international',
        'coordinates': {'lat': 19.6235, 'lng': 96.2010}
    },
    
    # Domestic Airports
    'Bagan': {
        'airport_name': 'Nyaung U Airport',
        'iata_code': 'NYU',
        'has_airport': True,
        'type': 'domestic',
        'coordinates': {'lat': 21.1788, 'lng': 94.9302}
    },
    'Heho': {
        'airport_name': 'Heho Airport',
        'iata_code': 'HEH',
        'has_airport': True,
        'type': 'domestic',
        'coordinates': {'lat': 20.7470, 'lng': 96.7920}
    },
    'Thandwe': {
        'airport_name': 'Thandwe Airport',
        'iata_code': 'SNW',
        'has_airport': True,
        'type': 'domestic',
        'coordinates': {'lat': 18.4607, 'lng': 94.2996}
    },
    'Sittwe': {
        'airport_name': 'Sittwe Airport',
        'iata_code': 'AKY',
        'has_airport': True,
        'type': 'domestic',
        'coordinates': {'lat': 20.1327, 'lng': 92.8726}
    },
    'Myitkyina': {
        'airport_name': 'Myitkyina Airport',
        'iata_code': 'MYT',
        'has_airport': True,
        'type': 'domestic',
        'coordinates': {'lat': 25.3544, 'lng': 97.2952}
    },
    'Tachileik': {
        'airport_name': 'Tachileik Airport',
        'iata_code': 'THL',
        'has_airport': True,
        'type': 'domestic',
        'coordinates': {'lat': 20.4838, 'lng': 99.9354}
    },
    'Kawthaung': {
        'airport_name': 'Kawthaung Airport',
        'iata_code': 'KAW',
        'has_airport': True,
        'type': 'domestic',
        'coordinates': {'lat': 10.0495, 'lng': 98.5380}
    },
    'Dawei': {
        'airport_name': 'Dawei Airport',
        'iata_code': 'TVY',
        'has_airport': True,
        'type': 'domestic',
        'coordinates': {'lat': 14.1039, 'lng': 98.2036}
    },
    'Myeik': {
        'airport_name': 'Myeik Airport',
        'iata_code': 'MGZ',
        'has_airport': True,
        'type': 'domestic',
        'coordinates': {'lat': 12.4398, 'lng': 98.6215}
    },
    'Mawlamyine': {
        'airport_name': 'Mawlamyine Airport',
        'iata_code': 'MNU',
        'has_airport': True,
        'type': 'domestic',
        'coordinates': {'lat': 16.4447, 'lng': 97.6607}
    },
    'Pathein': {
        'airport_name': 'Pathein Airport',
        'iata_code': 'BSX',
        'has_airport': True,
        'type': 'domestic',
        'coordinates': {'lat': 16.8152, 'lng': 94.7799}
    },
    'Loikaw': {
        'airport_name': 'Loikaw Airport',
        'iata_code': 'LIW',
        'has_airport': True,
        'type': 'domestic',
        'coordinates': {'lat': 19.6915, 'lng': 97.2148}
    },
    'Hakha': {
        'airport_name': 'Hakha Airport',
        'iata_code': 'HKH',
        'has_airport': True,
        'type': 'domestic',
        'coordinates': {'lat': 22.6470, 'lng': 93.6110}
    },
    
    # DESTINATIONS WITHOUT AIRPORTS (Bus/Car only)
    'Pyin Oo Lwin': {'has_airport': False},
    'Hsipaw': {'has_airport': False},
    'Kalaw': {'has_airport': False},
    'Hpa-An': {'has_airport': False},
    'Monywa': {'has_airport': False},
    'Taunggyi': {'has_airport': False},
    'Inle Lake': {'has_airport': False},
    'Ngapali Beach': {'has_airport': False},
    'Ngwe Saung Beach': {'has_airport': False},
    'Kyaiktiyo': {'has_airport': False},
    'Mrauk U': {'has_airport': False},
    'Bago': {'has_airport': False},
    'Sagaing': {'has_airport': False},
    'Magway': {'has_airport': False},
    'Kachin State': {'has_airport': False},
    'Kayah State': {'has_airport': False},
    'Kayin State': {'has_airport': False},
    'Chin State': {'has_airport': False},
    'Mon State': {'has_airport': False},
    'Rakhine State': {'has_airport': False},
    'Shan State': {'has_airport': False},
}

def get_airport_info(destination_name):
    """
    Get airport information for a destination
    
    Args:
        destination_name (str): Name of the destination
    
    Returns:
        dict: Airport information or {'has_airport': False} if no airport
    """
    if not destination_name:
        return {'has_airport': False}
    
    # Clean the destination name
    destination_name = str(destination_name).strip()
    
    # Check exact match first
    if destination_name in MYANMAR_AIRPORTS:
        return MYANMAR_AIRPORTS[destination_name]
    
    # Check for "Inle Lake" (uses Heho airport)
    if 'Inle Lake' in destination_name or 'Inle' in destination_name:
        return MYANMAR_AIRPORTS['Heho']
    
    # Check for "Ngapali Beach" (uses Thandwe airport)
    if 'Ngapali' in destination_name:
        return MYANMAR_AIRPORTS['Thandwe']
    
    # Check partial matches
    for key, info in MYANMAR_AIRPORTS.items():
        if key.lower() in destination_name.lower() or destination_name.lower() in key.lower():
            return info
    
    # Default to no airport
    return {'has_airport': False}

def destination_has_airport(destination_name):
    """
    Check if a destination has an airport
    
    Args:
        destination_name (str): Name of the destination
    
    Returns:
        bool: True if destination has airport, False otherwise
    """
    info = get_airport_info(destination_name)
    return info.get('has_airport', False)

def get_nearest_airport(destination_name):
    """
    Get nearest airport for a destination without airport
    
    Args:
        destination_name (str): Name of the destination
    
    Returns:
        dict: Nearest airport information
    """
    info = get_airport_info(destination_name)
    
    # If destination has airport, return it
    if info.get('has_airport', False):
        return info
    
    # Map destinations without airports to nearest airports
    nearest_airport_map = {
        'Pyin Oo Lwin': 'Mandalay',
        'Hsipaw': 'Lashio',  # Note: Lashio not in our list, using Mandalay
        'Kalaw': 'Heho',
        'Hpa-An': 'Hpa-An has no airport, nearest is Yangon',
        'Monywa': 'Mandalay',
        'Taunggyi': 'Heho',
        'Inle Lake': 'Heho',
        'Ngapali Beach': 'Thandwe',
        'Ngwe Saung Beach': 'Pathein',
        'Kyaiktiyo': 'Yangon',
        'Mrauk U': 'Sittwe',
        'Bago': 'Yangon',
        'Sagaing': 'Mandalay',
        'Magway': 'Magway has no airport, nearest is Bagan',
    }
    
    if destination_name in nearest_airport_map:
        nearest = nearest_airport_map[destination_name]
        if nearest in MYANMAR_AIRPORTS:
            return MYANMAR_AIRPORTS[nearest]
    
    # Default to Yangon
    return MYANMAR_AIRPORTS['Yangon']