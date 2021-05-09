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

    if request.method == 'POST':

        if 'notification_form' in request.POST:
            # User selected a notification from nav

            # get form data (id (str))
            notification_id = request.POST.get('notification_form')

            # get Notification object matching id, mark as 'read'
            notification = Notification.objects.get(id=notification_id)
            notification.unread = False
            notification.save()

        elif 'mark_all_form' in request.POST:
            # mark all user notifications as 'unread = False'
            Notification.objects.filter(recipient=request.user).update(unread=False)

    return redirect('/profile')
