from django.shortcuts import render, redirect, HttpResponse, reverse, HttpResponseRedirect
from .models import Notification
from kokoro_app.models import ProfilePost

from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
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

            # get form data (id == (str))
            notification_id = request.POST.get('notification_form')

            # get Notification object matching id, mark as 'read'
            notification = Notification.objects.get(id=notification_id)
            notification.unread = False
            notification.save()

            # deliver user to correct url

            # Type 1: Someone sent you a friendship request
            if notification.type == 1:
                # On click, should bring user to 'view_friendships.html'
                return redirect('/view_friendships')

            # Type 2: Someone accepted your friendship request
            elif notification.type == 2:
                # should call profile(request), add profile_to_visit session variable
                request.session['profile_to_visit'] = notification.sent_from.id
                return redirect('/profile')

            # Type 3: Someone pinned your ProfilePost to their profile
            elif notification.type == 3:
                # should call profile(request), add profile_to_visit session variable
                request.session['profile_to_visit'] = notification.sent_from.id
                return redirect('/profile')

            # Type 4: Friend published a new ProfilePost
            elif notification.type == 4:

                # bring user to new profile post

                reference_post = notification.reference
                reference_post_author = notification.sent_from

                try:
                    # get matching post
                    post = ProfilePost.objects.get(author=reference_post_author, headline=reference_post)

                    # get unique slug of post
                    post_slug = post.post_slug

                    # redirect with proper param
                    return redirect('kokoro_app:post', post_slug=post_slug)

                except ObjectDoesNotExist:
                    # Author may have edited post/post_slug, bring user to their profile instead
                    request.session['profile_to_visit'] = reference_post_author.id
                    return redirect('kokoro_app:profile')

        # These should return user to the same page they're visiting
        elif 'mark_all_form' in request.POST:
            # mark all user notifications as 'unread = False'
            Notification.objects.filter(recipient=request.user).update(unread=False)
            try:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            except Exception as e:
                print(e)

        elif 'clear_all_form' in request.POST:
            # Delete all notifications for user
            all_notifications = Notification.objects.filter(recipient=request.user)
            all_notifications.delete()
            try:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            except Exception as e:
                print(e)

    return redirect('/profile')
