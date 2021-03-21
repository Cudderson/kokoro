# File for 'balance' feature helper functions/calculations

from kokoro_app.models import Activity
import datetime


def daily_mind(request):
    """Returns all mind-related activites submitted today for user"""
    # Get data only from 12:00AM (today)

    # this works, let's use this for now. The only problem is warning that the object is naive, not aware
    # a = Activity.objects.filter(date_added__gte=datetime.datetime.today())

    # return activities related to the mind that were submitted today
    daily_mind_activities = Activity.objects.filter(
        owner__username=request.user,
        activity__iexact='mind',
        date_added__gte=datetime.datetime.today(),
    )

    return daily_mind_activities


def daily_body(request):
    """Returns all body-related activites submitted today for user"""

    daily_body_activities = Activity.objects.filter(
        owner__username=request.user,
        activity__iexact='body',
        date_added__gte=datetime.datetime.today(),
    )

    return daily_body_activities


def daily_soul(request):
    """Returns all soul-related activites submitted today for user"""

    daily_soul_activities = Activity.objects.filter(
        owner__username=request.user,
        activity__iexact='soul',
        date_added__gte=datetime.datetime.today(),
    )

    return daily_soul_activities


def balance(request):
    """Helper function for balance feature on home page"""
    ...


