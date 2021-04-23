from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Activity, PerfectBalance, ProfileBio, ProfileDisplayName, ProfileQuote
from .forms import ActivityForm, PerfectBalanceForm, ProfileBioForm, ProfileDisplayNameForm, ProfileQuoteForm
from . import balance, perfect, profile_utils


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
            form = ActivityForm()

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
    found_balance = balance.balance(request)

    context = {
        'form': form,
        'activities': activities,
        'all_daily': all_daily,
        'balance_bool': found_balance,
    }

    return render(request, 'kokoro_app/home.html', context)


@login_required
def profile(request):
    """
    Profile page for kokoro users
    :param request: request data
    :return: HttpResponse
    """
    user = request.user

    perfect_form = PerfectBalanceForm()

    # we now need a form that the user can update their biography with (move to profile_utils after)
    # we can use the submit button's name in the POST request to determine which form the user is submitting
    bio_form = ProfileBioForm()

    display_name_form = ProfileDisplayNameForm()

    quote_form = ProfileQuoteForm()

    # * when a user submits a new form, the old objects should first be deleted (only 1 perfect balance per user)
    if request.method == "POST":
        if 'perfect_form' in request.POST:
            perfect_form = PerfectBalanceForm(data=request.POST)
            if perfect_form.is_valid():
                # delete old perfect balance (working)
                PerfectBalance.objects.filter(owner__exact=request.user).delete()
                new_form = perfect_form.save(commit=False)
                new_form.owner = request.user
                new_form.save()
                perfect_form = PerfectBalanceForm()

        elif 'manage_form' in request.POST:
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

        elif 'display_name_form' in request.POST:
            # get submitted form data
            display_name_form_submitted = ProfileDisplayNameForm(data=request.POST)
            if display_name_form_submitted.is_valid():
                # delete old display name
                ProfileDisplayName.objects.filter(owner__exact=request.user).delete()
                # save new display name with helper function
                profile_utils.save_new_display_name(request, display_name_form_submitted)

        elif 'quote_form' in request.POST:
            # get form data
            quote_form_submitted = ProfileQuoteForm(data=request.POST)
            # check validity
            if quote_form_submitted.is_valid():
                # delete old quote & author
                ProfileQuote.objects.filter(owner__exact=request.user).delete()
                # save new quote & author (before committing, add owner)
                profile_utils.save_new_biography(request, quote_form_submitted)

    # Returns a list
    perfect_balance = perfect.get_perfect_balance_data(request)

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

    # we need to get the users biography
    biography = profile_utils.get_biography(request)

    # We'll also get the user's display name
    display_name = ProfileDisplayName.objects.filter(owner__exact=request.user)

    # get user's profile quote (move to util file later)
    quote_data = ProfileQuote.objects.filter(owner__exact=request.user)
    # convert to string
    quote_data_string = str(quote_data[0])
    # parse string to list
    quote_data_parsed = quote_data_string.split(',,, ')
    # convert to dict for template readability
    quote_data = {
        'quote': quote_data_parsed[0],
        'quote_author': quote_data_parsed[1]
    }

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
        'quote_form': quote_form
    }

    return render(request, 'kokoro_app/profile.html', context)
