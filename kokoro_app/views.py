from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.db import IntegrityError

from .models import Activity, PerfectBalance, ProfileBio, ProfileDisplayName,\
                    ProfileQuote, ProfileImage, ProfileTimezone, BalanceStreak, ContactInfo, ProfilePost, User
from .forms import ActivityForm, PerfectBalanceForm, ProfileBioForm, ProfileDisplayNameForm, \
                   ProfileQuoteForm, ProfileImageForm, ProfileTimezoneForm, ContactInfoForm, ProfilePostForm
from . import balance, profile_utils
import pytz
import datetime


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

    # Returns all activities submitted today for user
    daily_mind = balance.daily_mind(request)
    daily_body = balance.daily_body(request)
    daily_soul = balance.daily_soul(request)

    # Package daily activities
    all_daily = {
        'daily_mind': daily_mind,
        'daily_body': daily_body,
        'daily_soul': daily_soul
    }

    # Returns boolean indicating if user has submitted at least 1 mind, body, and soul activity today
    # Also returns user balance streak
    balance_data = balance.balance(request)
    found_balance = balance_data[0]
    balance_streak = balance_data[1]

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

    if request.method == "POST":

        # user timezone testing
        if 'tz_form' in request.POST:
            # timezone the user selected
            user_timezone_form = ProfileTimezoneForm(request.POST, instance=request.user.profiletimezone)
            # check validity
            if user_timezone_form.is_valid():
                print("VALID")
                # save form (working)
                user_timezone_form.save()

            return redirect('/profile')

        elif 'perfect_form' in request.POST:
            perfect_form_submitted = PerfectBalanceForm(data=request.POST)
            if perfect_form_submitted.is_valid():
                # delete old perfect balance (working)
                PerfectBalance.objects.filter(owner__exact=request.user).delete()
                # save new perfect balance form with helper function
                profile_utils.save_new_perfect_balance(request, perfect_form_submitted)
                return redirect('/profile')

        elif 'bio_form' in request.POST:
            # user is submitting a biography
            bio_form_submitted = ProfileBioForm(data=request.POST)
            if bio_form_submitted.is_valid():
                # delete old biography
                ProfileBio.objects.filter(owner__exact=request.user).delete()
                # save new biography
                profile_utils.save_new_biography(request, bio_form_submitted)
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
            # Make more robust (and entire function)
            # get form data
            profile_image_submitted = ProfileImageForm(request.POST, request.FILES, instance=request.user.profileimage)
            # check validity
            if profile_image_submitted.is_valid():
                profile_image_submitted.save()
                return redirect('/profile')

        elif 'contact_info_form' in request.POST: # move logic to helper
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

    elif request.method == 'GET':

        if 'profile_to_visit' in request.GET:
            # User is requesting the profile of a different user (search form)
            # redefine user to grab their data rather than logged in user
            user = request.GET.get('profile_to_visit')
            print(user)
        else:
            user = request.user
            print(user)

        # Returns all activities submitted today for user
        daily_mind = balance.daily_mind(request)
        daily_body = balance.daily_body(request)
        daily_soul = balance.daily_soul(request)

        # Package daily activities
        all_daily = {
            'daily_mind': daily_mind,
            'daily_body': daily_body,
            'daily_soul': daily_soul
        }

        # user info for profile page
        user = request.user
        biography = ProfileBio.objects.filter(owner__exact=request.user)
        display_name = ProfileDisplayName.objects.filter(owner__exact=request.user)
        contact_info = ContactInfo.objects.filter(owner__exact=request.user)

        # 'quote_data' is 'quote_data_queryset' parsed to a dictionary
        quote_data_queryset = ProfileQuote.objects.filter(owner__exact=request.user)
        quote_data = profile_utils.parse_quote_data(quote_data_queryset)

        # 'perfect_balance' is 'perfect_balance_queryset parsed into a list
        perfect_balance_queryset = PerfectBalance.objects.filter(owner=request.user)
        perfect_balance = profile_utils.get_perfect_balance_data(perfect_balance_queryset)

        # *** MOVE to helper file
        # get UTC time with offset
        utc_timezone = datetime.datetime.now(tz=pytz.UTC)
        print(f'utc time: {utc_timezone}')
        # get user's saved time zone
        user_timezone_object = ProfileTimezone.objects.filter(owner__exact=request.user)[0] # type= <class 'kokoro_app.models.ProfileTimezone'>
        # convert to string
        user_timezone_string = str(user_timezone_object)
        print(f'users saved TZ string: {user_timezone_string}')
        # convert utc_timezone to user timezone (with offset)
        user_timezone = utc_timezone.astimezone(pytz.timezone(user_timezone_string))
        print(f'user timezone: {user_timezone}')
        print(f"Are these the same time? {user_timezone == utc_timezone}") # true

        # forms for profile page
        perfect_form = PerfectBalanceForm()
        bio_form = ProfileBioForm()
        display_name_form = ProfileDisplayNameForm()
        quote_form = ProfileQuoteForm()
        profile_image_form = ProfileImageForm()
        contact_info_form = ContactInfoForm()

        # testing Profile Posts
        profile_posts = ProfilePost.objects.filter(author__exact=request.user)

        context = {
            'user': user,
            'perfect_form': perfect_form,
            'perfect_balance': perfect_balance,
            'all_daily': all_daily,
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
            # testing profile posts
            'posts': profile_posts,
        }

        return render(request, 'kokoro_app/profile.html', context)


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
    requested_post_data = ProfilePost.objects.filter(post_slug__exact=post_slug)

    # get user's saved time zone
    user_timezone_object = ProfileTimezone.objects.filter(owner__exact=request.user)[0]  # type= <class 'kokoro_app.models.ProfileTimezone'>
    # convert to string
    user_timezone_string = str(user_timezone_object)

    # convert date_published from UTC to user timezone
    date_published_utc = requested_post_data[0].date_published
    date_published_user_tz = balance.convert_to_user_tz(date_published_utc, user_timezone_string)

    context = {
        'requested_post_data': requested_post_data,
        'date_published_user_tz': date_published_user_tz,
    }

    return render(request, 'kokoro_app/post.html', context)


def write_post(request):
    """
    Page for writing a new ProfilePost
    :param request: http request data
    :return: render of 'write post' page
    """

    # testing profile posts
    if request.method == 'POST':
        if 'profile_post_form' in request.POST:
            # get form data
            post_submitted = ProfilePostForm(data=request.POST)

            # check validity
            if post_submitted.is_valid():
                print('Valid Profile Post.')
                new_post = post_submitted.save(commit=False)
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
    else:
        profile_post_form = ProfilePostForm()
        context = {'profile_post_form': profile_post_form}

        return render(request, 'kokoro_app/write_post.html', context)


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
