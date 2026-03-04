# posts/context_processors.py
from .models import Notification

def notifications_context(request):
    context = {}
    if request.user.is_authenticated:
        try:
            unread_count = Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()
            context['unread_notifications'] = unread_count
        except:
            context['unread_notifications'] = 0
    return context