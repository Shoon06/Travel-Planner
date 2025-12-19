from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
import json

from users.models import CustomUser
from planner.models import TripPlan, Destination, Hotel, Flight, BusService, CarRental
from posts.models import Post, Comment

def is_admin_user(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.user_type == 'admin' or user.is_staff)

@login_required
@user_passes_test(is_admin_user)
@require_POST
def toggle_user_active(request, user_id):
    """Toggle user active status"""
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        
        # Prevent self-deactivation
        if user == request.user:
            return JsonResponse({
                'success': False,
                'error': 'You cannot deactivate your own account'
            })
        
        user.is_active = not user.is_active
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'is_active': user.is_active
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_admin_user)
@require_POST
def delete_trip(request, trip_id):
    """Delete a trip"""
    try:
        trip = get_object_or_404(TripPlan, id=trip_id)
        trip.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Trip deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_admin_user)
@csrf_exempt
@require_POST
def update_user_role(request):
    """Update user role"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        new_role = data.get('role')
        
        if not user_id or not new_role:
            return JsonResponse({'success': False, 'error': 'Missing parameters'})
        
        user = get_object_or_404(CustomUser, id=user_id)
        
        # Prevent self-demotion
        if user == request.user and new_role != 'admin':
            return JsonResponse({
                'success': False,
                'error': 'You cannot change your own role from admin'
            })
        
        user.user_type = new_role
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'User role updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_admin_user)
@require_POST
def delete_content(request, content_type, content_id):
    """Delete content (posts, comments, hotels, etc.)"""
    try:
        if content_type == 'post':
            content = get_object_or_404(Post, id=content_id)
        elif content_type == 'comment':
            content = get_object_or_404(Comment, id=content_id)
        elif content_type == 'hotel':
            content = get_object_or_404(Hotel, id=content_id)
        elif content_type == 'destination':
            content = get_object_or_404(Destination, id=content_id)
        elif content_type == 'flight':
            content = get_object_or_404(Flight, id=content_id)
        elif content_type == 'bus':
            content = get_object_or_404(BusService, id=content_id)
        elif content_type == 'car':
            content = get_object_or_404(CarRental, id=content_id)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid content type'})
        
        content.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{content_type.title()} deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_admin_user)
@csrf_exempt
@require_POST
def update_content_status(request, content_type, content_id):
    """Update content status (active/inactive)"""
    try:
        data = json.loads(request.body)
        is_active = data.get('is_active', True)
        
        if content_type == 'hotel':
            content = get_object_or_404(Hotel, id=content_id)
            content.is_active = is_active
        elif content_type == 'flight':
            content = get_object_or_404(Flight, id=content_id)
            content.is_active = is_active
        elif content_type == 'bus':
            content = get_object_or_404(BusService, id=content_id)
            content.is_active = is_active
        elif content_type == 'car':
            content = get_object_or_404(CarRental, id=content_id)
            content.is_available = is_active
        elif content_type == 'user':
            content = get_object_or_404(CustomUser, id=content_id)
            content.is_active = is_active
        else:
            return JsonResponse({'success': False, 'error': 'Invalid content type'})
        
        content.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{content_type.title()} status updated successfully',
            'is_active': is_active
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@user_passes_test(is_admin_user)
@require_POST
def get_statistics(request):
    """Get real-time statistics for admin dashboard"""
    try:
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # User statistics
        total_users = CustomUser.objects.count()
        new_users_today = CustomUser.objects.filter(
            date_joined__date=datetime.now().date()
        ).count()
        active_users = CustomUser.objects.filter(is_active=True).count()
        
        # Trip statistics
        total_trips = TripPlan.objects.count()
        active_trips = TripPlan.objects.filter(
            status__in=['planning', 'booked']
        ).count()
        completed_trips = TripPlan.objects.filter(status='completed').count()
        
        # Destination statistics
        total_destinations = Destination.objects.count()
        
        # Hotel statistics
        total_hotels = Hotel.objects.count()
        active_hotels = Hotel.objects.filter(is_active=True).count()
        
        # Transport statistics
        total_flights = Flight.objects.count()
        total_buses = BusService.objects.count()
        total_cars = CarRental.objects.count()
        
        # Post statistics
        total_posts = Post.objects.count()
        total_comments = Comment.objects.count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        
        new_users_week = CustomUser.objects.filter(
            date_joined__gte=week_ago
        ).count()
        
        new_trips_week = TripPlan.objects.filter(
            created_at__gte=week_ago
        ).count()
        
        # Popular destinations
        popular_destinations = list(
            TripPlan.objects.values('destination__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        return JsonResponse({
            'success': True,
            'statistics': {
                'users': {
                    'total': total_users,
                    'new_today': new_users_today,
                    'active': active_users,
                    'new_week': new_users_week
                },
                'trips': {
                    'total': total_trips,
                    'active': active_trips,
                    'completed': completed_trips,
                    'new_week': new_trips_week
                },
                'content': {
                    'destinations': total_destinations,
                    'hotels': total_hotels,
                    'active_hotels': active_hotels,
                    'flights': total_flights,
                    'buses': total_buses,
                    'cars': total_cars,
                    'posts': total_posts,
                    'comments': total_comments
                },
                'popular_destinations': popular_destinations
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})