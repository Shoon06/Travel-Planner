from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.utils.text import slugify
from django import forms
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image, ImageDraw
import random
from .models import Destination, Hotel, Flight, BusService, CarRental, TripPlan, Airline, BookedSeat

# ==================== FORMS ====================
class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'
        widgets = {
            'amenities': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter amenities separated by commas'}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = '__all__'

class BusServiceForm(forms.ModelForm):
    class Meta:
        model = BusService
        fields = '__all__'

class CarRentalForm(forms.ModelForm):
    class Meta:
        model = CarRental
        fields = '__all__'

class TripPlanForm(forms.ModelForm):
    class Meta:
        model = TripPlan
        fields = '__all__'

# ==================== AIRLINE ADMIN ====================
@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'is_default_for_domestic']
    list_filter = ['is_active', 'is_default_for_domestic']
    search_fields = ['name', 'code']
    list_per_page = 20

# ==================== BOOKED SEAT ADMIN ====================
@admin.register(BookedSeat)
class BookedSeatAdmin(admin.ModelAdmin):
    list_display = ['transport_type', 'transport_id', 'seat_number', 'trip', 'booked_by', 'booking_time', 'is_cancelled']
    list_filter = ['transport_type', 'is_cancelled', 'booking_time']
    search_fields = ['seat_number', 'transport_id', 'booked_by__username']
    list_per_page = 20

# ==================== DESTINATION ADMIN ====================
@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    form = DestinationForm
    list_display = ['name', 'region', 'type', 'image_preview', 'is_active', 'created_at', 'destination_actions']
    search_fields = ['name', 'region', 'description']
    list_filter = ['type', 'region', 'is_active', 'created_at']
    ordering = ['name']
    list_per_page = 20
    actions = ['activate_destinations', 'deactivate_destinations', 'fetch_sample_images', 'duplicate_destinations']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'region', 'type', 'description')
        }),
        ('Image', {
            'fields': ('image', 'image_preview'),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['image_preview', 'created_at', 'updated_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<img src="{}" style="max-height: 150px; max-width: 200px; border-radius: 8px; border: 1px solid #ddd;" />'
                '<br><small>{}</small>'
                '</div>', 
                obj.image.url, 
                obj.image.name
            )
        return format_html(
            '<div style="margin: 10px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; text-align: center;">'
            '<i class="fas fa-image fa-2x text-muted"></i><br>'
            '<span class="text-muted">No image uploaded</span>'
            '</div>'
        )
    image_preview.short_description = 'Image Preview'
    
    def destination_actions(self, obj):
        return format_html(
            '<div class="btn-group" role="group">'
            '<a href="{}" class="btn btn-sm btn-outline-primary">Edit</a>'
            '<a href="/destination/{}/" class="btn btn-sm btn-outline-success" style="margin-left: 5px;" target="_blank">View</a>'
            '</div>',
            reverse('admin:planner_destination_change', args=[obj.id]),
            obj.id
        )
    destination_actions.short_description = 'Actions'
    
    def fetch_sample_images(self, request, queryset):
        success_count = 0
        for destination in queryset:
            try:
                if not destination.image:
                    # Create a beautiful gradient image with destination name
                    img = Image.new('RGB', (800, 600), color=(
                        random.randint(50, 150),
                        random.randint(50, 150),
                        random.randint(50, 150)
                    ))
                    
                    # Create gradient
                    for i in range(600):
                        r = int(img.getpixel((0, i))[0] * (600 - i) / 600)
                        g = int(img.getpixel((0, i))[1] * (600 - i) / 600)
                        b = int(img.getpixel((0, i))[2] * (600 - i) / 600)
                        for j in range(800):
                            img.putpixel((j, i), (r, g, b))
                    
                    draw = ImageDraw.Draw(img)
                    
                    # Draw destination name
                    try:
                        from PIL import ImageFont
                        font = ImageFont.truetype("arial.ttf", 60)
                    except:
                        font = ImageFont.load_default()
                    
                    # Draw text with shadow
                    text = destination.name
                    draw.text((402, 302), text, font=font, fill=(0, 0, 0))
                    draw.text((400, 300), text, font=font, fill=(255, 255, 255))
                    
                    # Draw region
                    try:
                        small_font = ImageFont.truetype("arial.ttf", 30)
                    except:
                        small_font = ImageFont.load_default()
                    region_text = destination.region
                    draw.text((402, 372), region_text, font=small_font, fill=(0, 0, 0))
                    draw.text((400, 370), region_text, font=small_font, fill=(200, 200, 200))
                    
                    # Save to BytesIO
                    img_io = BytesIO()
                    img.save(img_io, 'JPEG', quality=85)
                    img_io.seek(0)
                    
                    # Save to destination
                    destination.image.save(
                        f'{slugify(destination.name)}_preview.jpg',
                        ContentFile(img_io.read()),
                        save=True
                    )
                    
                    success_count += 1
                    self.message_user(
                        request, 
                        f'Created image for {destination.name}', 
                        level=messages.SUCCESS
                    )
            except Exception as e:
                self.message_user(
                    request, 
                    f'Error for {destination.name}: {str(e)}', 
                    level=messages.ERROR
                )
        
        self.message_user(
            request, 
            f'Successfully created images for {success_count} destinations', 
            level=messages.SUCCESS
        )
    fetch_sample_images.short_description = "Create sample images"
    
    def duplicate_destinations(self, request, queryset):
        for destination in queryset:
            try:
                new_dest = Destination.objects.create(
                    name=f"{destination.name} (Copy)",
                    region=destination.region,
                    type=destination.type,
                    description=destination.description,
                    image=destination.image if destination.image else None,
                    is_active=destination.is_active
                )
                self.message_user(
                    request, 
                    f'Duplicated {destination.name} to {new_dest.name}', 
                    level=messages.SUCCESS
                )
            except Exception as e:
                self.message_user(
                    request, 
                    f'Error duplicating {destination.name}: {str(e)}', 
                    level=messages.ERROR
                )
    duplicate_destinations.short_description = "Duplicate selected"
    
    def activate_destinations(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} destinations activated successfully.', level=messages.SUCCESS)
    activate_destinations.short_description = "Activate selected"
    
    def deactivate_destinations(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} destinations deactivated successfully.', level=messages.SUCCESS)
    deactivate_destinations.short_description = "Deactivate selected"

# ==================== HOTEL ADMIN ====================
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    form = HotelForm
    list_display = ['name', 'destination', 'price_per_night', 'rating', 'image_preview', 'is_active', 'hotel_actions']
    list_filter = ['is_active', 'destination', 'rating', 'created_at']
    search_fields = ['name', 'destination__name', 'address', 'description']
    ordering = ['name']
    list_per_page = 20
    actions = ['activate_hotels', 'deactivate_hotels', 'increase_prices_10', 'add_sample_images']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'destination', 'address', 'description')
        }),
        ('Pricing', {
            'fields': ('price_per_night',)
        }),
        ('Ratings & Reviews', {
            'fields': ('rating', 'review_count')
        }),
        ('Amenities', {
            'fields': ('amenities',),
            'classes': ('collapse',)
        }),
        ('Images', {
            'fields': ('image', 'image_preview'),
            'classes': ('wide',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at')
        }),
    )
    
    readonly_fields = ['image_preview', 'created_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<img src="{}" style="max-height: 150px; max-width: 200px; border-radius: 8px; border: 1px solid #ddd;" />'
                '<br><small>{}</small>'
                '</div>', 
                obj.image.url, 
                obj.image.name
            )
        return format_html(
            '<div style="margin: 10px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; text-align: center;">'
            '<i class="fas fa-hotel fa-2x text-muted"></i><br>'
            '<span class="text-muted">No hotel image</span>'
            '</div>'
        )
    image_preview.short_description = 'Hotel Image'
    
    def hotel_actions(self, obj):
        return format_html(
            '<div class="btn-group" role="group">'
            '<a href="{}" class="btn btn-sm btn-outline-primary">Edit</a>'
            '<a href="/hotel/{}/" class="btn btn-sm btn-outline-success" style="margin-left: 5px;" target="_blank">View</a>'
            '</div>',
            reverse('admin:planner_hotel_change', args=[obj.id]),
            obj.id
        )
    hotel_actions.short_description = 'Actions'
    
    def increase_prices_10(self, request, queryset):
        for hotel in queryset:
            hotel.price_per_night = hotel.price_per_night * 1.1
            hotel.save()
        self.message_user(request, f'Increased prices for {queryset.count()} hotels by 10%', level=messages.SUCCESS)
    increase_prices_10.short_description = "Increase prices by 10 percent"
    
    def add_sample_images(self, request, queryset):
        for hotel in queryset:
            if not hotel.image:
                try:
                    # Create a hotel-themed image
                    img = Image.new('RGB', (800, 600), color=(240, 240, 240))
                    draw = ImageDraw.Draw(img)
                    
                    # Draw hotel building
                    building_color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
                    draw.rectangle([200, 200, 600, 500], fill=building_color, outline=(0, 0, 0), width=2)
                    
                    # Draw windows
                    for i in range(4):
                        for j in range(3):
                            window_x = 250 + i * 100
                            window_y = 250 + j * 80
                            draw.rectangle([window_x, window_y, window_x + 50, window_y + 50], 
                                         fill=(255, 255, 200), outline=(0, 0, 0), width=1)
                    
                    # Draw hotel name
                    try:
                        from PIL import ImageFont
                        font = ImageFont.truetype("arial.ttf", 40)
                    except:
                        font = ImageFont.load_default()
                    
                    draw.text((250, 100), hotel.name[:20], font=font, fill=(0, 0, 0))
                    
                    # Save image
                    img_io = BytesIO()
                    img.save(img_io, 'JPEG', quality=85)
                    img_io.seek(0)
                    
                    hotel.image.save(
                        f'{slugify(hotel.name)}_hotel.jpg',
                        ContentFile(img_io.read()),
                        save=True
                    )
                    
                    self.message_user(
                        request, 
                        f'Created image for {hotel.name}', 
                        level=messages.SUCCESS
                    )
                except Exception as e:
                    self.message_user(
                        request, 
                        f'Error creating image for {hotel.name}: {str(e)}', 
                        level=messages.ERROR
                    )
    add_sample_images.short_description = "Add hotel images"
    
    def activate_hotels(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} hotels activated successfully.', level=messages.SUCCESS)
    activate_hotels.short_description = "Activate hotels"
    
    def deactivate_hotels(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} hotels deactivated successfully.', level=messages.SUCCESS)
    deactivate_hotels.short_description = "Deactivate hotels"

# ==================== FLIGHT ADMIN ====================
@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    form = FlightForm
    list_display = ['airline', 'flight_number', 'departure', 'arrival', 'departure_time', 'price', 'available_seats', 'is_active', 'flight_actions']
    list_filter = ['category', 'airline', 'is_active', 'departure', 'arrival', 'created_at']
    search_fields = ['airline', 'flight_number', 'departure__name', 'arrival__name']
    ordering = ['departure_time']
    list_per_page = 20
    actions = ['activate_flights', 'deactivate_flights', 'increase_price_10', 'duplicate_flights']
    
    fieldsets = (
        ('Flight Details', {
            'fields': ('airline', 'flight_number')
        }),
        ('Route & Schedule', {
            'fields': ('departure', 'arrival', 'departure_time', 'arrival_time', 'duration')
        }),
        ('Pricing & Capacity', {
            'fields': ('price', 'category', 'total_seats', 'available_seats')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def flight_actions(self, obj):
        return format_html(
            '<div class="btn-group" role="group">'
            '<a href="{}" class="btn btn-sm btn-outline-primary">Edit</a>'
            '</div>',
            reverse('admin:planner_flight_change', args=[obj.id])
        )
    flight_actions.short_description = 'Actions'
    
    def increase_price_10(self, request, queryset):
        for flight in queryset:
            flight.price = flight.price * 1.1
            flight.save()
        self.message_user(request, f'{queryset.count()} flight prices increased by 10%.', level=messages.SUCCESS)
    increase_price_10.short_description = "Increase prices by 10 percent"
    
    def duplicate_flights(self, request, queryset):
        for flight in queryset:
            try:
                Flight.objects.create(
                    airline=flight.airline,
                    flight_number=f"{flight.flight_number}-COPY",
                    departure=flight.departure,
                    arrival=flight.arrival,
                    departure_time=flight.departure_time,
                    arrival_time=flight.arrival_time,
                    duration=flight.duration,
                    price=flight.price,
                    category=flight.category,
                    total_seats=flight.total_seats,
                    available_seats=flight.available_seats,
                    is_active=flight.is_active
                )
            except Exception as e:
                self.message_user(request, f'Error duplicating {flight.flight_number}: {str(e)}', level=messages.ERROR)
    duplicate_flights.short_description = "Duplicate flights"
    
    def activate_flights(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} flights activated successfully.', level=messages.SUCCESS)
    activate_flights.short_description = "Activate flights"
    
    def deactivate_flights(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} flights deactivated successfully.', level=messages.SUCCESS)
    deactivate_flights.short_description = "Deactivate flights"

# ==================== BUS SERVICE ADMIN ====================
@admin.register(BusService)
class BusServiceAdmin(admin.ModelAdmin):
    form = BusServiceForm
    list_display = ['company', 'departure', 'arrival', 'departure_time', 'bus_type', 'price', 'available_seats', 'is_active', 'bus_actions']
    list_filter = ['bus_type', 'company', 'is_active', 'departure', 'arrival', 'created_at']
    search_fields = ['company', 'departure__name', 'arrival__name']
    ordering = ['departure_time']
    list_per_page = 20
    actions = ['activate_buses', 'deactivate_buses']
    
    fieldsets = (
        ('Bus Details', {
            'fields': ('company', 'bus_number')
        }),
        ('Route & Schedule', {
            'fields': ('departure', 'arrival', 'departure_time', 'duration')
        }),
        ('Pricing & Capacity', {
            'fields': ('price', 'bus_type', 'total_seats', 'available_seats')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def bus_actions(self, obj):
        return format_html(
            '<div class="btn-group" role="group">'
            '<a href="{}" class="btn btn-sm btn-outline-primary">Edit</a>'
            '</div>',
            reverse('admin:planner_busservice_change', args=[obj.id])
        )
    bus_actions.short_description = 'Actions'
    
    def activate_buses(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} buses activated successfully.', level=messages.SUCCESS)
    activate_buses.short_description = "Activate buses"
    
    def deactivate_buses(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} buses deactivated successfully.', level=messages.SUCCESS)
    deactivate_buses.short_description = "Deactivate buses"

# ==================== CAR RENTAL ADMIN ====================
@admin.register(CarRental)
class CarRentalAdmin(admin.ModelAdmin):
    form = CarRentalForm
    list_display = ['company', 'car_model', 'car_type', 'seats', 'price_per_day', 'location', 'is_available', 'car_actions']
    list_filter = ['car_type', 'company', 'is_available', 'location', 'created_at']
    search_fields = ['company', 'car_model', 'location__name']
    ordering = ['company', 'car_model']
    list_per_page = 20
    actions = ['make_available', 'make_unavailable']
    
    fieldsets = (
        ('Car Details', {
            'fields': ('company', 'car_model', 'car_type', 'seats')
        }),
        ('Pricing & Features', {
            'fields': ('price_per_day', 'features')
        }),
        ('Location & Availability', {
            'fields': ('location', 'is_available')
        }),
    )
    
    def car_actions(self, obj):
        return format_html(
            '<div class="btn-group" role="group">'
            '<a href="{}" class="btn btn-sm btn-outline-primary">Edit</a>'
            '</div>',
            reverse('admin:planner_carrental_change', args=[obj.id])
        )
    car_actions.short_description = 'Actions'
    
    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} cars made available.', level=messages.SUCCESS)
    make_available.short_description = "Make available"
    
    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} cars made unavailable.', level=messages.SUCCESS)
    make_unavailable.short_description = "Make unavailable"

# ==================== TRIP PLAN ADMIN (CORRECTED) ====================
@admin.register(TripPlan)
class TripPlanAdmin(admin.ModelAdmin):
    form = TripPlanForm
    list_display = ['id', 'get_user', 'get_destination', 'start_date', 'end_date', 'get_status', 'total_cost_display', 'trip_actions']
    list_filter = ['status', 'budget_range', 'created_at', 'start_date']
    search_fields = ['user__username', 'destination__name', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'total_cost_calculation']
    list_per_page = 20
    actions = ['mark_as_completed', 'mark_as_cancelled', 'mark_as_booked']
    
    fieldsets = (
        ('Trip Information', {
            'fields': ('user', 'origin', 'destination', 'start_date', 'end_date', 'travelers', 'budget_range')
        }),
        ('Accommodation', {
            'fields': ('accommodation_type', 'selected_hotel')
        }),
        ('Transportation', {
            'fields': ('transportation_preference', 'selected_transport')
        }),
        ('Status & Dates', {
            'fields': ('status', 'created_at', 'updated_at', 'total_cost_calculation')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_user(self, obj):
        return obj.user.username
    get_user.short_description = 'User'
    get_user.admin_order_field = 'user__username'
    
    def get_destination(self, obj):
        return f"{obj.destination.name} ({obj.destination.region})"
    get_destination.short_description = 'Destination'
    get_destination.admin_order_field = 'destination__name'
    
    def get_status(self, obj):
        status_colors = {
            'draft': 'secondary',
            'planning': 'info',
            'booked': 'success',
            'completed': 'primary',
            'cancelled': 'danger'
        }
        color = status_colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status.short_description = 'Status'
    get_status.admin_order_field = 'status'
    
    def total_cost_display(self, obj):
        total_cost = obj.get_total_cost_in_mmk()
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">{:,} MMK</span>',
            total_cost
        )
    total_cost_display.short_description = 'Total Cost'
    
    def total_cost_calculation(self, obj):
        total_cost = obj.get_total_cost_in_mmk()
        breakdown = obj.get_cost_breakdown()
        
        html = """
        <div style="padding: 15px; background: #f8f9fa; border-radius: 8px;">
            <h5 style="margin-bottom: 15px;">Cost Breakdown</h5>
            <table style="width: 100%;">
        """
        
        if breakdown['hotel'] > 0:
            html += f"""
            <tr>
                <td style="padding: 5px;">Hotel Cost:</td>
                <td style="padding: 5px; text-align: right;">{breakdown['hotel']:,} MMK</td>
            </tr>
            """
        
        if breakdown['transport'] > 0:
            html += f"""
            <tr>
                <td style="padding: 5px;">Transport Cost:</td>
                <td style="padding: 5px; text-align: right;">{breakdown['transport']:,} MMK</td>
            </tr>
            """
        
        html += f"""
            <tr>
                <td style="padding: 5px;">Activities & Food:</td>
                <td style="padding: 5px; text-align: right;">{breakdown['destination']:,} MMK</td>
            </tr>
        """
        
        if breakdown['additional_travelers'] > 0:
            html += f"""
            <tr>
                <td style="padding: 5px;">Additional Travelers:</td>
                <td style="padding: 5px; text-align: right;">{breakdown['additional_travelers']:,} MMK</td>
            </tr>
            """
        
        html += f"""
            <tr style="border-top: 2px solid #dee2e6;">
                <td style="padding: 5px; font-weight: bold;">Total Cost:</td>
                <td style="padding: 5px; text-align: right; font-weight: bold; color: #28a745;">{total_cost:,} MMK</td>
            </tr>
            </table>
        </div>
        """
        
        return format_html(html)
    total_cost_calculation.short_description = 'Cost Breakdown'
    
    def trip_actions(self, obj):
        return format_html(
            '<div class="btn-group" role="group">'
            '<a href="{}" class="btn btn-sm btn-outline-primary">Edit</a>'
            '</div>',
            reverse('admin:planner_tripplan_change', args=[obj.id])
        )
    trip_actions.short_description = 'Actions'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} trips marked as completed.', level=messages.SUCCESS)
    mark_as_completed.short_description = "Mark as completed"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} trips marked as cancelled.', level=messages.SUCCESS)
    mark_as_cancelled.short_description = "Mark as cancelled"
    
    def mark_as_booked(self, request, queryset):
        updated = queryset.update(status='booked')
        self.message_user(request, f'{updated} trips marked as booked.', level=messages.SUCCESS)
    mark_as_booked.short_description = "Mark as booked"

# ==================== CUSTOM ADMIN SITE ====================
admin.site.site_header = "Myanmar Travel Planner Administration"
admin.site.site_title = "Myanmar Travel Admin"
admin.site.index_title = "Welcome to Myanmar Travel Planner Admin"