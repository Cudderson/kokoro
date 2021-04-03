from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Activity, PerfectBalance
from .forms import ActivityForm, PerfectBalanceForm
from . import balance


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

    # Returns boolean indicating if user has submitted at least 1 mind, body, and soul activity today
    found_balance = balance.balance(request)

    context = {
        'form': form,
        'activities': activities,
        'daily_mind': daily_mind,
        'daily_body': daily_body,
        'daily_soul': daily_soul,
        'balance_bool': found_balance,
    }

    return render(request, 'kokoro_app/home.html', context)


@login_required
def profile(request):

    # querying for certain fields still returns the __str__ response:
    # q = PB.objects.filter(perfect_mind__icontains='alice')
    # print(q)
    # QuerySet[<PerfectBalance: M:alice, B:rebecca, S:sage>]>

    # Identify User
    user = request.user

    # *** add form-submission logic ***
    # Site should display 'none' if user doesn't have a perfect balance.
    # If they do, display it.
    p_b = PerfectBalance.objects.filter(owner=request.user)

    # but first, have a user submit some data
    form = PerfectBalanceForm()

    if request.method == "POST":
        form = PerfectBalanceForm(data=request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.owner = request.user
            new_form.save()
            form = PerfectBalanceForm()


    # *** add logic so that form can only be submitted if all 3 (MBS) specified *** (django did this for me)

    context = {
        'user': user,
        'form': form,
        'p_b': p_b,
    }

    return render(request, 'kokoro_app/profile.html', context)
