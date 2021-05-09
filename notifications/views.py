from django.shortcuts import render, redirect
from .models import Notification
# Create your views here.


def notification_form_handler(request):
    """
    Helper function for handling forms involving Notification model,
    marks Notification object as 'unread = False'
    :param request: http data
    :return:
    """

    if request.method == 'GET':

        if 'notification_form' in request.GET:

            # get form data (id (str))
            notification_id = request.GET.get('notification_form')

            # get Notification object matching id, mark as 'read'
            notification = Notification.objects.get(id=notification_id)
            notification.unread = False
            notification.save()

        # Now, any notification clicked on from nav is marked as unread = False
        # We can show if a notification is read in template using the 'unread' value of the notification [x]

    return redirect('/profile')
