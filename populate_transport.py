# C:\Users\ASUS\MyanmarTravelPlanner\populate_transport.py
import os
import sys
import django
from decimal import Decimal
from datetime import time, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from planner.models import Destination, Flight, BusService, CarRental

def populate_transport():
    print("Populating transport options...")
    
    # Get destinations
    yangon = Destination.objects.get(name="Yangon")
    mandalay = Destination.objects.get(name="Mandalay")
    bagan = Destination.objects.get(name="Bagan")
    inle_lake = Destination.objects.get(name="Inle Lake")
    
    # Flights
    FLIGHTS = [
        {
            "airline": "Air KBZ",
            "flight_number": "K7 201",
            "departure": yangon,
            "arrival": mandalay,
            "departure_time": time(6, 0),
            "arrival_time": time(7, 30),
            "duration": timedelta(hours=1, minutes=30),
            "price": Decimal("50.00"),
            "category": "low",
            "total_seats": 180,
            "available_seats": 150
        },
        {
            "airline": "Myanmar National Airlines",
            "flight_number": "UB 301",
            "departure": yangon,
            "arrival": mandalay,
            "departure_time": time(10, 0),
            "arrival_time": time(11, 30),
            "duration": timedelta(hours=1, minutes=30),
            "price": Decimal("80.00"),
            "category": "medium",
            "total_seats": 150,
            "available_seats": 120
        },
        {
            "airline": "Golden Myanmar Airlines",
            "flight_number": "GY 101",
            "departure": yangon,
            "arrival": mandalay,
            "departure_time": time(14, 0),
            "arrival_time": time(15, 30),
            "duration": timedelta(hours=1, minutes=30),
            "price": Decimal("120.00"),
            "category": "high",
            "total_seats": 120,
            "available_seats": 80
        },
        {
            "airline": "Air KBZ",
            "flight_number": "K7 205",
            "departure": yangon,
            "arrival": bagan,
            "departure_time": time(8, 0),
            "arrival_time": time(9, 15),
            "duration": timedelta(hours=1, minutes=15),
            "price": Decimal("60.00"),
            "category": "medium",
            "total_seats": 180,
            "available_seats": 140
        }
    ]
    
    for flight_data in FLIGHTS:
        flight, created = Flight.objects.get_or_create(
            airline=flight_data["airline"],
            flight_number=flight_data["flight_number"],
            departure=flight_data["departure"],
            arrival=flight_data["arrival"],
            defaults=flight_data
        )
        if created:
            print(f"Created flight: {flight.airline} {flight.flight_number}")
    
    # Bus Services
    BUSES = [
        {
            "company": "JJ Express",
            "departure": yangon,
            "arrival": mandalay,
            "departure_time": time(20, 0),
            "duration": timedelta(hours=9),
            "price": Decimal("20.00"),
            "bus_type": "standard",
            "total_seats": 40,
            "available_seats": 30
        },
        {
            "company": "Elite Bus",
            "departure": yangon,
            "arrival": mandalay,
            "departure_time": time(21, 0),
            "duration": timedelta(hours=8, minutes=30),
            "price": Decimal("40.00"),
            "bus_type": "vip",
            "total_seats": 30,
            "available_seats": 25
        },
        {
            "company": "Luxury Coach",
            "departure": yangon,
            "arrival": mandalay,
            "departure_time": time(22, 0),
            "duration": timedelta(hours=8),
            "price": Decimal("60.00"),
            "bus_type": "luxury",
            "total_seats": 20,
            "available_seats": 15
        },
        {
            "company": "Mandalar Express",
            "departure": yangon,
            "arrival": bagan,
            "departure_time": time(19, 0),
            "duration": timedelta(hours=10),
            "price": Decimal("25.00"),
            "bus_type": "standard",
            "total_seats": 40,
            "available_seats": 35
        }
    ]
    
    for bus_data in BUSES:
        bus, created = BusService.objects.get_or_create(
            company=bus_data["company"],
            departure=bus_data["departure"],
            arrival=bus_data["arrival"],
            defaults=bus_data
        )
        if created:
            print(f"Created bus: {bus.company}")
    
    # Car Rentals
    CARS = [
        {
            "company": "City Car Rental",
            "car_model": "Toyota Vios",
            "car_type": "economy",
            "seats": 4,
            "price_per_day": Decimal("35.00"),
            "features": ["AC", "GPS", "Automatic"],
            "is_available": True,
            "location": yangon
        },
        {
            "company": "Premium Rentals",
            "car_model": "Toyota Fortuner",
            "car_type": "suv",
            "seats": 7,
            "price_per_day": Decimal("65.00"),
            "features": ["AC", "GPS", "Automatic", "Sunroof"],
            "is_available": True,
            "location": yangon
        },
        {
            "company": "Luxury Wheels",
            "car_model": "Mercedes E-Class",
            "car_type": "luxury",
            "seats": 4,
            "price_per_day": Decimal("120.00"),
            "features": ["AC", "GPS", "Automatic", "Leather", "Premium Sound"],
            "is_available": True,
            "location": yangon
        },
        {
            "company": "Mandalay Rent-a-Car",
            "car_model": "Honda City",
            "car_type": "economy",
            "seats": 4,
            "price_per_day": Decimal("30.00"),
            "features": ["AC", "Manual"],
            "is_available": True,
            "location": mandalay
        },
        {
            "company": "Bagan Car Rental",
            "car_model": "Suzuki Ertiga",
            "car_type": "suv",
            "seats": 7,
            "price_per_day": Decimal("55.00"),
            "features": ["AC", "Manual", "Roof Rack"],
            "is_available": True,
            "location": bagan
        }
    ]
    
    for car_data in CARS:
        car, created = CarRental.objects.get_or_create(
            company=car_data["company"],
            car_model=car_data["car_model"],
            location=car_data["location"],
            defaults=car_data
        )
        if created:
            print(f"Created car: {car.company} - {car.car_model}")
    
    print(f"Total flights: {Flight.objects.count()}")
    print(f"Total buses: {BusService.objects.count()}")
    print(f"Total cars: {CarRental.objects.count()}")

if __name__ == "__main__":
    populate_transport()