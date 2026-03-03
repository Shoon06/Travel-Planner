# C:\Users\ASUS\MyanmarTravelPlanner\planner\forms.py

from django import forms
from .models import Destination, Hotel, Flight, BusService, CarRental, TripPlan, Airline, BookedSeat
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import json

class DestinationForm(forms.ModelForm):
    # Add a choice field for regions
    region = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    # Multiple image fields for attractions
    image_1 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        label="Photo 1"
    )
    image_2 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        label="Photo 2"
    )
    image_3 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        label="Photo 3"
    )
    image_4 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        label="Photo 4"
    )
    image_5 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        label="Photo 5"
    )
    image_6 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        label="Photo 6"
    )
    image_7 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        label="Photo 7"
    )
    image_8 = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        label="Photo 8"
    )
    
    # Text blocks for each photo
    caption_1 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for Photo 1'}),
        label="Caption 1"
    )
    caption_2 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for Photo 2'}),
        label="Caption 2"
    )
    caption_3 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for Photo 3'}),
        label="Caption 3"
    )
    caption_4 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for Photo 4'}),
        label="Caption 4"
    )
    caption_5 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for Photo 5'}),
        label="Caption 5"
    )
    caption_6 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for Photo 6'}),
        label="Caption 6"
    )
    caption_7 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for Photo 7'}),
        label="Caption 7"
    )
    caption_8 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for Photo 8'}),
        label="Caption 8"
    )
    
    class Meta:
        model = Destination
        fields = [
            'name', 'region', 'type', 'description', 
            'latitude', 'longitude',
            'history', 'attractions', 'activities', 'cultural_info',
            'best_time_to_visit', 'local_cuisine', 'tips',
            'is_active', 'is_region', 'parent',
            # We'll handle images in save method
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'history': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'attractions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'activities': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'cultural_info': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'local_cuisine': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'tips': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get all unique regions/states from database
        regions = Destination.objects.exclude(region__isnull=True).exclude(region='')\
                                     .values_list('region', flat=True).distinct().order_by('region')
        
        # Create choices for region dropdown
        region_choices = [('', '--- Select Region/State ---')]
        for region in regions:
            region_choices.append((region, region))
        
        # Add any common regions that might not be in database yet
        common_regions = [
            'Yangon Region', 'Mandalay Region', 'Sagaing Region', 'Tanintharyi Region',
            'Bago Region', 'Magway Region', 'Ayeyarwady Region', 'Shan State',
            'Kachin State', 'Kayah State', 'Kayin State', 'Mon State',
            'Rakhine State', 'Chin State', 'Naypyidaw Union Territory'
        ]
        
        for region in common_regions:
            if region not in [r[0] for r in region_choices if r[0]]:
                region_choices.append((region, region))
        
        self.fields['region'].choices = region_choices
        
        # If this is an existing instance, populate the caption fields from JSON
        if self.instance and self.instance.pk and self.instance.gallery_images:
            try:
                if isinstance(self.instance.gallery_images, dict):
                    gallery = self.instance.gallery_images
                    for i in range(1, 9):
                        caption_key = f'caption_{i}'
                        if caption_key in gallery:
                            self.fields[f'caption_{i}'].initial = gallery[caption_key]
            except:
                pass
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle multiple images and captions
        gallery_data = {}
        
        # Process each image-caption pair
        for i in range(1, 9):
            image_field = f'image_{i}'
            caption_field = f'caption_{i}'
            
            if image_field in self.files:
                image_file = self.files[image_field]
                
                # Optimize image
                try:
                    img = Image.open(image_file)
                    
                    # Resize if too large (max 1200px)
                    if img.width > 1200 or img.height > 1200:
                        img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                    
                    # Save to BytesIO
                    img_io = BytesIO()
                    img.save(img_io, format='JPEG', quality=85, optimize=True)
                    img_io.seek(0)
                    
                    # Generate filename
                    filename = f"{instance.name.replace(' ', '_')}_{i}.jpg"
                    
                    # Save to the appropriate image field
                    setattr(instance, f'gallery_image{i}', filename)
                    getattr(instance, f'gallery_image{i}').save(filename, ContentFile(img_io.read()), save=False)
                    
                except Exception as e:
                    print(f"Error processing image {i}: {e}")
                    # If error, just save the original
                    setattr(instance, f'gallery_image{i}', image_file)
            
            # Store caption
            caption = self.cleaned_data.get(caption_field, '')
            if caption:
                gallery_data[f'caption_{i}'] = caption
        
        # Store gallery data as JSON
        if gallery_data:
            instance.gallery_images = gallery_data
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance