from django.shortcuts import render, redirect
from .models import Notification
# Create your views here.


def notification_form_handler(request):
    """
    Helper function for handling forms involving Notification model
    :param request: http data
    :return:
    """

    if request.method == 'GET':
        # do stuff
        ...
        if 'notification_form' in request.GET:
            print("hehe")
            notification_id = request.GET.get('notification_form')
            print(notification_id, "is the notification id.")

            # get Notification object matching id
            notification = Notification.objects.get(id__exact=notification_id)

            print(f'{notification.type} is the type value')

    return redirect('/profile')
