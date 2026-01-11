# C:\Users\ASUS\MyanmarTravelPlanner\users\forms_admin.py
from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser
from planner.models import Destination, Hotel, Flight, BusService, CarRental, Airline
import json

# ========== USER FORMS ==========
class CustomUserAdminForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 
                  'user_type', 'is_active', 'is_staff', 'is_superuser',
                  'phone_number', 'location', 'bio', 'profile_picture')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

# ========== DESTINATION FORMS ==========
class AdminAddDestinationForm(forms.ModelForm):
    """Form for adding destinations with coordinate help"""
    class Meta:
        model = Destination
        fields = ['name', 'region', 'type', 'latitude', 'longitude', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Yangon'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Yangon Region'
            }),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': '16.8409 (Yangon latitude)'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': '96.1735 (Yangon longitude)'
            }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'latitude': 'Latitude coordinate (e.g., 16.8409 for Yangon, 21.9588 for Mandalay)',
            'longitude': 'Longitude coordinate (e.g., 96.1735 for Yangon, 96.0891 for Mandalay)',
        }

class AdminEditDestinationForm(forms.ModelForm):
    """Form for editing destinations"""
    class Meta:
        model = Destination
        fields = ['name', 'region', 'type', 'latitude', 'longitude', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001'
            }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# ========== HOTEL FORMS ==========
class AdminAddHotelForm(forms.ModelForm):
    """Form for adding hotels with manual coordinate input"""
    amenities_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2, 
            'class': 'form-control', 
            'placeholder': 'Enter amenities separated by commas: wifi, pool, spa, restaurant, gym, parking, breakfast'
        }),
        help_text='Enter amenities separated by commas'
    )
    
    class Meta:
        model = Hotel
        fields = [
            'name', 'destination', 'address', 'latitude', 'longitude',
            'price_per_night', 'category', 'rating', 'review_count',
            'description', 'image', 'phone_number', 'website',
            'is_real_hotel', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Mandalay Hill Resort'
            }),
            'destination': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={
                'rows': 2, 
                'class': 'form-control',
                'placeholder': 'Full address including street, city, region'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': '21.9588 (Mandalay latitude)'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001',
                'placeholder': '96.0891 (Mandalay longitude)'
            }),
            'price_per_night': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1000',
                'placeholder': '50000 (MMK per night)'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '5',
                'placeholder': '4.5'
            }),
            'review_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'is_real_hotel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'latitude': 'Latitude coordinate (required for map display)',
            'longitude': 'Longitude coordinate (required for map display)',
            'price_per_night': 'Price in MMK (Myanmar Kyat) per night',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize amenities text field if editing
        if self.instance and self.instance.pk and self.instance.amenities:
            self.initial['amenities_text'] = ', '.join(self.instance.amenities)
    
    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        # Check if coordinates are provided
        if not latitude or not longitude:
            raise forms.ValidationError(
                "Please provide both latitude and longitude coordinates for map display."
            )
        
        # Validate Myanmar coordinates range
        if latitude and (latitude < 9.0 or latitude > 28.0):
            raise forms.ValidationError("Latitude must be within Myanmar (approximately 9.0 to 28.0)")
        
        if longitude and (longitude < 92.0 or longitude > 101.0):
            raise forms.ValidationError("Longitude must be within Myanmar (approximately 92.0 to 101.0)")
        
        return cleaned_data
    
    def save(self, commit=True):
        hotel = super().save(commit=False)
        
        # Convert amenities_text to JSON list
        amenities_text = self.cleaned_data.get('amenities_text', '')
        if amenities_text:
            amenities_list = [amenity.strip().lower() for amenity in amenities_text.split(',')]
            hotel.amenities = amenities_list
        else:
            hotel.amenities = []
        
        # Mark as created by admin
        hotel.created_by_admin = True
        
        if commit:
            hotel.save()
        return hotel

class AdminEditHotelForm(forms.ModelForm):
    """Form for editing hotels"""
    amenities_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 2, 
            'class': 'form-control', 
            'placeholder': 'wifi, pool, spa, restaurant, gym, parking, breakfast'
        }),
        help_text='Enter amenities separated by commas'
    )
    
    class Meta:
        model = Hotel
        fields = [
            'name', 'destination', 'address', 'latitude', 'longitude',
            'price_per_night', 'category', 'rating', 'review_count',
            'description', 'image', 'phone_number', 'website',
            'is_real_hotel', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.000001'
            }),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0',
                'max': '5'
            }),
            'review_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'is_real_hotel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.amenities:
            self.initial['amenities_text'] = ', '.join(self.instance.amenities)
    
    def save(self, commit=True):
        hotel = super().save(commit=False)
        
        # Convert amenities_text to JSON list
        amenities_text = self.cleaned_data.get('amenities_text', '')
        if amenities_text:
            amenities_list = [amenity.strip().lower() for amenity in amenities_text.split(',')]
            hotel.amenities = amenities_list
        
        if commit:
            hotel.save()
        return hotel

# ========== HOTEL FORM WITH MAP (Optional - for Google Maps integration) ==========
class HotelFormWithMap(forms.ModelForm):
    """Hotel form with Google Maps integration (if you want to use maps in admin)"""
    latitude = forms.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        required=False,
        widget=forms.HiddenInput()
    )
    longitude = forms.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        required=False,
        widget=forms.HiddenInput()
    )
    
    google_maps_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for address on Google Maps...'
        }),
        help_text='Type to search address on Google Maps'
    )
    
    class Meta:
        model = Hotel
        fields = ['name', 'destination', 'address', 'description', 
                 'price_per_night', 'category', 'rating', 'review_count',
                 'image', 'is_active', 'latitude', 'longitude']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

# ========== FLIGHT FORMS ==========
class AdminAddFlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ['airline', 'flight_number', 'departure', 'arrival', 
                  'departure_time', 'arrival_time', 'duration', 'price',
                  'category', 'total_seats', 'available_seats', 'description',
                  'flight_image', 'amenities', 'is_active']
        widgets = {
            'airline': forms.Select(attrs={'class': 'form-select'}),
            'flight_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., MTA101'
            }),
            'departure': forms.Select(attrs={'class': 'form-select'}),
            'arrival': forms.Select(attrs={'class': 'form-select'}),
            'departure_time': forms.TimeInput(attrs={
                'class': 'form-control', 
                'type': 'time'
            }),
            'arrival_time': forms.TimeInput(attrs={
                'class': 'form-control', 
                'type': 'time'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'HH:MM:SS (e.g., 01:30:00)'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1000',
                'placeholder': 'e.g., 80000 (MMK)'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'flight_image': forms.FileInput(attrs={'class': 'form-control'}),
            'amenities': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2,
                'placeholder': 'Enter as JSON array: ["wifi", "meals", "entertainment"]'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'price': 'Price in MMK (Myanmar Kyat)',
        }

class AdminEditFlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ['airline', 'flight_number', 'departure', 'arrival', 
                  'departure_time', 'arrival_time', 'duration', 'price',
                  'category', 'total_seats', 'available_seats', 'description',
                  'flight_image', 'amenities', 'is_active']
        widgets = {
            'airline': forms.Select(attrs={'class': 'form-select'}),
            'flight_number': forms.TextInput(attrs={'class': 'form-control'}),
            'departure': forms.Select(attrs={'class': 'form-select'}),
            'arrival': forms.Select(attrs={'class': 'form-select'}),
            'departure_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'arrival_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'flight_image': forms.FileInput(attrs={'class': 'form-control'}),
            'amenities': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# ========== BUS SERVICE FORMS ==========
class AdminAddBusForm(forms.ModelForm):
    class Meta:
        model = BusService
        fields = ['company', 'departure', 'arrival', 'departure_time', 
                  'duration', 'price', 'bus_type', 'total_seats', 
                  'available_seats', 'bus_number', 'bus_image', 
                  'amenities', 'description', 'is_active']
        widgets = {
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Myanmar Express Bus'
            }),
            'departure': forms.Select(attrs={'class': 'form-select'}),
            'arrival': forms.Select(attrs={'class': 'form-select'}),
            'departure_time': forms.TimeInput(attrs={
                'class': 'form-control', 
                'type': 'time'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'HH:MM:SS (e.g., 08:00:00)'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1000',
                'placeholder': 'e.g., 25000 (MMK)'
            }),
            'bus_type': forms.Select(attrs={'class': 'form-select'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'bus_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bus_image': forms.FileInput(attrs={'class': 'form-control'}),
            'amenities': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2,
                'placeholder': 'Enter as JSON array: ["ac", "wifi", "tv", "toilet"]'
            }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'price': 'Price in MMK (Myanmar Kyat)',
        }

class AdminEditBusForm(forms.ModelForm):
    class Meta:
        model = BusService
        fields = ['company', 'departure', 'arrival', 'departure_time', 
                  'duration', 'price', 'bus_type', 'total_seats', 
                  'available_seats', 'bus_number', 'bus_image', 
                  'amenities', 'description', 'is_active']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'departure': forms.Select(attrs={'class': 'form-select'}),
            'arrival': forms.Select(attrs={'class': 'form-select'}),
            'departure_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'bus_type': forms.Select(attrs={'class': 'form-select'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'bus_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bus_image': forms.FileInput(attrs={'class': 'form-control'}),
            'amenities': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# ========== CAR RENTAL FORMS ==========
class AdminAddCarForm(forms.ModelForm):
    class Meta:
        model = CarRental
        fields = ['company', 'car_model', 'car_type', 'seats', 
                  'price_per_day', 'features', 'is_available', 
                  'location', 'car_image', 'description', 'year',
                  'fuel_type', 'transmission']
        widgets = {
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Myanmar Car Rentals'
            }),
            'car_model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Toyota Vios'
            }),
            'car_type': forms.Select(attrs={'class': 'form-select'}),
            'seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_per_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1000',
                'placeholder': 'e.g., 40000 (MMK per day)'
            }),
            'features': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 2,
                'placeholder': 'Enter as JSON array: ["ac", "gps", "bluetooth"]'
            }),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'car_image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'transmission': forms.Select(attrs={'class': 'form-select'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'price_per_day': 'Price in MMK (Myanmar Kyat) per day',
        }

class AdminEditCarForm(forms.ModelForm):
    class Meta:
        model = CarRental
        fields = ['company', 'car_model', 'car_type', 'seats', 
                  'price_per_day', 'features', 'is_available', 
                  'location', 'car_image', 'description', 'year',
                  'fuel_type', 'transmission']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'car_model': forms.TextInput(attrs={'class': 'form-control'}),
            'car_type': forms.Select(attrs={'class': 'form-select'}),
            'seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_per_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'features': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'location': forms.Select(attrs={'class': 'form-select'}),
            'car_image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'transmission': forms.Select(attrs={'class': 'form-select'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# ========== AIRLINE FORMS ==========
class AdminAddAirlineForm(forms.ModelForm):
    class Meta:
        model = Airline
        fields = ['name', 'code', 'logo', 'description', 'is_active', 'is_default_for_domestic']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Myanmar Travel Airlines'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., MTA'
            }),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_default_for_domestic': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AdminEditAirlineForm(forms.ModelForm):
    class Meta:
        model = Airline
        fields = ['name', 'code', 'logo', 'description', 'is_active', 'is_default_for_domestic']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_default_for_domestic': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }