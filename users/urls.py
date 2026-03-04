from django.urls import path
from . import views
from . import views_admin
from posts import views as posts_views 
from .views import admin_how_it_works
from .views_admin_actions import delete_content, update_content_status
from .views_admin import (
    admin_trip_list,
    admin_trip_detail,
    admin_delete_trip,
    admin_update_trip_status,
    admin_trip_analytics
)

app_name = 'users'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # User Role Management (ONLY ONE PATH FOR EACH!)
    path('admin/users/roles/', views_admin.admin_user_roles, name='admin_user_roles'),
    path('posts/admin/delete/<int:post_id>/', 
         posts_views.admin_delete_post,  # Use the imported posts_views
         name='admin_delete_post'),
    # Destination Management - Separate URLs for City/Town and Attraction
    path('admin/destinations/add-city/', views_admin.admin_add_city, name='admin_add_city'),
    path('admin/destinations/add-attraction/', views_admin.admin_add_attraction, name='admin_add_attraction'),
    # Admin URLs
    path('admin/dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),
    path('admin/how-it-works/', admin_how_it_works, name='admin_how_it_works'),
    
    # User Management
    path('admin/users/', views_admin.AdminUserListView.as_view(), name='admin_dashboard_users'),
    path('admin/users/add/', views_admin.AdminAddUserView.as_view(), name='admin_add_user'),
    path('admin/users/<int:user_id>/edit/', views_admin.admin_edit_user, name='admin_edit_user'),
    path('admin/users/toggle-active/<int:user_id>/', views_admin.admin_toggle_user_active, name='admin_toggle_user_active'),
    
    # Trip Management
    path('admin/trips/', admin_trip_list, name='admin_trip_list'),
    path('admin/trips/<int:trip_id>/', admin_trip_detail, name='admin_trip_detail'),
    path('admin/trips/<int:trip_id>/edit/', views_admin.admin_edit_trip, name='admin_edit_trip'),
    path('admin/trips/<int:trip_id>/delete/', admin_delete_trip, name='admin_delete_trip'),
    path('admin/trips/<int:trip_id>/update-status/', admin_update_trip_status, name='admin_update_trip_status'),
    path('admin/trips/analytics/', admin_trip_analytics, name='admin_trip_analytics'),
    # Replace the old edit URL with these two new ones
    path('admin/destinations/<int:destination_id>/edit-city/', views_admin.admin_edit_city, name='admin_edit_city'),
    path('admin/destinations/<int:destination_id>/edit-attraction/', views_admin.admin_edit_attraction, name='admin_edit_attraction'),
# Keep the old one for backward compatibility or remove it
# path('admin/destinations/<int:destination_id>/edit/', views_admin.admin_edit_destination, name='admin_edit_destination'),
    # Content Actions
    path('admin/delete/<str:content_type>/<int:content_id>/', delete_content, name='admin_delete_content'),
    path('admin/update-status/<str:content_type>/<int:content_id>/', update_content_status, name='admin_update_content_status'),
    
    # Content Management
    path('admin/content/', views_admin.admin_content, name='admin_content'),
    path('admin/destinations/', views_admin.admin_destinations, name='admin_destinations'),
    path('admin/destinations/add/', views_admin.admin_add_destination, name='admin_add_destination'),
    path('admin/destinations/<int:destination_id>/edit/', views_admin.admin_edit_destination, name='admin_edit_destination'),
    path('admin/destinations/<int:destination_id>/delete/', views_admin.admin_delete_destination, name='admin_delete_destination'),
    
    # Hotel Management
    path('admin/hotels/', views_admin.admin_hotels, name='admin_hotels'),
    path('admin/hotels/add/', views_admin.admin_add_hotel, name='admin_add_hotel'),
    path('admin/hotels/add-with-map/', views_admin.admin_add_hotel_with_map, name='admin_add_hotel_with_map'),
    path('admin/hotels/<int:hotel_id>/edit/', views_admin.admin_edit_hotel, name='admin_edit_hotel'),
    path('admin/hotels/<int:hotel_id>/delete/', views_admin.admin_delete_hotel, name='admin_delete_hotel'),
    
    # Flight Management
    path('admin/flights/', views_admin.admin_flights, name='admin_flights'),
    path('admin/flights/add/', views_admin.admin_add_flight, name='admin_add_flight'),
    path('admin/flights/<int:flight_id>/edit/', views_admin.admin_edit_flight, name='admin_edit_flight'),
    path('admin/flights/<int:flight_id>/delete/', views_admin.admin_delete_flight, name='admin_delete_flight'),
    
    # Bus Management
    path('admin/buses/', views_admin.admin_buses, name='admin_buses'),
    path('admin/buses/add/', views_admin.admin_add_bus, name='admin_add_bus'),
    path('admin/buses/<int:bus_id>/edit/', views_admin.admin_edit_bus, name='admin_edit_bus'),
    
    # Car Rental Management
    path('admin/cars/', views_admin.admin_cars, name='admin_cars'),
    path('admin/cars/add/', views_admin.admin_add_car, name='admin_add_car'),
    path('admin/cars/<int:car_id>/edit/', views_admin.admin_edit_car, name='admin_edit_car'),
    
    # Airline Management
    path('admin/airlines/', views_admin.admin_airlines, name='admin_airlines'),
    path('admin/airlines/add/', views_admin.admin_add_airline, name='admin_add_airline'),
    path('admin/airlines/<int:airline_id>/edit/', views_admin.admin_edit_airline, name='admin_edit_airline'),
    
    # Schedule Management
    path('admin/schedules/', views_admin.admin_schedules, name='admin_schedules'),
    
    # System Settings
    path('admin/system-settings/', views_admin.admin_system_settings, name='admin_system_settings'),
    path('admin/database-backup/', views_admin.admin_database_backup, name='admin_database_backup'),
    
    # Trip Content (Redirect)
    path('admin/trip-content/', views_admin.admin_trip_content_view, name='admin_trip_content'),
    # Add these to your urlpatterns list
path('admin/destinations/<int:destination_id>/toggle-active/', 
     views_admin.admin_toggle_destination_active, 
     name='admin_toggle_destination_active'),
path('admin/destinations/<int:destination_id>/delete-ajax/', 
     views_admin.admin_delete_destination_ajax, 
     name='admin_delete_destination_ajax'),
path('posts/admin/delete/<int:post_id>/', 
     posts_views.admin_delete_post, 
     name='admin_delete_post'),
]