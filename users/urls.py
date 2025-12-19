from django.urls import path
from . import views
from .views_admin import (
    AdminDashboardView, AdminUserListView, AdminUserRoleManagementView, 
    AdminTripListView, AdminTripAnalyticsView, AdminContentManagementView, 
    AdminDatabaseBackupView, AdminAddUserView  # Add AdminAddUserView here
)
from . import views_admin_actions
from django.contrib.auth.views import LogoutView

app_name = 'users'

urlpatterns = [
    # Authentication URLs
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('force-logout/', views.force_logout_view, name='force_logout'),
    
    # Email availability check
    path('check-email/', views.check_email_availability, name='check_email_availability'),
    
    # Admin Dashboard
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # User Management
    path('admin/users/', AdminUserListView.as_view(), name='admin_dashboard_users'),
    path('admin/users/add/', AdminAddUserView.as_view(), name='admin_add_user'),  # Custom add user
    path('admin/users/roles/', AdminUserRoleManagementView.as_view(), name='admin_dashboard_user_roles'),
    
    # Trip Management
    path('admin/trips/', AdminTripListView.as_view(), name='admin_dashboard_trips'),
    path('admin/trips/analytics/', AdminTripAnalyticsView.as_view(), name='admin_dashboard_trip_analytics'),
    path('admin/trips/content/', AdminContentManagementView.as_view(), name='admin_dashboard_trip_content'),
    
    # System Management
    path('admin/database-backup/', AdminDatabaseBackupView.as_view(), name='admin_database_backup'),
    path('admin/content/', AdminContentManagementView.as_view(), name='admin_content'),
    
    # Action URLs
    path('admin/user/<int:user_id>/toggle-active/', views_admin_actions.toggle_user_active, name='admin_toggle_user_active'),
    path('admin/trip/<int:trip_id>/delete/', views_admin_actions.delete_trip, name='admin_delete_trip'),
    path('admin/update-user-role/', views_admin_actions.update_user_role, name='admin_update_user_role'),
    path('admin/content/<str:content_type>/<int:content_id>/delete/', views_admin_actions.delete_content, name='admin_delete_content'),
    path('admin/content/<str:content_type>/<int:content_id>/status/', views_admin_actions.update_content_status, name='admin_update_content_status'),
    path('admin/statistics/', views_admin_actions.get_statistics, name='admin_get_statistics'),
]