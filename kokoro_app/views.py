from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.db import IntegrityError
from django.http import Http404
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect

import cloudinary

from .models import Activity, PerfectBalance, ProfileBio, ProfileDisplayName, ProfileQuote, ProfileImage, \
                    ProfileTimezone, BalanceStreak, ContactInfo, ProfilePost, User, PinnedProfilePost,\
                    FriendshipRequest, Friendships

from .forms import ActivityForm, PerfectBalanceForm, ProfileBioForm, ProfileDisplayNameForm, \
                   ProfileQuoteForm, ProfileImageForm, ProfileTimezoneForm, ContactInfoForm, \
                   ProfilePostForm, SupportEmailForm

from . import balance, profile_utils, friendship_utils
import pytz
import datetime
import os


def index(request):
    """Landing Page for Kokoro"""

    return render(request, 'kokoro_app/index.html', {})


@login_required()
def home(request):
    """Home Page for Kokoro users"""

    # Expire the user session on browser close ( 0 secs )
    request.session.set_expiry(0)

    if request.method == "POST":
        if 'activity_form' in request.POST:
            activity_form = ActivityForm(data=request.POST)
            if activity_form.is_valid():
                new_form = activity_form.save(commit=False)
                # title-ize activity
                new_form.description = new_form.description.title()
                # add owner
                new_form.owner = request.user
                new_form.save()
                return redirect('/home')

        elif 'manage_form' in request.POST:

            raw_post_data = request.POST

            # checkbox attrs are key=id_of_entry, value=on/off
            # By retrieving the key(s), we know what values to delete from database
            # '[1:len(result) - 1]' removes the csrf_token and button name from result
            post_data = list(raw_post_data.keys())[1:len(raw_post_data) - 1]

            # Delete objects based on their 'id' obtained from the queryDict/QueryList
            acts_to_delete = Activity.objects.filter(id__in=post_data)
            acts_to_delete.delete()
            return redirect('/home')

    # form for submitting daily activities
    activity_form = ActivityForm()

    activities = Activity.objects.filter(owner=request.user).order_by('date_added')

    # Returns all activities submitted today for user (queryset)
    start_of_today = balance.get_start_of_today(request)
    daily_mind = balance.daily_mind(request, start_of_today)
    daily_body = balance.daily_body(request, start_of_today)
    daily_soul = balance.daily_soul(request, start_of_today)

    # Package daily activities
    all_daily = {
        'daily_mind': daily_mind,
        'daily_body': daily_body,
        'daily_soul': daily_soul
    }

    # Returns boolean indicating if user has submitted at least 1 mind, body, and soul activity today
    # Also returns user balance streak
    balance_data = balance.balance(request, daily_mind, daily_body, daily_soul)
    found_balance = balance_data['found_balance']
    balance_streak = balance_data['balance_streak_value']

    context = {
        'activity_form': activity_form,
        'activities': activities,
        'all_daily': all_daily,
        'balance_bool': found_balance,
        'balance_streak': balance_streak
    }

    return render(request, 'kokoro_app/home.html', context)


@login_required
def profile(request):
    """
    Profile page for kokoro users
    :param request: request data
    :return: render of a user's profile page
    """

    # initial variables that aren't always reached
    already_friends = False
    pending_friendship_request = False

    if request.method == "POST":
        raise Http404("This shouldn't happen.")

    elif request.method == 'GET':

        # Get id of user profile to visit
        user_id = profile_utils.get_profile_to_visit(request)

        # user requesting their own profile
        if user_id == request.user.id:

            user = request.user

        # Get user object if user requesting a different profile than their own
        else:
            try:
                user = User.objects.get(id__exact=user_id)

            except Exception as e:
                raise Http404('Something went wrong while retrieving the profile you requested.', e)

            # determine if current user is already friends with the user that we're visiting (returns bool)
            already_friends = friendship_utils.determine_if_friends(request, user)

            # Check for pending friendship request if users are not friends (returns bool)
            if not already_friends:
                pending_friendship_request = friendship_utils.check_for_pending_friendship_request(request, user_id)

        # ----- user info/data for profile page -----
        # Note: some data can be accessed via 'user'
        profile_models = {
            'contact_info_model': ContactInfo,
            'post_model': ProfilePost,
            'pinned_post_model': PinnedProfilePost,
        }

        # Pass profile_models to helper (returns dictionary of user-specific data to build profile page)
        profile_data = profile_utils.get_profile_data(user, profile_models)

        # Retrieve TZ info separately, as we always want request.user's TZ data
        user_timezone_object, user_timezone = profile_utils.get_user_timezone(
            request.user, ProfileTimezone
        )

        for post in profile_data['posts']:
            date_published_utc = post.date_published
            date_published_user_tz = balance.convert_to_user_tz(date_published_utc, str(user_timezone_object))
            post.date_published = date_published_user_tz

        context = {
            'user': user,
            'already_friends': already_friends,
            'pending_friendship_request': pending_friendship_request,
            'contact_info': profile_data['contact_info'],  # Determine usage of contact info
            'posts': profile_data['posts'],
        }

        return render(request, 'kokoro_app/profile.html', context)


@login_required
def edit_profile(request):
    """
    Page for editing profile and account settings
    :param request: http data
    :return: render of edit_profile.html
    """

    user = request.user

    # *** MOVE to helper file
    # get UTC time with offset
    utc_timezone = datetime.datetime.now(tz=pytz.UTC)

    # get user's saved time zone
    user_timezone_object = user.profiletimezone
    # convert to string
    user_timezone_string = str(user_timezone_object)
    # convert utc_timezone to user timezone (with offset)
    user_timezone = utc_timezone.astimezone(pytz.timezone(user_timezone_string))

    # retrieve user-related objects as placeholders
    try:
        bio_placeholder = user.profilebio
    except ObjectDoesNotExist:
        bio_placeholder = None
    try:
        perfect_placeholder_queryset = user.perfectbalance
    except ObjectDoesNotExist:
        perfect_placeholder_queryset = None
    try:
        display_name_placeholder = user.profiledisplayname
    except ObjectDoesNotExist:
        display_name_placeholder = None
    try:
        quote_placeholder_queryset = user.profilequote
    except ObjectDoesNotExist:
        quote_placeholder_queryset = None
    try:
        contact_info = user.contactinfo
    except ObjectDoesNotExist:
        contact_info = None

    # Everyone has an image by default
    try:
        profile_image_placeholder = user.profileimage
    except ObjectDoesNotExist:
        profile_image_placeholder = None

    # Forms for editing profile
    display_name_form = ProfileDisplayNameForm(instance=display_name_placeholder)
    quote_form = ProfileQuoteForm(instance=quote_placeholder_queryset)
    bio_form = ProfileBioForm(instance=bio_placeholder)
    contact_form = ContactInfoForm(instance=contact_info)
    perfect_form = PerfectBalanceForm(instance=perfect_placeholder_queryset)
    profile_image_form = ProfileImageForm(instance=profile_image_placeholder)

    context = {
        'profile_image_form': profile_image_form,
        'profile_image_placeholder': profile_image_placeholder,
        'display_name_form': display_name_form,
        'display_name_placeholder': display_name_placeholder,
        'quote_form': quote_form,
        'quote_placeholder_queryset': quote_placeholder_queryset,
        'bio_form': bio_form,
        'bio_placeholder': bio_placeholder,
        'contact_info': contact_info,
        'contact_form': contact_form,
        'perfect_form': perfect_form,
        'perfect_placeholder_queryset': perfect_placeholder_queryset,
        'timezones': pytz.common_timezones,
        'user_timezone_object': user_timezone_object,
        'user_timezone': user_timezone,
    }

    return render(request, 'kokoro_app/edit_profile.html', context)


@login_required
def profile_form_handler(request):
    """
    Helper function for processing forms submitted from profile.html template
    :param request: http request data
    :return: A redirect to profile() view
    """

    if request.method == "POST":

        if 'tz_form' in request.POST:

            # timezone the user selected
            user_timezone_form = ProfileTimezoneForm(request.POST, instance=request.user.profiletimezone)
            # check validity and save
            if user_timezone_form.is_valid():
                user_timezone_form.save()

            return redirect('/profile')

        elif 'perfect_form' in request.POST:
            perfect_form_submitted = PerfectBalanceForm(data=request.POST)
            if perfect_form_submitted.is_valid():

                # retrieve user PerfectBalance object
                current_perfect_balance, created = PerfectBalance.objects.get_or_create(owner=request.user)
                # save new perfect balance form with helper function
                profile_utils.save_new_perfect_balance(request, perfect_form_submitted, current_perfect_balance)

                return redirect('/profile')

        elif 'bio_form' in request.POST:
            # user is submitting a biography
            bio_form_submitted = ProfileBioForm(data=request.POST)
            if bio_form_submitted.is_valid():

                # retrieve user biography
                current_biography, created = ProfileBio.objects.get_or_create(owner=request.user)
                # save new biography
                profile_utils.save_new_biography(request, bio_form_submitted, current_biography)

                return redirect('/profile')

        elif 'display_name_form' in request.POST:
            # get submitted form data
            display_name_form_submitted = ProfileDisplayNameForm(data=request.POST)
            if display_name_form_submitted.is_valid():

                # retrieve or create ProfileDisplayName object for user
                current_display_name, created = ProfileDisplayName.objects.get_or_create(owner=request.user)
                # save new display name with helper function
                profile_utils.save_new_display_name(request, display_name_form_submitted, current_display_name)

                return redirect('/profile')

        elif 'quote_form' in request.POST:
            # get form data
            quote_form_submitted = ProfileQuoteForm(data=request.POST)
            # check validity
            if quote_form_submitted.is_valid():

                # retrieve current ProfileQuote object for user
                current_quote, created = ProfileQuote.objects.get_or_create(owner=request.user)
                # save new quote & author
                profile_utils.save_new_quote(request, quote_form_submitted, current_quote)

                return redirect('/profile')

        elif 'profile_image_form' in request.POST:

            try:
                # get User's current Profile Image and remove/delete
                current_image = request.user.profileimage
                profile_utils.remove_current_profile_image(current_image)
            except Exception as e:
                # user doesn't have profile image (probably)
                pass

            try:
                # remove image from cloudinary (required param == public id of cloudinary image)
                cloudinary.uploader.destroy(request.user.profileimage.image.public_id)
            except Exception as e:
                print(e)

            # get form data
            profile_image_submitted = ProfileImageForm(request.POST, request.FILES, instance=request.user.profileimage)
            # check validity
            if profile_image_submitted.is_valid():

                y = profile_image_submitted.save()
                print(y)

                return redirect('/profile')

        elif 'contact_info_form' in request.POST:
            # get form data
            try:
                contact_info_submitted = ContactInfoForm(data=request.POST, instance=request.user.contactinfo)

            except Exception as e:
                # User likely doesn't have ContactInfo yet.
                # Create default ContactInfo instance for user, then override with POST data
                ContactInfo.objects.create(owner=request.user)
                contact_info_submitted = ContactInfoForm(data=request.POST, instance=request.user.contactinfo)

            # check validity and save
            if contact_info_submitted.is_valid():
                contact_info_submitted.save(commit=False)
                contact_info_submitted.owner = request.user
                contact_info_submitted.save()

                return redirect('/profile')


@login_required()
def post(request, post_slug):
    """
    A page for viewing a user's individual profile post
    (post_slug is received via form action variable)
    :param request: http request data
    :param post_slug: a unique slug value for a profile post
    :return: render of a 'post' page with unique post_slug for URL
    """

    # use unique slug to retrieve desired post
    requested_post = ProfilePost.objects.get(post_slug__exact=post_slug)

    # Check if this post already pinned by user
    # This query may be a little too complex (think how it could be easier)
    # It says: pinned == PinnedProfilePost object where pinned_by = request.user,
    #          and FK original = ProfilePost object with post_slug passed from template (post clicked on)
    try:
        pinned_post = PinnedProfilePost.objects.get(
            pinned_by__exact=request.user,
            original__exact=requested_post
        )
        # If query executes without exception, post is already pinned
        pinned = True
    except Exception as e:
        pinned = False

    # get user's saved time zone (outsource to helper?)
    user_timezone_object = ProfileTimezone.objects.get(owner__exact=request.user)
    # convert to string
    user_timezone_string = str(user_timezone_object)

    # convert date_published from UTC to user timezone
    date_published_utc = requested_post.date_published
    date_published_user_tz = balance.convert_to_user_tz(date_published_utc, user_timezone_string)

    context = {
        'post': requested_post,
        'pinned': pinned,
        'date_published_user_tz': date_published_user_tz,
    }

    return render(request, 'kokoro_app/post.html', context)


@login_required
def write_post(request):
    """
    Page for writing a new ProfilePost
    :param request: http request data
    :return: render of 'write post' page
    """

    # testing profile posts
    if request.method == 'POST':
        raise Http404("Something is wrong.")
    else:
        profile_post_form = ProfilePostForm()
        context = {'profile_post_form': profile_post_form}

        return render(request, 'kokoro_app/write_post.html', context)


@login_required
def edit_post(request):
    """
    Page for editing a ProfilePost object
    :param request: http data
    :return: render of edit_profile.html
    """

    context = {}

    if request.method == 'GET':

        try:
            # get unique slug of ProfilePost object
            post_slug = request.GET.get('edit_post_form')

            # get ProfilePost object matching slug
            post_to_edit = ProfilePost.objects.get(post_slug__exact=post_slug)

            # generate ProfilePostForm prepopulated with instance object
            post_form = ProfilePostForm(instance=post_to_edit)

            context = {
                'post_to_edit': post_to_edit,
                'post_form': post_form,
            }
        except Exception as e:
            raise Http404("Something went wrong retrieving your post to edit.")

    elif request.method == 'POST':

        try:
            # form returns the unique slug of a ProfilePost object
            post_slug = request.POST.get('update_post_form')

            # get object with matching slug
            post_to_update = ProfilePost.objects.get(post_slug__exact=post_slug)

            # get updated fields
            new_headline = request.POST.get('headline')
            new_content = request.POST.get('content')
            new_post_slug = slugify(new_headline)

            # save object with updated fields
            post_to_update.headline = new_headline.title()
            post_to_update.content = new_content
            post_to_update.post_slug = new_post_slug

            post_to_update.save(update_fields=['headline', 'content', 'post_slug'])

        except Exception as e:
            raise Http404("Something went wrong while updating your post. Sorry :( ")

        return post(request, new_post_slug)

    # get requests render the page to edit a post
    return render(request, 'kokoro_app/edit_post.html', context)


@login_required
def posts_form_handler(request):
    """
    Helper function for processing forms submitted from post.html and write_post.html templates
    :param request: http request data
    :return: A redirect to profile()
    """

    if request.method == 'POST':

        if 'write_post_form' in request.POST:
            # get form data
            post_submitted = ProfilePostForm(data=request.POST)

            # check validity
            if post_submitted.is_valid():

                new_post = post_submitted.save(commit=False)
                # Title-ize headline
                new_post.headline = new_post.headline.title()
                # add author and unique slug to post
                new_post.author = request.user
                new_post.post_slug = slugify(new_post.headline)

                try:
                    new_post.save()
                except IntegrityError:
                    # The generated slug was not unique
                    new_slug_id = get_random_string(length=6)
                    unique_slug = f'{new_post.post_slug}-{new_slug_id}'
                    new_post.post_slug = unique_slug
                    new_post.save()

                return redirect('/profile')

        elif 'pin_post_form' in request.POST:
            # get form data, returns unique slug
            post_to_pin_slug = request.POST.get('pin_post_form')

            # get post with matching slug
            post_to_pin = ProfilePost.objects.get(post_slug__exact=post_to_pin_slug)

            # Create new PinnedProfilePost
            new_pinned_post = PinnedProfilePost()

            # Apply necessary fields and save
            new_pinned_post.original = post_to_pin
            new_pinned_post.pinned_by = request.user
            new_pinned_post.save()

            try:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            except Exception as e:
                return redirect("/profile")

        elif 'unpin_post_form' in request.POST:
            # get form data
            post_to_unpin_slug = request.POST.get('unpin_post_form')

            try:
                # get post with matching slug
                post_to_unpin = PinnedProfilePost.objects.get(
                    pinned_by__exact=request.user,
                    original__exact=ProfilePost.objects.get(post_slug__exact=post_to_unpin_slug)
                )

                # Delete PinnedProfilePost object
                post_to_unpin.delete()

            except Exception as e:
                raise Http404('Something went wrong while un-pinning the post.')

            return redirect('/profile')

        elif 'delete_post_form' in request.POST:
            # get form data (post_slug)
            try:
                post_to_delete_slug = request.POST.get('delete_post_form')
                post_to_delete = ProfilePost.objects.get(post_slug__exact=post_to_delete_slug)
                post_to_delete.delete()

            except Exception as e:
                raise Http404("Something went wrong while deleting your post.")

            return redirect('/profile')


@login_required()
def search(request):
    """
    Search kokoro user-base based on user-input and display results
    :param request: http request data
    :return:
    """

    # returns text entered into search box
    search_input = request.GET.get('search')

    if not search_input:
        # Don't allow blank searches
        return redirect('/home')

    # returns queryset of User(s) with username value of search_input
    users_queryset = User.objects.filter(username__icontains=f'{search_input}')

    context = {
        'search_results': users_queryset,
    }

    return render(request, 'kokoro_app/search.html', context)


@login_required
def send_friendship_request_handler(request, sending_to_id):
    """
    Handler for sending a friendship request from current user to another user
    :param request: http request data
    :param sending_to_id: a unique id (str) of a User object
    :return: a message indicating that the friendship request sent successfully or 404
    """

    successful = friendship_utils.send_friendship_request(request, sending_to_id)

    if successful:
        # Bring user back to profile they were viewing with success message
        try:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        except Exception as e:
            # user/browser may not have 'HTTP_REFERER' turned on, bring user back to friendships
            return redirect('/view_friendships')


@login_required
def accept_friendship_request_handler(request, sent_by):
    """
    Handler for accepting(saving) a Friendships object, and deleting the corresponding FriendshipRequest object
    :param sent_by: a unique id (str) of the user who sent the friendship request to the current user
    :param request: http post data
    :return:
    """

    successful = friendship_utils.accept_friendship_request(request, sent_by)

    if successful:
        return redirect('/view_friendships')


@login_required
def cancel_friendship_request_handler(request, friendship_request):
    """
    Handler for cancelling (deleting) a FriendshipRequest object
    :param request: http post data
    :param friendship_request: unique id (str) of a FriendshipRequest object
    :return: HttpResponseRedirect
    """

    successful = friendship_utils.cancel_friendship_request(request, friendship_request)

    if successful:
        return redirect('/view_friendships')
    else:
        raise Http404("There was an error redirecting you to page. Friendship Request cancelled.")


@login_required
def decline_friendship_request_handler(request, friendship_request):
    """
    Handler for declining(deleting) a FriendshipRequest object
    :param request: http post data
    :param friendship_request: unique id (str) of a FriendshipRequest object
    :return: HttpResponseRedirect
    """

    successful = friendship_utils.decline_friendship_request(request, friendship_request)

    if successful:
        return redirect('/view_friendships')
    else:
        raise Http404("There was an error redirecting you to page. Friendship request declined.")


@login_required
def view_friendships(request):
    """
    Page for viewing a user's friendships
    :param request: http request data
    :return: render of view_friendships.html
    """

    # get user friendships
    # return type = <class 'kokoro_app.models.Friendships'> (ManyRelatedManager object)
    friendships, created = Friendships.objects.get_or_create(owner=request.user)

    # convert ManyRelatedManager object into Queryset
    friendships = friendships.friendships.all()

    friendships = friendships.order_by('username')

    # get friendship request pbjects for both users
    pending_requests_from_user = FriendshipRequest.objects.filter(from_user__exact=request.user)
    pending_requests_to_user = FriendshipRequest.objects.filter(to_user__exact=request.user)

    context = {
        'friendships': friendships,
        'requests_from_user': pending_requests_from_user,
        'requests_to_user': pending_requests_to_user,
    }

    return render(request, 'kokoro_app/view_friendships.html', context)


@login_required
def remove_friendship_handler(request):
    """
    Helper for removing a friendship from a user's friendships (remove User from Friendships object)
    :param request: http post data
    :return: redirect to view_friendships.html
    """

    try:
        friendship_to_remove_id = request.POST['friend-to-remove']
    except Exception as e:
        raise Http404("Something went wrong while updating your friendships. Nothing was altered.")

    successful = friendship_utils.remove_friendship(request, friendship_to_remove_id)

    if successful:
        return redirect('/view_friendships')
    else:
        raise Http404("There was an error redirecting you to page. Friendship Removed.")


def support(request):
    """
    Page for contacting kokoro
    :param request: http get data
    :return: render of support.html
    """

    context = {}

    if request.method == 'POST':

        # validate form
        submitted_support_form = SupportEmailForm(data=request.POST)

        if submitted_support_form.is_valid():
            try:
                # get data from submitted form
                sent_from = submitted_support_form.cleaned_data['sent_from']
                subject = submitted_support_form.cleaned_data['subject']
                username = submitted_support_form.cleaned_data['username']
                message = submitted_support_form.cleaned_data['message']
                message = f'{message} || From: @{username}/{sent_from}'
                recipient = os.environ.get('KOKORO_EMAIL_HOST_USER')
                recipients = [recipient]
            except Exception as e:
                raise Http404("Something went wrong while processing your report. Please try again later.", e)

            # Send Email
            try:
                # requires: subject, message, from_email, recipient list
                mail_sent = send_mail(subject, message, sent_from, recipients)
            except Exception as e:
                print("ERROR", e)
                raise Http404("Something went wrong while preparing your report. Please try again later.")

            # send_mail() returns 0 or 1, representing the amount of emails that were sent
            if mail_sent == 1:
                # successful, render support_success.html
                return render(request, 'kokoro_app/support_success.html')

            else:
                raise Http404("Something went wrong while sending your report. Please try again later.", mail_sent)
        else:
            raise Http404("Your report was not valid.")

    elif request.method == 'GET':
        # instantiate blank form
        support_form = SupportEmailForm()

        context['support_form'] = support_form

    return render(request, 'kokoro_app/support.html', context)
