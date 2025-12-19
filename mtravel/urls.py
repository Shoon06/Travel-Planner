from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

def home_view(request):
    """ALWAYS show home page - NEVER redirect automatically"""
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('users/', include('users.urls', namespace='users')),
    path('trips/', include('trips.urls')),
    path('posts/', include('posts.urls')),
    path('planner/', include('planner.urls', namespace='planner')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)