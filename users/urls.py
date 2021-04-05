"""Defines url patterns for users"""

from django.urls import path, include
from . import views

# Distinguish 'users' urls from other app urls
app_name = 'users'
urlpatterns = [
    # Include the default django auth urls (login\logout)
    path('', include('django.contrib.auth.urls')),

    # Registration page for new users
    path('register/', views.register, name='register'),
]
