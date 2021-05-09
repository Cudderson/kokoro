from django.shortcuts import render, redirect, HttpResponse, reverse, HttpResponseRedirect
from .models import Notification

from kokoro_app.views import view_friendship_requests

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

            # type (int)
            print(notification.type)

            # deliver user to correct url

            # Type 1: Someone sent you a friend request
            if notification.type == 1:
                # On click, should bring user to 'friendship_requests.html'
                # The proper way is to redirect to the appropriate url
                return redirect('/view_friendship_requests')
            elif notification.type == 2:
                # should call profile(request) with a 'profile_to_visit' parameter
                request.session['profile_to_visit'] = notification.sent_from.id
                return redirect('/profile')

        elif 'mark_all_form' in request.POST:
            # mark all user notifications as 'unread = False'
            Notification.objects.filter(recipient=request.user).update(unread=False)

    return HttpResponse("yolo")


# if not request.GET._mutable:
#    request.GET._mutable = True
#
# # now you can edit it
# request.GET['name'] = 'jhon'
# request.GET['age'] = 26