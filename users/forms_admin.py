# C:\Users\ASUS\MyanmarTravelPlanner\users\forms_admin.py
from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser
from planner.models import Destination, Hotel, Flight, BusService, CarRental, Airline
import json
from .models import CustomUser, SystemSettings
from django.db.models import Q  # ← Add this line
# ========== SIMPLE HOTEL FORM FOR MAP ==========
# C:\Users\ASUS\MyanmarTravelPlanner\users\forms_admin.py



# Add this at the TOP of your forms_admin.py, after other imports
from django.contrib.auth.forms import UserCreationForm

# Add this form class (put it after CustomUserAdminForm)
class AdminUserCreationForm(UserCreationForm):
    """Form for creating new users in admin panel"""
    
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        initial='user',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'user_type', 'is_active', 'first_name', 'last_name', 'phone_number')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
            
            # Set placeholders
            if field_name == 'username':
                field.widget.attrs['placeholder'] = 'Enter username'
            elif field_name == 'email':
                field.widget.attrs['placeholder'] = 'user@example.com'
            elif field_name == 'password1':
                field.widget.attrs['placeholder'] = 'Enter password'
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = 'Confirm password'
            elif field_name == 'first_name':
                field.widget.attrs['placeholder'] = 'First name'
            elif field_name == 'last_name':
                field.widget.attrs['placeholder'] = 'Last name'
            elif field_name == 'phone_number':
                field.widget.attrs['placeholder'] = 'Phone number'
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.cleaned_data.get('user_type', 'user')
        user.is_active = self.cleaned_data.get('is_active', True)
        
        # Set staff status based on user type
        if user.user_type == 'admin':
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False
        
        if commit:
            user.save()
        return user

# ============================
# ADD HOTEL (WITH MAP)
# ============================
class AdminAddHotelFormWithMap(forms.ModelForm):
    """Simple form for adding hotels with map"""

    # 🔥 OVERRIDE JSONField → CharField
    amenities = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'wifi, pool, spa, restaurant, gym'
        }),
        help_text='Enter amenities separated by commas or as JSON array'
    )

    class Meta:
        model = Hotel
        fields = [
            'name', 'destination', 'address',
            'latitude', 'longitude',
            'price_per_night', 'category',
            'rating', 'amenities',
            'description', 'image',
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
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
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
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Hotel description...'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_real_hotel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')

        if latitude and longitude:
            try:
                lat = float(latitude)
                lng = float(longitude)

                if not (9.0 <= lat <= 28.0):
                    raise forms.ValidationError(
                        "Latitude must be within Myanmar (9.0 – 28.0)"
                    )

                if not (92.0 <= lng <= 101.0):
                    raise forms.ValidationError(
                        "Longitude must be within Myanmar (92.0 – 101.0)"
                    )
            except (ValueError, TypeError):
                raise forms.ValidationError(
                    "Please provide valid latitude and longitude values"
                )

        return cleaned_data

    def clean_amenities(self):
        """
        Accepts:
        - wifi, pool, spa
        - ["wifi", "pool", "spa"]
        Stores: list[str]
        """
        raw = self.cleaned_data.get('amenities', '')

        if not raw:
            return []

        raw = raw.strip()

        # JSON input
        if raw.startswith('['):
            try:
                data = json.loads(raw)
                return [
                    str(a).strip().lower()
                    for a in data
                    if str(a).strip()
                ]
            except json.JSONDecodeError:
                raise forms.ValidationError(
                    "Invalid JSON format for amenities"
                )

        # Comma-separated
        return [
            a.strip().lower()
            for a in raw.split(',')
            if a.strip()
        ]


# ============================
# EDIT HOTEL
# ============================
# ============================
# EDIT HOTEL FORM
# ============================
class AdminEditHotelForm(forms.ModelForm):
    """Form for editing hotels"""

    # 🔥 OVERRIDE JSONField → CharField
    amenities = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'wifi, pool, spa, restaurant, gym'
        }),
        help_text='Enter amenities separated by commas or as JSON array like ["wifi", "pool"]'
    )

    class Meta:
        model = Hotel
        fields = [
            'name', 'destination', 'address',
            'latitude', 'longitude',
            'price_per_night', 'category',
            'rating', 'review_count',
            'amenities', 'description',
            'image', 'phone_number',
            'website', 'is_real_hotel',
            'is_active'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
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
        # If editing an existing instance, convert amenities list to string for display
        if self.instance and self.instance.pk and self.instance.amenities:
            if isinstance(self.instance.amenities, list):
                # Convert list to comma-separated string for the form field
                self.initial['amenities'] = ', '.join(self.instance.amenities)
            elif isinstance(self.instance.amenities, str):
                # If it's already a string (maybe from old data), use it as is
                self.initial['amenities'] = self.instance.amenities

    def clean_amenities(self):
        """
        Accepts both formats:
        1. Comma-separated: wifi, pool, spa
        2. JSON array: ["wifi", "pool", "spa"]
        Stores: list[str]
        """
        raw = self.cleaned_data.get('amenities', '')

        if not raw:
            return []

        raw = raw.strip()

        # Handle JSON array input like ["wifi", "pool"]
        if raw.startswith('[') and raw.endswith(']'):
            try:
                data = json.loads(raw)
                if isinstance(data, list):
                    return [
                        str(a).strip().lower()
                        for a in data
                        if str(a).strip()
                    ]
                else:
                    # If JSON is valid but not a list, wrap it in a list
                    return [str(data).strip().lower()]
            except json.JSONDecodeError:
                # If JSON parsing fails, fall back to comma-separated parsing
                pass

        # Handle comma-separated input like "wifi, pool, spa"
        return [
            a.strip().lower()
            for a in raw.split(',')
            if a.strip()
        ]

    def clean(self):
        """Add any additional form-wide validation"""
        cleaned_data = super().clean()
        
        # Validate coordinates if provided
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        if latitude and longitude:
            try:
                lat = float(latitude)
                lng = float(longitude)
                
                # Validate Myanmar coordinates
                if not (9.0 <= lat <= 28.0):
                    self.add_error('latitude', 
                        "Latitude must be within Myanmar (9.0 – 28.0)"
                    )
                
                if not (92.0 <= lng <= 101.0):
                    self.add_error('longitude',
                        "Longitude must be within Myanmar (92.0 – 101.0)"
                    )
            except (ValueError, TypeError):
                self.add_error('latitude', "Please provide valid numeric coordinates")
                self.add_error('longitude', "Please provide valid numeric coordinates")
        
        # Validate price
        price = cleaned_data.get('price_per_night')
        if price is not None and price < 0:
            self.add_error('price_per_night', "Price cannot be negative")
        
        # Validate rating
        rating = cleaned_data.get('rating')
        if rating is not None and (rating < 0 or rating > 5):
            self.add_error('rating', "Rating must be between 0 and 5")
        
        return cleaned_data

# ============================
# ADD HOTEL (MANUAL COORDINATES)
# ============================
class AdminAddHotelForm(forms.ModelForm):
    """Form for adding hotels with manual coordinate input"""
    
    # Add explicit amenities field
    amenities = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'wifi, pool, spa, restaurant, gym, parking, breakfast'
        }),
        help_text='Enter amenities separated by commas or as JSON array like ["wifi", "pool"]'
    )
    
    class Meta:
        model = Hotel
        fields = [
            'name', 'destination', 'address', 'latitude', 'longitude',
            'price_per_night', 'category', 'rating', 'amenities',
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
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'is_real_hotel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For new hotels, no initial data needed
    
    def clean_amenities(self):
        """Convert comma-separated amenities or JSON array to list"""
        amenities_text = self.cleaned_data.get('amenities', '')
        
        if not amenities_text:
            return []
        
        amenities_text = amenities_text.strip()
        
        # Handle JSON array input like ["wifi", "pool"]
        if amenities_text.startswith('[') and amenities_text.endswith(']'):
            try:
                import json
                amenities_list = json.loads(amenities_text)
                if isinstance(amenities_list, list):
                    return [str(amenity).strip().lower() for amenity in amenities_list if str(amenity).strip()]
                else:
                    # If JSON is valid but not a list, wrap it
                    return [str(amenities_list).strip().lower()]
            except json.JSONDecodeError:
                # If JSON parsing fails, fall back to comma-separated parsing
                pass
        
        # Handle comma-separated input like "wifi, pool, spa"
        amenities_list = [amenity.strip().lower() for amenity in amenities_text.split(',') if amenity.strip()]
        return amenities_list
    
    def clean(self):
        """Add form-wide validation"""
        cleaned_data = super().clean()
        
        # Validate coordinates if provided
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        if latitude and longitude:
            try:
                lat = float(latitude)
                lng = float(longitude)
                
                # Validate Myanmar coordinates
                if not (9.0 <= lat <= 28.0):
                    self.add_error('latitude', 
                        "Latitude must be within Myanmar (9.0 – 28.0)"
                    )
                
                if not (92.0 <= lng <= 101.0):
                    self.add_error('longitude',
                        "Longitude must be within Myanmar (92.0 – 101.0)"
                    )
            except (ValueError, TypeError):
                self.add_error('latitude', "Please provide valid numeric coordinates")
                self.add_error('longitude', "Please provide valid numeric coordinates")
        
        # Validate price
        price = cleaned_data.get('price_per_night')
        if price is not None and price < 0:
            self.add_error('price_per_night', "Price cannot be negative")
        
        # Validate rating
        rating = cleaned_data.get('rating')
        if rating is not None and (rating < 0 or rating > 5):
            self.add_error('rating', "Rating must be between 0 and 5")
        
        return cleaned_data
    
    def save(self, commit=True):
        hotel = super().save(commit=False)
        hotel.created_by_admin = True
        if commit:
            hotel.save()
        return hotel
# ========== EDIT HOTEL FORM ==========


# ========== DESTINATION FORMS ==========
# ========== DESTINATION FORMS ==========
# ========== DESTINATION FORMS ==========
# ========== DESTINATION FORMS ==========
# ========== DESTINATION FORMS ==========
# ========== DESTINATION FORMS ==========
class AdminAddDestinationForm(forms.ModelForm):
    """Enhanced form for adding destinations with 8 gallery images and captions"""
    
    # Add fields for 8 gallery images
    gallery_image1 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image2 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image3 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image4 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image5 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image6 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image7 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image8 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    # Add fields for captions (to be stored in gallery_captions JSON)
    caption_1 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 1'}))
    caption_2 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 2'}))
    caption_3 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 3'}))
    caption_4 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 4'}))
    caption_5 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 5'}))
    caption_6 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 6'}))
    caption_7 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 7'}))
    caption_8 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 8'}))
    
    # Add parent as a CharField for text input
    parent = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Bagan, Mandalay, Taunggyi'
        }),
        help_text='Enter the name of the city/town where this attraction is located (for attractions only)'
    )
    
    class Meta:
        model = Destination
        fields = [
            'name', 'region', 'type', 'latitude', 'longitude', 
            'description', 'is_active', 'is_region'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Yangon, Shwedagon Pagoda'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Yangon Region, Shan State'
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
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description of the destination'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_region': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make type field have the right choices
        self.fields['type'].choices = Destination._meta.get_field('type').choices
        
        # Make latitude and longitude not required at form level (HTML5 will handle it)
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        
        # Add a hidden field to store the active tab
        self.fields['active_tab'] = forms.CharField(
            required=False,
            widget=forms.HiddenInput(),
            initial='city'  # Default to city tab
        )
    
    def clean_parent(self):
        """Clean and validate parent field - only used for attractions"""
        # Get the destination type from the data
        dest_type = self.data.get('type', '')
        
        # If this is a city or town, return None immediately
        if dest_type in ['city', 'town']:
            return None
        
        parent_name = self.data.get('parent', '').strip()
        if not parent_name:
            return None
        
        # Try to find existing parent
        try:
            parent = Destination.objects.get(
                Q(name__iexact=parent_name) | 
                Q(name__icontains=parent_name),
                type__in=['city', 'town']
            )
            return parent
        except Destination.DoesNotExist:
            # Return the name as a string - will be handled in the view
            return parent_name
        except Destination.MultipleObjectsReturned:
            # If multiple found, return the first one
            return Destination.objects.filter(
                Q(name__iexact=parent_name) | 
                Q(name__icontains=parent_name),
                type__in=['city', 'town']
            ).first()
    
    def clean_latitude(self):
        """Clean and validate latitude field"""
        latitude = self.cleaned_data.get('latitude')
        
        # If latitude is empty, return None
        if not latitude:
            return None
        
        try:
            # Convert to float for validation
            lat_value = float(latitude)
            
            # Basic validation for Myanmar coordinates
            if not (9.0 <= lat_value <= 28.0):
                raise forms.ValidationError("Latitude must be within Myanmar (9.0 – 28.0)")
            
            # Round to 6 decimal places to avoid decimal place errors
            from decimal import Decimal, getcontext
            getcontext().prec = 10
            lat_value = Decimal(str(lat_value)).quantize(Decimal('0.000001'))
            
            return lat_value
        except (ValueError, TypeError):
            raise forms.ValidationError("Please provide a valid numeric latitude")
    
    def clean_longitude(self):
        """Clean and validate longitude field"""
        longitude = self.cleaned_data.get('longitude')
        
        # If longitude is empty, return None
        if not longitude:
            return None
        
        try:
            # Convert to float for validation
            lng_value = float(longitude)
            
            # Basic validation for Myanmar coordinates
            if not (92.0 <= lng_value <= 101.0):
                raise forms.ValidationError("Longitude must be within Myanmar (92.0 – 101.0)")
            
            # Round to 6 decimal places to avoid decimal place errors
            from decimal import Decimal, getcontext
            getcontext().prec = 10
            lng_value = Decimal(str(lng_value)).quantize(Decimal('0.000001'))
            
            return lng_value
        except (ValueError, TypeError):
            raise forms.ValidationError("Please provide a valid numeric longitude")
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        
        # Get the destination type
        dest_type = cleaned_data.get('type')
        
        # For cities/towns, ensure parent is not processed
        if dest_type in ['city', 'town']:
            # Remove parent from cleaned_data if it exists
            if 'parent' in cleaned_data:
                del cleaned_data['parent']
        
        # Get latitude and longitude from cleaned_data (already validated in individual field clean methods)
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        # Validate that both coordinates are provided together
        if latitude and not longitude:
            self.add_error('longitude', 'Longitude is required when latitude is provided')
        elif longitude and not latitude:
            self.add_error('latitude', 'Latitude is required when longitude is provided')
        
        # If both coordinates are provided, ensure they are Decimal objects with correct precision
        if latitude and longitude:
            try:
                from decimal import Decimal
                
                # Ensure they are Decimal objects with proper precision
                if not isinstance(latitude, Decimal):
                    latitude = Decimal(str(latitude)).quantize(Decimal('0.000001'))
                    cleaned_data['latitude'] = latitude
                
                if not isinstance(longitude, Decimal):
                    longitude = Decimal(str(longitude)).quantize(Decimal('0.000001'))
                    cleaned_data['longitude'] = longitude
                    
            except Exception as e:
                self.add_error('latitude', f"Error processing coordinates: {str(e)}")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle main image (profile photo) - this is the 'image' field
        if 'image' in self.files:
            instance.image = self.files['image']
        
        # Handle gallery images (8 photos)
        caption_data = {}  # Store captions for gallery images
        
        # Process each gallery image (1-8)
        for i in range(1, 9):
            image_field = f'gallery_image{i}'
            caption_field = f'caption_{i}'
            
            if image_field in self.files:
                image_file = self.files[image_field]
                
                # Generate filename
                filename = f"{instance.name.replace(' ', '_')}_gallery_{i}.jpg"
                
                # Save to the appropriate gallery image field
                gallery_field = getattr(instance, f'gallery_image{i}')
                gallery_field.save(filename, image_file, save=False)
            
            # Store caption
            caption = self.cleaned_data.get(caption_field, '')
            if caption:
                caption_data[f'caption_{i}'] = caption
        
        # Store gallery captions as JSON - Use gallery_captions (not gallery_images)
        if caption_data:
            instance.gallery_captions = caption_data
        
        # Handle parent (only for attractions)
        if instance.type == 'attraction':
            parent_value = self.cleaned_data.get('parent') if 'parent' in self.cleaned_data else None
            if isinstance(parent_value, Destination):
                instance.parent = parent_value
            elif isinstance(parent_value, str) and parent_value:
                # Will be handled in the view to create new parent if needed
                instance._temp_parent_name = parent_value
        else:
            # For cities/towns, ensure parent is None
            instance.parent = None
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance
class AdminEditDestinationForm(forms.ModelForm):
    """Enhanced form for editing destinations with 8 gallery images and captions"""
    
    # Add fields for 8 gallery images
    gallery_image1 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image2 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image3 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image4 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image5 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image6 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image7 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    gallery_image8 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    # Add fields for captions (to be stored in gallery_captions JSON)
    caption_1 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 1'}))
    caption_2 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 2'}))
    caption_3 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 3'}))
    caption_4 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 4'}))
    caption_5 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 5'}))
    caption_6 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 6'}))
    caption_7 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 7'}))
    caption_8 = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description for photo 8'}))
    
    # Add parent as a CharField for text input
    parent = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Bagan, Mandalay, Taunggyi'
        }),
        help_text='Enter the name of the city/town where this attraction is located (for attractions only)'
    )
    
    class Meta:
        model = Destination
        fields = [
            'name', 'region', 'type', 'latitude', 'longitude', 
            'description', 'is_active', 'is_region'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_region': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make latitude and longitude not required at form level
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        
        # If editing an existing instance, populate parent field
        if self.instance and self.instance.pk:
            if self.instance.parent:
                self.initial['parent'] = self.instance.parent.name
            
            # Populate caption fields from gallery_captions JSON
            if self.instance.gallery_captions:
                try:
                    if isinstance(self.instance.gallery_captions, dict):
                        gallery = self.instance.gallery_captions
                        for i in range(1, 9):
                            caption_key = f'caption_{i}'
                            if caption_key in gallery:
                                self.initial[caption_key] = gallery[caption_key]
                except:
                    pass
    
    def clean_parent(self):
        """Clean and validate parent field - only used for attractions"""
        parent_name = self.data.get('parent', '').strip()
        if not parent_name:
            return None
        
        # Try to find existing parent
        try:
            parent = Destination.objects.get(
                Q(name__iexact=parent_name) | 
                Q(name__icontains=parent_name),
                type__in=['city', 'town']
            )
            return parent
        except Destination.DoesNotExist:
            # Return the name as a string - will be handled in the view
            return parent_name
        except Destination.MultipleObjectsReturned:
            # If multiple found, return the first one
            return Destination.objects.filter(
                Q(name__iexact=parent_name) | 
                Q(name__icontains=parent_name),
                type__in=['city', 'town']
            ).first()
    
    def clean_latitude(self):
        """Clean and validate latitude field"""
        latitude = self.cleaned_data.get('latitude')
        
        # If latitude is empty, return None
        if not latitude:
            return None
        
        try:
            # Convert to float for validation
            lat_value = float(latitude)
            
            # Basic validation for Myanmar coordinates
            if not (9.0 <= lat_value <= 28.0):
                raise forms.ValidationError("Latitude must be within Myanmar (9.0 – 28.0)")
            
            # Round to 6 decimal places to avoid decimal place errors
            from decimal import Decimal, getcontext
            getcontext().prec = 10
            lat_value = Decimal(str(lat_value)).quantize(Decimal('0.000001'))
            
            return lat_value
        except (ValueError, TypeError):
            raise forms.ValidationError("Please provide a valid numeric latitude")
    
    def clean_longitude(self):
        """Clean and validate longitude field"""
        longitude = self.cleaned_data.get('longitude')
        
        # If longitude is empty, return None
        if not longitude:
            return None
        
        try:
            # Convert to float for validation
            lng_value = float(longitude)
            
            # Basic validation for Myanmar coordinates
            if not (92.0 <= lng_value <= 101.0):
                raise forms.ValidationError("Longitude must be within Myanmar (92.0 – 101.0)")
            
            # Round to 6 decimal places to avoid decimal place errors
            from decimal import Decimal, getcontext
            getcontext().prec = 10
            lng_value = Decimal(str(lng_value)).quantize(Decimal('0.000001'))
            
            return lng_value
        except (ValueError, TypeError):
            raise forms.ValidationError("Please provide a valid numeric longitude")
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        
        # If type is city or town, ensure parent is not set
        dest_type = cleaned_data.get('type')
        if dest_type in ['city', 'town']:
            # Remove any parent value for cities/towns
            if 'parent' in cleaned_data:
                del cleaned_data['parent']
        
        # Get latitude and longitude from cleaned_data
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        
        # Validate that both coordinates are provided together
        if latitude and not longitude:
            self.add_error('longitude', 'Longitude is required when latitude is provided')
        elif longitude and not latitude:
            self.add_error('latitude', 'Latitude is required when longitude is provided')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle main image (profile photo) - Check files, not just form data
        if 'image' in self.files:
            instance.image = self.files['image']
        
        # Handle gallery images (8 photos)
        caption_data = {}
        
        # Process each gallery image (1-8)
        for i in range(1, 9):
            image_field = f'gallery_image{i}'
            caption_field = f'caption_{i}'
            
            if image_field in self.files:
                image_file = self.files[image_field]
                
                # Generate filename
                filename = f"{instance.name.replace(' ', '_')}_gallery_{i}.jpg"
                
                # Save to the appropriate gallery image field
                gallery_field = getattr(instance, f'gallery_image{i}')
                gallery_field.save(filename, image_file, save=False)
            
            # Store caption
            caption = self.cleaned_data.get(caption_field, '')
            if caption:
                caption_data[f'caption_{i}'] = caption
        
        # Store gallery captions as JSON in gallery_captions
        if caption_data:
            if instance.gallery_captions and isinstance(instance.gallery_captions, dict):
                instance.gallery_captions.update(caption_data)
            else:
                instance.gallery_captions = caption_data
        
        # Handle parent (only for attractions)
        if instance.type == 'attraction':
            parent_value = self.cleaned_data.get('parent')
            if isinstance(parent_value, Destination):
                instance.parent = parent_value
            elif isinstance(parent_value, str) and parent_value:
                # Will be handled in the view to create new parent if needed
                instance._temp_parent_name = parent_value
        else:
            # For cities/towns, ensure parent is None
            instance.parent = None
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance
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
# ========== SYSTEM SETTINGS FORM ==========
class SystemSettingsForm(forms.ModelForm):
    """Form for system settings"""
    
    class Meta:
        model = SystemSettings
        fields = '__all__'
        widgets = {
            'site_name': forms.TextInput(attrs={'class': 'form-control'}),
            'site_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'default_currency': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('MMK', 'MMK - Myanmar Kyat'),
                ('USD', 'USD - US Dollar'),
                ('EUR', 'EUR - Euro'),
                ('SGD', 'SGD - Singapore Dollar'),
                ('THB', 'THB - Thai Baht'),
            ]),
            'maintenance_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'smtp_host': forms.TextInput(attrs={'class': 'form-control'}),
            'smtp_port': forms.NumberInput(attrs={'class': 'form-control'}),
            'email_address': forms.EmailInput(attrs={'class': 'form-control'}),
            'email_password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current'}),
            'enable_email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password field not required (so it can be left blank)
        self.fields['email_password'].required = False