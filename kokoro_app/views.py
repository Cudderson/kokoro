from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.db import IntegrityError
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

from .models import Activity, PerfectBalance, ProfileBio, ProfileDisplayName,\
                    ProfileQuote, ProfileImage, ProfileTimezone, BalanceStreak, ContactInfo, ProfilePost, User, PinnedProfilePost,\
                    FriendshipRequest, Friendships

from notifications.models import Notification

from .forms import ActivityForm, PerfectBalanceForm, ProfileBioForm, ProfileDisplayNameForm, \
                   ProfileQuoteForm, ProfileImageForm, ProfileTimezoneForm, ContactInfoForm, ProfilePostForm
from . import balance, profile_utils, friendship_utils
import pytz
import datetime

# testing returning to same page after sending friend request
from django.http import HttpResponseRedirect
# success messages
from django.contrib import messages


def index(request):
    """Landing Page for Kokoro"""

    return render(request, 'kokoro_app/index.html', {})


@login_required()
def home(request):
    """Home Page for Kokoro users"""

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
            # should probably move this logic to helper file
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

        if 'profile_to_visit' in request.GET:

            # User is requesting the profile of a different user (search form)
            user_id = request.GET.get('profile_to_visit')

        elif 'profile_to_visit' in request.session:

            # User is requesting the profile of a different user (notification)
            user_id = request.session['profile_to_visit']
            # remove variable from session to avoid cross-ups
            del request.session['profile_to_visit']

        else:
            # Logged in user is requesting their own profile
            user = request.user
            user_id = request.user.id
            already_friends = False

        # Get user object if user requesting a different profile than their own
        if user_id != request.user.id:
            try:
                # Objects.get() returns 1 object rather than queryset of objects (objects.filter())
                user = User.objects.get(id__exact=user_id)
            except Exception as e:
                # Handle the case of MultipleObjectsReturned & DoesNotExist
                print(e)
                raise Http404('Something went wrong while retrieving the profile you requested.')

            # determine if current user is already friends with the user that we're visiting
            try:
                already_friends = Friendships.objects.get(owner=request.user, friendships__id=user.id)
                already_friends = True
            except Exception as e:
                print(e)

            # Let's get the user's FriendshipRequest objects
            # Better yet, let's determine in here if there is an open FriendshipRequest
            # This block will try to execute when user is visiting someone else's profile (move to helper)
            try:
                # check if user has sent FriendshipRequest to profile visiting
                pending_friendship_request = FriendshipRequest.objects.get(from_user=request.user, to_user=user_id, accepted=False)
            except ObjectDoesNotExist:
                # check if profile visiting has sent FriendshipRequest to user
                try:
                    pending_friendship_request = FriendshipRequest.objects.get(from_user=user_id, to_user=request.user, accepted=False)
                except ObjectDoesNotExist:
                    pass

            pending_friendship_request = True if pending_friendship_request else False

        # user info for profile page
        try:
            biography = ProfileBio.objects.get(owner__exact=user.id)
        except Exception as e:
            biography = ""
        try:
            display_name = ProfileDisplayName.objects.get(owner__exact=user.id)
        except Exception as e:
            display_name = ""
        try:
            contact_info = ContactInfo.objects.filter(owner__exact=user.id)
        except Exception as e:
            contact_info = ""

        # 'quote_data' is 'quote_data_queryset' parsed to a dictionary
        try:
            quote_data_queryset = ProfileQuote.objects.get(owner__exact=user.id)
        except Exception as e:
            quote_data_queryset = ""
        quote_data = profile_utils.parse_quote_data(quote_data_queryset)

        try:
            # 'perfect_balance' is 'perfect_balance_queryset parsed into a list
            perfect_balance_queryset = PerfectBalance.objects.get(owner=user.id)
        except Exception as e:
            perfect_balance_queryset = ""
        perfect_balance = profile_utils.get_perfect_balance_data(perfect_balance_queryset)

        # *** MOVE to helper file
        # get UTC time with offset
        utc_timezone = datetime.datetime.now(tz=pytz.UTC)
        # print(f'utc time: {utc_timezone}')
        # get user's saved time zone
        user_timezone_object = ProfileTimezone.objects.get(owner__exact=user.id)
        # convert to string
        user_timezone_string = str(user_timezone_object)
        # print(f'users saved TZ string: {user_timezone_string}')
        # convert utc_timezone to user timezone (with offset)
        user_timezone = utc_timezone.astimezone(pytz.timezone(user_timezone_string))
        # print(f'user timezone: {user_timezone}')
        # print(f"Are these the same time? {user_timezone == utc_timezone}") # true

        # forms for profile page
        perfect_form = PerfectBalanceForm()
        bio_form = ProfileBioForm()
        display_name_form = ProfileDisplayNameForm()
        quote_form = ProfileQuoteForm()
        profile_image_form = ProfileImageForm()
        contact_info_form = ContactInfoForm()

        # ***** Create list of queryset objects for template *****
        # our 2 querysets to sort together are pinned_posts and profile_posts
        # User ProfilePost's
        profile_posts = ProfilePost.objects.filter(author__exact=user.id)

        # Pinned Posts
        pinned_posts = PinnedProfilePost.objects.filter(pinned_by__exact=user.id)

        from itertools import chain
        posts = sorted(
            chain(profile_posts, pinned_posts),
            key=lambda post_or_pinned: post_or_pinned.date_published, reverse=True
        )

        # Let's also pass BalanceStreak data to template
        balance_streak_object = BalanceStreak.objects.get(owner__exact=request.user)
        balance_streak = balance_streak_object.balance_streak

        # Will shrink context later as we define new User model
        context = {
            'user': user,
            # boolean
            'already_friends': already_friends,
            'pending_friendship_request': pending_friendship_request,
            'perfect_form': perfect_form,
            'perfect_balance': perfect_balance,
            'display_name_form': display_name_form,
            'display_name': display_name,
            'bio_form': bio_form,
            'biography': biography,
            'quote_data': quote_data,
            'quote_form': quote_form,
            'profile_image_form': profile_image_form,
            'contact_info_form': contact_info_form,
            'contact_info': contact_info,
            'timezones': pytz.common_timezones,
            'user_timezone_object': user_timezone_object,
            'user_timezone': user_timezone,
            'posts': posts,
            'balance_streak': balance_streak,
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
    user_timezone_object = ProfileTimezone.objects.get(owner__exact=user.id)
    # convert to string
    user_timezone_string = str(user_timezone_object)
    # convert utc_timezone to user timezone (with offset)
    user_timezone = utc_timezone.astimezone(pytz.timezone(user_timezone_string))

    # retrieve user-related objects as placeholders
    try:
        bio_placeholder = ProfileBio.objects.get(owner=request.user)
    except Exception as e:
        bio_placeholder = None
    try:
        perfect_placeholder_queryset = PerfectBalance.objects.get(owner=request.user)
    except Exception as e:
        perfect_placeholder_queryset = None
    try:
        display_name_placeholder = ProfileDisplayName.objects.get(owner=request.user)
    except Exception as e:
        display_name_placeholder = None
    try:
        quote_placeholder_queryset = ProfileQuote.objects.get(owner=request.user)
    except Exception as e:
        quote_placeholder_queryset = None

    # Everyone has an image by default
    profile_image_placeholder = ProfileImage.objects.get(owner=request.user)

    # Forms for editing profile
    bio_form = ProfileBioForm(instance=bio_placeholder)
    perfect_form = PerfectBalanceForm(instance=perfect_placeholder_queryset)
    display_name_form = ProfileDisplayNameForm(instance=display_name_placeholder)
    quote_form = ProfileQuoteForm(instance=quote_placeholder_queryset)
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

    # checking when moved from here to edit_profile()

    if request.method == "POST":

        # user timezone testing
        if 'tz_form' in request.POST:   # [x]
            # timezone the user selected
            user_timezone_form = ProfileTimezoneForm(request.POST, instance=request.user.profiletimezone)
            # check validity
            if user_timezone_form.is_valid():
                print("VALID TZ")
                # save form (working)
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
                # delete old display name
                ProfileDisplayName.objects.filter(owner__exact=request.user).delete()
                # save new display name with helper function
                profile_utils.save_new_display_name(request, display_name_form_submitted)

                return redirect('/profile')

        elif 'quote_form' in request.POST:
            # get form data
            quote_form_submitted = ProfileQuoteForm(data=request.POST)
            # check validity
            if quote_form_submitted.is_valid():
                # delete old quote & author
                ProfileQuote.objects.filter(owner__exact=request.user).delete()
                # save new quote & author (before committing, add owner)
                profile_utils.save_new_quote(request, quote_form_submitted)

                return redirect('/profile')

        elif 'profile_image_form' in request.POST:
            # Make more robust
            # get form data
            profile_image_submitted = ProfileImageForm(request.POST, request.FILES, instance=request.user.profileimage)
            # check validity
            if profile_image_submitted.is_valid():
                profile_image_submitted.save()

                return redirect('/profile')

        elif 'contact_info_form' in request.POST:
            # get form data
            # try to retrieve user's ContactInfo object with POST data
            try:
                contact_info_submitted = ContactInfoForm(data=request.POST, instance=request.user.contactinfo)

            except Exception as e:
                # User likely doesn't have ContactInfo yet.
                # Create default ContactInfo instance for user, then override with POST data
                print(e)
                print(f'Creating ContactInfo for {request.user}...')
                ContactInfo.objects.create(owner=request.user)
                contact_info_submitted = ContactInfoForm(data=request.POST, instance=request.user.contactinfo)

            # check validity
            if contact_info_submitted.is_valid():
                contact_info_submitted.save(commit=False)
                contact_info_submitted.owner = request.user
                contact_info_submitted.save()

                return redirect('/profile')


# consider if login should be required
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
        print(e)

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
        print("this shouldn't happen.")
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
            # get the specific post to edit
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
            raise Http404("Something went wrong retrieving your post to edit.", e)

    elif request.method == 'POST':

        try:
            # form returns the unique slug of a ProfilePost object
            post_slug = request.POST.get('update_post_form')

            # get object with matching slug
            post_to_update = ProfilePost.objects.get(post_slug__exact=post_slug)

            # get updated fields
            new_headline = request.POST.get('headline')
            new_content = request.POST.get('content')

            # save object with updated fields
            post_to_update.headline = new_headline
            post_to_update.content = new_content
            post_to_update.save(update_fields=['headline', 'content'])

        except Exception as e:
            raise Http404("Something went wrong while updating your post. Sorry :( ", e)

        return post(request, post_slug)

    # get requests render the page to edit a post
    return redirect(request, 'kokoro_app/edit_post.html', context)


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
                print('Valid Profile Post.')
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
                    print(f'Generated unique slug: {unique_slug}')
                    new_post.post_slug = unique_slug
                    new_post.save()

                return redirect('/profile')

        elif 'pin_post_form' in request.POST:
            # get form data
            # returns unique slug
            post_to_pin_slug = request.POST.get('pin_post_form')

            # get post with matching slug
            post_to_pin = ProfilePost.objects.get(post_slug__exact=post_to_pin_slug)

            # Create new PinnedProfilePost
            new_pinned_post = PinnedProfilePost()

            # Apply necessary fields and save
            new_pinned_post.original = post_to_pin
            new_pinned_post.pinned_by = request.user
            new_pinned_post.save()

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
                print('Post successfully un-pinned!')

            except Exception as e:
                print(e)
                raise Http404('Something went wrong while un-pinning the post.')

            return redirect('/profile')

        elif 'delete_post_form' in request.POST:
            # get form data (post_slug)
            try:
                post_to_delete_slug = request.POST.get('delete_post_form')
                post_to_delete = ProfilePost.objects.get(post_slug__exact=post_to_delete_slug)
                post_to_delete.delete()
                print('Post Deleted.')
            except Exception as e:
                print(e)
                raise Http404("Something went wrong while deleting your post.")

            return redirect('/profile')


# consider a new app
def search(request):
    """
    Search kokoro user-base based on user-input and display results
    :param request: http request data
    :return:
    """

    # returns text entered into search box
    search_input = request.GET.get('search')

    # returns queryset of User(s) with username value of search_input
    users_queryset = User.objects.filter(username__icontains=f'{search_input}')
    print(users_queryset)

    # Now that we have the requested user(s), we should pass the results to new template
    # can pass additional needed data later

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
            print(e)
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
        # could return dynamic message where "Cancel" was
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
        # consider success message
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

    # get friendship requests
    pending_requests_from_user = FriendshipRequest.objects.filter(from_user__exact=request.user)
    pending_requests_to_user = FriendshipRequest.objects.filter(to_user__exact=request.user)

    context = {
        'friendships': friendships,
        'requests_from_user': pending_requests_from_user,
        'requests_to_user': pending_requests_to_user,
    }

    return render(request, 'kokoro_app/view_friendships.html', context)


@login_required
def remove_friendship_handler(request, friendship_to_remove_id):
    """
    Helper for removing a friendship from a user's friendships (remove User from Friendships object)
    :param request: http post data
    :param friendship_to_remove_id: unique id of a User object
    :return: redirect to view_friendships.html
    """

    successful = friendship_utils.remove_friendship(request, friendship_to_remove_id)

    if successful:
        print('Friendship removed successfully.')
        return redirect('/view_friendships')
    else:
        raise Http404("There was an error redirecting you to page. Friendship Removed.")
