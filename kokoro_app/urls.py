"""Defines URL patterns for kokoro_app"""

from django.urls import path

from . import views

app_name = 'kokoro_app'
urlpatterns = [
    # Landing Page
    path('', views.index, name='index'),

    # Home Page
    path('home/', views.home, name='home'),

    # User-Profile Page
    path('profile/', views.profile, name='profile'),
]
