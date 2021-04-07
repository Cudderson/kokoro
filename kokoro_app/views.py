from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Activity, PerfectBalance
from .forms import ActivityForm, PerfectBalanceForm
from . import balance, perfect


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

    # but first, have a user submit some data
    form = PerfectBalanceForm()

    # * when a user submits a new form, the old objects should first be deleted (only 1 perfect balance per user)
    if request.method == "POST":
        form = PerfectBalanceForm(data=request.POST)
        if form.is_valid():
            # delete old perfect balance (working)
            PerfectBalance.objects.all().delete()
            new_form = form.save(commit=False)
            new_form.owner = request.user
            new_form.save()
            form = PerfectBalanceForm()

    perfect_balance = perfect.get_perfect_balance_data(request)

    # *** add logic so that form can only be submitted if all 3 (MBS) specified *** (django did this for me)

    context = {
        'user': user,
        'form': form,
        'perfect_balance': perfect_balance,
    }

    return render(request, 'kokoro_app/profile.html', context)
