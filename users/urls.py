from django.urls import path
from . import views
from . import views_admin

app_name = 'users'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin URLs
    path('admin/dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views_admin.AdminUserListView.as_view(), name='admin_dashboard_users'),
    path('admin/users/add/', views_admin.AdminAddUserView.as_view(), name='admin_add_user'),
    path('admin/users/roles/', views_admin.AdminUserRolesView.as_view(), name='admin_user_roles'),
    path('admin/users/update-role/', views_admin.admin_update_user_role, name='admin_update_user_role'),
    path('admin/users/toggle-active/<int:user_id>/', views_admin.admin_toggle_user_active, name='admin_toggle_user_active'),
    
    # Trip Management
    path('admin/trips/', views_admin.AdminTripListView.as_view(), name='admin_trip_list'),
    path('admin/trips/<int:trip_id>/', views_admin.admin_trip_details, name='admin_trip_details'),
    path('admin/trips/analytics/', views_admin.AdminTripAnalyticsView.as_view(), name='admin_trip_analytics'),
    
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
    
    # System Settings
    path('admin/system-settings/', views_admin.admin_system_settings, name='admin_system_settings'),
    path('admin/database-backup/', views_admin.admin_database_backup, name='admin_database_backup'),
    
    # Trip Content (Redirect)
    path('admin/trip-content/', views_admin.admin_trip_content_view, name='admin_trip_content'),
]