# C:\Users\ASUS\MyanmarTravelPlanner\users\urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView  # Use Django's built-in LogoutView

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    # This will log out the user and redirect to home page
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('force-logout/', views.force_logout_view, name='force_logout'),
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
]