# C:\Users\ASUS\MyanmarTravelPlanner\mtravel\urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

def home_view(request):
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('users/', include('users.urls', namespace='users')),
    path('trips/', include('trips.urls')),
    path('posts/', include('posts.urls')),
    path('planner/', include('planner.urls', namespace='planner')),
]

# Admin redirect
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()

@user_passes_test(is_admin)
def admin_redirect(request):
    return redirect('users:admin_dashboard')

# Add this URL pattern to redirect /admin/ to your custom admin
urlpatterns += [
    path('admin-portal/', admin_redirect, name='admin_redirect'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)