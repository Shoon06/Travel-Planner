from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.contrib import messages
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'get_user_type_display', 'is_active', 'date_joined', 'user_actions']
    list_filter = ['user_type', 'is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    list_per_page = 20
    actions = ['make_admin', 'make_user', 'activate_users', 'deactivate_users']
    
    fieldsets = (
        ('Login Credentials', {
            'fields': ('username', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'location', 'bio')
        }),
        ('Profile Picture', {
            'fields': ('profile_picture', 'profile_picture_preview'),
            'classes': ('wide',)
        }),
        ('Permissions & Status', {
            'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'is_active', 'is_staff'),
        }),
    )
    
    readonly_fields = ['profile_picture_preview', 'last_login', 'date_joined']
    
    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px; border-radius: 10px;" />',
                obj.profile_picture.url
            )
        return format_html(
            '<div style="padding: 20px; background: #f8f9fa; border-radius: 10px; text-align: center;">'
            '<i class="fas fa-user-circle fa-3x text-muted"></i><br>'
            '<span class="text-muted">No profile picture</span>'
            '</div>'
        )
    profile_picture_preview.short_description = 'Profile Picture'
    
    def get_user_type_display(self, obj):
        if obj.user_type == 'admin':
            return format_html(
                '<span class="badge" style="background: linear-gradient(135deg, #dc3545, #c82333); color: white; padding: 4px 10px; border-radius: 12px;">'
                '<i class="fas fa-crown me-1"></i>Admin</span>'
            )
        else:
            return format_html(
                '<span class="badge" style="background: linear-gradient(135deg, #007bff, #0056b3); color: white; padding: 4px 10px; border-radius: 12px;">'
                '<i class="fas fa-user me-1"></i>User</span>'
            )
    get_user_type_display.short_description = 'User Type'
    
    def user_actions(self, obj):
        return format_html(
            '<div class="btn-group" role="group">'
            '<a href="{}" class="btn btn-sm btn-outline-primary">Edit</a>'
            '<a href="/admin/users/customuser/{}/delete/" class="btn btn-sm btn-outline-danger" style="margin-left: 5px;" onclick="return confirm(\'Are you sure?\')">Delete</a>'
            '</div>',
            f'/admin/users/customuser/{obj.id}/change/',
            obj.id
        )
    user_actions.short_description = 'Actions'
    
    def make_admin(self, request, queryset):
        updated = queryset.update(user_type='admin', is_staff=True)
        self.message_user(request, f'{updated} users promoted to admin.', level=messages.SUCCESS)
    make_admin.short_description = "👑 Promote to Admin"
    
    def make_user(self, request, queryset):
        updated = queryset.update(user_type='user', is_staff=False)
        self.message_user(request, f'{updated} users demoted to regular user.', level=messages.SUCCESS)
    make_user.short_description = "👤 Demote to User"
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated.', level=messages.SUCCESS)
    activate_users.short_description = "✅ Activate users"
    
    def deactivate_users(self, request, queryset):
        # Prevent deactivating yourself
        filtered_queryset = queryset.exclude(id=request.user.id)
        updated = filtered_queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated.', level=messages.SUCCESS)
    deactivate_users.short_description = "❌ Deactivate users"

admin.site.register(CustomUser, CustomUserAdmin)