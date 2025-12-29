
# C:\Users\ASUS\MyanmarTravelPlanner\users\forms_admin.py
from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser
from planner.models import Destination, Hotel, Flight, BusService
import json
# C:\Users\ASUS\MyanmarTravelPlanner\users\forms_admin.py
from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser
from planner.models import Destination, Hotel, Flight, BusService
import json

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

class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
# C:\Users\ASUS\MyanmarTravelPlanner\users\forms_admin.py
# Update or add this form:

class HotelFormWithMap(forms.ModelForm):
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
    
    class Meta:
        model = Hotel
        fields = '__all__'
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'amenities': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter amenities separated by commas'}),
        }
class HotelForm(forms.ModelForm):
    # Add custom field for amenities as comma-separated string
    amenities_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 
                                     'placeholder': 'Enter amenities separated by commas (wifi, pool, spa, restaurant, gym, parking, breakfast, air_conditioning, tv, minibar)'}),
        help_text='Enter amenities separated by commas'
    )
    
    # Google Maps fields
    google_maps_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'google-maps-address',
            'placeholder': 'Search for address on Google Maps...'
        }),
        help_text='Type to search address on Google Maps'
    )
    
    use_real_location = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'use-real-location'}),
        help_text='Check to use real Google Maps location (uncheck to set custom location)'
    )
    
    class Meta:
        model = Hotel
        fields = [
            'name', 'destination', 'address', 'description', 
            'price_per_night', 'category', 'rating', 'review_count',
            'image', 'gallery_images', 'is_active', 'latitude', 'longitude'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mandalay Hill Resort'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Enter full address including street, city, and region'}),
            'price_per_night': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '1000',
                'placeholder': 'e.g., 50000'
            }),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '5', 'placeholder': 'e.g., 4.5'}),
            'review_count': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 120'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'latitude': forms.HiddenInput(attrs={'id': 'latitude-field'}),
            'longitude': forms.HiddenInput(attrs={'id': 'longitude-field'}),
        }
        help_texts = {
            'price_per_night': 'Enter price in MMK (Myanmar Kyat) per night',
            'latitude': 'Automatically filled from Google Maps',
            'longitude': 'Automatically filled from Google Maps',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.amenities:
            # Convert JSON list to comma-separated string
            self.initial['amenities_text'] = ', '.join(self.instance.amenities)
    
    def clean_price_per_night(self):
        price = self.cleaned_data.get('price_per_night')
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative")
        return price
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is not None:
            if rating < 0 or rating > 5:
                raise forms.ValidationError("Rating must be between 0 and 5")
        return rating
    
    def save(self, commit=True):
        hotel = super().save(commit=False)
        
        # Convert amenities_text to JSON list
        amenities_text = self.cleaned_data.get('amenities_text', '')
        if amenities_text:
            amenities_list = [amenity.strip().lower() for amenity in amenities_text.split(',')]
            hotel.amenities = amenities_list
        
        # Mark as created by admin
        hotel.created_by_admin = True
        
        if commit:
            hotel.save()
        return hotel

class HotelForm(forms.ModelForm):
    # Add custom field for amenities as comma-separated string
    amenities_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 
                                     'placeholder': 'Enter amenities separated by commas (wifi, pool, spa, restaurant, gym, parking, breakfast)'}),
        help_text='Enter amenities separated by commas'
    )
    
    # Google Maps fields
    google_maps_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'google-maps-address',
            'placeholder': 'Search for address on Google Maps...'
        }),
        help_text='Type to search address on Google Maps'
    )
    
    use_real_location = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'use-real-location'}),
        help_text='Check to use real Google Maps location (uncheck to set custom location)'
    )
    
    class Meta:
        model = Hotel
        fields = [
            'name', 'destination', 'address', 'description', 
            'price_per_night', 'category', 'rating', 'review_count',
            'image', 'gallery_images', 'is_active', 'latitude', 'longitude',
            'is_real_hotel', 'google_place_id'
        ]
        widgets = {
             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Mandalay Hill Resort'
            }),
            'address': forms.Textarea(attrs={
                'rows': 2, 
                'class': 'form-control', 
                'placeholder': 'Enter full address: Street, Township, City, Country\nExample: 123 Main Street, Kyauktada Township, Yangon, Myanmar'
            }),
              'price_per_night': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '1000',
                'placeholder': 'e.g., 50000 (MMK)'
            }),
            'rating': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.1', 
                'min': '0', 
                'max': '5', 
                'placeholder': 'e.g., 4.5'
            }),
            'review_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'latitude': forms.HiddenInput(attrs={'id': 'latitude-field'}),
            'longitude': forms.HiddenInput(attrs={'id': 'longitude-field'}),
        }
        help_texts = {
            'price_per_night': 'Enter price in MMK (Myanmar Kyat)',
            'latitude': 'Automatically filled from Google Maps',
            'longitude': 'Automatically filled from Google Maps',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.amenities:
            # Convert JSON list to comma-separated string
            self.initial['amenities_text'] = ', '.join(self.instance.amenities)
    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address or len(address.strip()) < 10:
            raise forms.ValidationError(
                "Please enter a complete address including street, city, and country"
            )
        return address
    def save(self, commit=True):
        hotel = super().save(commit=False)
        
        # Convert amenities_text to JSON list
        amenities_text = self.cleaned_data.get('amenities_text', '')
        if amenities_text:
            amenities_list = [amenity.strip().lower() for amenity in amenities_text.split(',')]
            hotel.amenities = amenities_list
        
        # Mark as created by admin
        hotel.created_by_admin = True
        
        if commit:
            hotel.save()
        return hotel

# ... rest of your existing forms remain the same ...
class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = ['airline', 'flight_number', 'departure', 'arrival', 
                  'departure_time', 'arrival_time', 'duration', 'price',
                  'category', 'total_seats', 'available_seats', 'description',
                  'flight_image', 'amenities', 'is_active']
        widgets = {
            'airline': forms.TextInput(attrs={'class': 'form-control'}),
            'flight_number': forms.TextInput(attrs={'class': 'form-control'}),
            'departure': forms.Select(attrs={'class': 'form-select'}),
            'arrival': forms.Select(attrs={'class': 'form-select'}),
            'departure_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'arrival_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM:SS'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'flight_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'amenities': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 
                                               'placeholder': 'Enter as JSON array: ["wifi", "meals", "entertainment"]'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BusServiceForm(forms.ModelForm):
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
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM:SS'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bus_type': forms.Select(attrs={'class': 'form-select'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'bus_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bus_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'amenities': forms.Textarea(attrs={'class': 'form-control', 'rows': 2,
                                               'placeholder': 'Enter as JSON array: ["ac", "wifi", "tv"]'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }