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

    # Page for viewing a single post
    path('post/<slug:post_slug>/', views.post, name='post'),

    # Page for writing a new ProfilePost
    path('write_post/', views.write_post, name='write_post'),

    # Page to display search results
    path('search/', views.search, name='search'),

    # Called when forms submitted on profile page, redirects to profile()
    path('profile_form_handler/', views.profile_form_handler, name='profile_form_handler'),
]
