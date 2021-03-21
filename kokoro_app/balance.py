# File for 'balance' feature helper functions/queries

from kokoro_app.models import Activity
import datetime

# Get all activities submitted today for a logged-in user


def daily_mind(request):
    """Returns all mind-related activites submitted today for user"""

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
    """
    Returns a boolean indicating if user has at least 1 activity for mind, body and soul
    """

    # Determine if user has submitted at least 1 activity for mind, body and soul
    mind_fulfilled = True if len(daily_mind(request)) > 0 else False
    body_fulfilled = True if len(daily_body(request)) > 0 else False
    soul_fulfilled = True if len(daily_soul(request)) > 0 else False

    # If all true, user has found balance
    if mind_fulfilled and body_fulfilled and soul_fulfilled:
        found_balance = True
    else:
        found_balance = False

    # Convert bool to string for template evaluation (Jinja2)
    return str(found_balance)
