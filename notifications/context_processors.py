# Defining context to be made available in every template

# The first use case is to pass notifications to each template (can't define context for base.html on it's own)

from .models import Notification


def pass_notifications_to_context(request):
    """
    Grabs notifications for the logged-in user and passes them as view context for templates
    :param request: http data
    :return: global context for templates
    """

    try:
        user_notifications = Notification.objects.filter(recipient__exact=request.user).order_by('-id')

        return {
            'notifications': user_notifications
        }

    except Exception as e:
        print(e)
        return {
            'notifications': 'None'
        }

