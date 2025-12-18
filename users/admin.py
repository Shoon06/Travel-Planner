from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.html import format_html

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('user_type', 'profile_picture', 'bio', 'phone_number', 'location')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('user_type', 'profile_picture', 'bio', 'phone_number', 'location')
        }),
    )
    
    actions = ['make_admin', 'make_user']
    
    def make_admin(self, request, queryset):
        queryset.update(user_type='admin')
        self.message_user(request, f"{queryset.count()} users promoted to admin.")
    make_admin.short_description = "Promote selected users to Admin"
    
    def make_user(self, request, queryset):
        queryset.update(user_type='user')
        self.message_user(request, f"{queryset.count()} users demoted to regular user.")
    make_user.short_description = "Demote selected users to Regular User"

admin.site.register(CustomUser, CustomUserAdmin)