# File for 'balance' feature helper functions/queries

from kokoro_app.models import Activity
import datetime
import pytz


# Define start of current day for queries
def get_start_of_today():
    """
    Returns the beginning of today (midnight) as an aware datetime
    :return: aware datetime object
    """

    # pytz timezone definition
    tz = pytz.timezone('UTC')

    # Apply timezone info to make datetime aware
    today = datetime.datetime.now(tz=tz)

    # Replace current datetime values with midnight values
    start_of_day = today.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    return start_of_day


# Get all activities submitted today for a logged-in user
def daily_mind(request):
    """
    Returns all mind-related activities submitted today for user
    :param request:
    :return: django queryset
    """

    start_of_today = get_start_of_today()

    # Create queryset for activities submitted after start of today
    daily_mind_activities = Activity.objects.filter(
        owner__username=request.user,
        activity__iexact='mind',
        date_added__gt=start_of_today,
    )

    return daily_mind_activities


def daily_body(request):
    """
    Returns all body-related activities submitted today for user
    :param request:
    :return: django queryset
    """

    start_of_today = get_start_of_today()

    # Create queryset for activities submitted after start of today
    daily_body_activities = Activity.objects.filter(
        owner__username=request.user,
        activity__iexact='body',
        date_added__gt=start_of_today,
    )

    return daily_body_activities


def daily_soul(request):
    """
    Returns all soul-related activities submitted today for user
    :param request:
    :return: django queryset
    """

    start_of_today = get_start_of_today()

    # Create queryset for activities submitted after start of today
    daily_soul_activities = Activity.objects.filter(
        owner__username=request.user,
        activity__iexact='soul',
        date_added__gt=start_of_today,
    )

    return daily_soul_activities


def balance(request):
    """
    Returns a boolean indicating if user has at least 1 activity for mind, body and soul
    :param request:
    :return: boolean
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
