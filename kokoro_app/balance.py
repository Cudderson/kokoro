# File for 'balance' feature helper functions/queries
# This file violates DRY methods. Consider making less database queries if possible

from django.utils.timezone import is_aware
from kokoro_app.models import Activity, ProfileTimezone, BalanceStreak
import datetime
import pytz


# Define start of current day for queries
def get_start_of_today(request):
    """
    Returns the beginning of today (midnight) as an aware datetime with respect to user's timezone
    :return: aware datetime object
    """

    # get UTC time with offset
    utc_timezone = datetime.datetime.now(tz=pytz.UTC)

    # get user's saved time zone (type = queryset)
    user_timezone_object = ProfileTimezone.objects.filter(owner__exact=request.user)[0]

    # convert to string
    user_timezone_string = str(user_timezone_object)

    # convert utc_timezone to user timezone (with offset)
    today = utc_timezone.astimezone(pytz.timezone(user_timezone_string))

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

    start_of_today = get_start_of_today(request)

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

    start_of_today = get_start_of_today(request)

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

    start_of_today = get_start_of_today(request)

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
        # **********************************************
        # Let's try to put it all together:
        found_balance = True

        # determine if balance streak should be incremented
        # get date of today and date of date_last_incremented

        # today (user tz already applied)
        today = get_start_of_today(request)
        today_date = today.date()

        # get date() of date_last_incremented
        date_last_incremented_utc = BalanceStreak.objects.filter(owner__exact=request.user)[0].date_last_incremented

        # get user's saved time zone (type = queryset)
        user_timezone_object = ProfileTimezone.objects.filter(owner__exact=request.user)[0]
        # convert to string
        user_timezone_string = str(user_timezone_object)

        # convert date_last_incremented_utc to user TZ, get date
        date_last_incremented_user_tz = date_last_incremented_utc.astimezone(pytz.timezone(user_timezone_string))
        date_last_incremented_user_tz_date = date_last_incremented_user_tz.date()

        # check if streak incremented today:
        if today_date > date_last_incremented_user_tz_date:

            # increment streak, set new expiration
            balance_streak = BalanceStreak.objects.get(owner__exact=request.user)
            balance_streak.balance_streak += 1

            # add expiration date before saving
            start_of_today_utc = datetime.datetime.now(tz=pytz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
            start_of_tomorrow_utc = start_of_today_utc + datetime.timedelta(days=1)
            end_of_tomorrow_utc = start_of_tomorrow_utc + datetime.timedelta(hours=23, minutes=59, seconds=59)

            expiration_date = end_of_tomorrow_utc
            balance_streak.expiration_date = expiration_date

            # add date_last_incremented too
            balance_streak.date_last_incremented = datetime.datetime.now(tz=pytz.UTC)

            balance_streak.save()
        else:
            ...
            # don't increment streak
    else:
        found_balance = False

    # Convert bool to string for template evaluation (Jinja2), return user balance streak
    balance_streak = BalanceStreak.objects.get(owner__exact=request.user)
    balance_streak = balance_streak.balance_streak
    return str(found_balance), balance_streak
