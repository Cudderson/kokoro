from django.shortcuts import render, redirect

# Create your views here.


def notification_form_handler(request):
    """
    Helper function for handling forms involving Notification model
    :param request: http data
    :return:
    """

    if request.method == 'POST':
        # do stuff
        ...

    return redirect('/profile')
