""" Defines URL patterns for notifications app """

from django.urls import path

from . import views

app_name = 'notifications'
print(app_name)

urlpatterns = [

    # Called when a Notification object needs to be altered
    path('notifications/notifications_form_handler', views.notification_form_handler, name='notification_form_handler'),

]
