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

    # Called when forms submitted from profile.html, redirects to profile()
    path('profile_form_handler/', views.profile_form_handler, name='profile_form_handler'),

    # Called when forms submitted from post.html & write_post.html, redirects to profile()
    path('posts_form_handler/', views.posts_form_handler, name='posts_form_handler'),

    # Called when send_friend_request_form submitted
    path('send_friendship_request/<sending_to>/', views.send_friendship_request, name='send_friendship_request'),

    # Page to view pending friendship requests to and from user
    path('view_friendship_requests', views.view_friendship_requests, name='view_friendship_requests'),

    # Called when a user wants to accept a pending friendship request
    path('accept_friendship_request/<sent_by>/', views.accept_friendship_request, name='accept_friendship_request'),
]
