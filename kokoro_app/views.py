from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Activity, PerfectBalance, ProfileBio, ProfileDisplayName, ProfileQuote, ProfileImage, ProfileTimezone, BalanceStreak
from .forms import ActivityForm, PerfectBalanceForm, ProfileBioForm, ProfileDisplayNameForm, ProfileQuoteForm, ProfileImageForm, ProfileTimezoneForm
from . import balance, profile_utils
import pytz
import datetime


def index(request):
    """Landing Page for Kokoro"""

    return render(request, 'kokoro_app/index.html', {})


@login_required()
def home(request):
    """Home Page for Kokoro users"""

    form = ActivityForm()

    if request.method == "POST":
        form = ActivityForm(data=request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.owner = request.user
            new_form.save()
            return redirect('/home')

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
        'form': form,
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
    :return: HttpResponse
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

        # *** Do this later if decide to include on profile page ***
        elif 'manage_form' in request.POST: # this functionality isn't included yet (form to delete activities)
            # could move some logic to helper file
            result = request.POST
            # checkbox attrs are key=id_of_entry, value=on/off
            # By retrieving the key(s), we know what values to delete from database
            # '[1:len(result) - 1]' removes the csrf_token and button name from result
            result = list(result.keys())[1:len(result) - 1]

            # Delete objects based on their 'id' obtained from the queryDict/QueryList
            acts_to_delete = Activity.objects.filter(id__in=result)
            acts_to_delete.delete()

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

    # 'quote_data' is 'quote_data_queryset' parsed to a dictionary
    quote_data_queryset = ProfileQuote.objects.filter(owner__exact=request.user)
    quote_data = profile_utils.parse_quote_data(quote_data_queryset)

    # 'perfect_balance' is 'perfect_balance_queryset parsed into a list
    perfect_balance_queryset = PerfectBalance.objects.filter(owner=request.user)
    perfect_balance = profile_utils.get_perfect_balance_data(perfect_balance_queryset)

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
        # testing tz
        'timezones': pytz.common_timezones,
        'user_timezone_object': user_timezone_object,
        'user_timezone': user_timezone,
    }

    return render(request, 'kokoro_app/profile.html', context)
