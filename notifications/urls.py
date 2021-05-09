""" Defines URL patterns for notifications app """

from django.urls import path

from . import views

app_name = 'notifications'

urlpatterns = [

    # Called when a Notification object needs to be altered
    path('notification_form_handler/', views.notification_form_handler, name='notification_form_handler'),

]
