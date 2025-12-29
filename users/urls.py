# C:\Users\ASUS\MyanmarTravelPlanner\users\urls.py
from django.urls import path
from . import views
from . import views_admin
from .views_admin import admin_add_hotel_with_map

app_name = 'users'

urlpatterns = [
    # Authentication URLs
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.force_logout_view, name='logout'),
    path('check-email/', views.check_email_availability, name='check_email'),
    
    # Admin Dashboard - Using function-based view
    path('admin/dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),
    
    # Hotel Management - Using function-based views
    path('admin/hotels/', views_admin.admin_hotels, name='admin_hotels'),
    path('admin/hotels/add/', views_admin.admin_add_hotel, name='admin_add_hotel'),
    path('admin/hotels/edit/<int:hotel_id>/', views_admin.admin_edit_hotel, name='admin_edit_hotel'),
    path('admin/hotels/delete/<int:hotel_id>/', views_admin.admin_delete_hotel, name='admin_delete_hotel'),
    
    # User Management - Using class-based views
    path('admin/users/', views_admin.AdminUserListView.as_view(), name='admin_dashboard_users'),
    path('admin/users/add/', views_admin.AdminAddUserView.as_view(), name='admin_add_user'),
    path('admin/users/roles/', views_admin.AdminUserRolesView.as_view(), name='admin_dashboard_user_roles'),
    path('admin/users/<int:user_id>/toggle-active/', views_admin.admin_toggle_user_active, name='admin_toggle_user_active'),
    path('admin/users/update-role/', views_admin.admin_update_user_role, name='admin_update_user_role'),
    
    # Trip Management - Using class-based views
    path('admin/trips/', views_admin.AdminTripListView.as_view(), name='admin_dashboard_trips'),
    path('admin/trips/analytics/', views_admin.AdminTripAnalyticsView.as_view(), name='admin_dashboard_trip_analytics'),
    path('admin/trips/content/', views_admin.admin_trip_content_view, name='admin_dashboard_trip_content'),
    
    # Content Management - Mix of function and class-based
    path('admin/content/', views_admin.AdminContentView.as_view(), name='admin_content'),
    path('admin/destinations/', views_admin.AdminDestinationsView.as_view(), name='admin_destinations'),
    path('admin/destinations/add/', views_admin.AdminAddDestinationView.as_view(), name='admin_add_destination'),
    
    # Flights and Buses
    path('admin/flights/', views_admin.AdminFlightsView.as_view(), name='admin_flights'),
    path('admin/flights/add/', views_admin.AdminAddFlightView.as_view(), name='admin_add_flight'),
    path('admin/buses/', views_admin.AdminBusesView.as_view(), name='admin_buses'),
    path('admin/buses/add/', views_admin.AdminAddBusView.as_view(), name='admin_add_bus'),
    
    # System Settings
    path('admin/settings/', views_admin.AdminSystemSettingsView.as_view(), name='admin_system_settings'),
    path('admin/database/backup/', views_admin.AdminDatabaseBackupView.as_view(), name='admin_database_backup'),
    path('admin/hotels/add-with-map/', admin_add_hotel_with_map, name='admin_add_hotel_with_map'),]