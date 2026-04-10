from .models import Notification

def notifications(request):
    """Injects unread_notifications count and list into every template context."""
    if request.user.is_authenticated:
        unread = request.user.notifications.filter(is_read=False).order_by('-created_at')
        return {
            'unread_notifications': unread,
            'unread_notifications_count': unread.count(),
        }
    return {
        'unread_notifications': [],
        'unread_notifications_count': 0,
    }
