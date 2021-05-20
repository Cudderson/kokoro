# File for 'balance' feature & 'BalanceStreak' helper functions/queries

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
    user_timezone_object = ProfileTimezone.objects.get(owner__exact=request.user)

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
def daily_mind(request, start_of_today):
    """
    Returns all mind-related activities submitted today for user
    :param request: http data
    :param start_of_today: TZ-aware datetime indicating 12:00AM today
    :return: django queryset
    """

    # Create queryset for activities submitted after start of today
    daily_mind_activities = Activity.objects.filter(
        owner__username=request.user,
        activity__iexact='mind',
        date_added__gt=start_of_today,
    )

    return daily_mind_activities


def daily_body(request, start_of_today):
    """
    Returns all body-related activities submitted today for user
    :param request: http data
    :param start_of_today: TZ-aware datetime indicating 12:00AM today
    :return: django queryset
    """

    # Create queryset for activities submitted after start of today
    daily_body_activities = Activity.objects.filter(
        owner__username=request.user,
        activity__iexact='body',
        date_added__gt=start_of_today,
    )

    return daily_body_activities


def daily_soul(request, start_of_today):
    """
    Returns all soul-related activities submitted today for user
    :param request: http data
    :param start_of_today: TZ-aware datetime indicating 12:00AM today
    :return: django queryset
    """

    # Create queryset for activities submitted after start of today
    daily_soul_activities = Activity.objects.filter(
        owner__username=request.user,
        activity__iexact='soul',
        date_added__gt=start_of_today,
    )

    return daily_soul_activities


def get_user_timezone(request):
    """
    :param request: http request data
    :return: user's timezone (string)
    """

    user_timezone_object = ProfileTimezone.objects.get(owner__exact=request.user)
    user_timezone_string = str(user_timezone_object)

    return user_timezone_string


def get_user_balance_streak_object(request):
    """
    :param request: http data
    :return: user's BalanceStreak object from database
    """

    balance_streak_object = BalanceStreak.objects.get(owner__exact=request.user)

    return balance_streak_object


def convert_to_utc(datetime_to_convert):
    """
    :param datetime_to_convert: an aware datetime object
    :return: an aware datetime object with UTC timezone configuration
    """

    utc_datetime_object = datetime_to_convert.astimezone(pytz.UTC)

    return utc_datetime_object


def convert_to_user_tz(datetime_to_convert, user_timezone):
    """
    :param datetime_to_convert: an aware datetime object
    :param user_timezone: user's timezone from database (string)
    :return: an aware datetime object with User TZ configuration
    """

    user_tz_datetime_object = datetime_to_convert.astimezone(pytz.timezone(user_timezone))

    return user_tz_datetime_object


def get_current_time_user_tz(user_timezone_string):
    """
    :param user_timezone_string: self-explanatory
    :return: an aware datetime of the current time in the user's timezone
    """

    # define the current UTC time
    current_time = datetime.datetime.now(tz=pytz.UTC)

    # Convert current UTC time to current time of user's TZ
    current_time_user_tz = convert_to_user_tz(current_time, user_timezone_string)

    return current_time_user_tz


def get_expiration_date_user_tz(user_balance_streak_object, user_timezone_string):
    """
    :param user_timezone_string: self-explanatory
    :param user_balance_streak_object: user's BalanceStreak object from database
    :return: a user's balance streak expiration date configured to user's timezone
    """

    balance_streak_expiration_date_utc = user_balance_streak_object.expiration_date

    # Convert expiration_date(UTC) to user timezone
    balance_streak_expiration_date_user_tz = convert_to_user_tz(balance_streak_expiration_date_utc, user_timezone_string)

    return balance_streak_expiration_date_user_tz


def reset_balance_streak(user_balance_streak_object):
    """
    Resets user's balance streak to 0 and sets arbitrary expiration date
    :param user_balance_streak_object: a user's BalanceStreak object from database
    :return:
    """

    # set new expiration date to now (streak is at 0, doesn't matter)
    # reset user's balance streak to 0
    user_balance_streak_object.expiration_date = datetime.datetime.now(tz=pytz.timezone('UTC'))
    user_balance_streak_object.balance_streak = 0

    # save updated BalanceStreak object for user
    user_balance_streak_object.save(update_fields=['balance_streak'])

    # make better return
    return 'streak reset'


def get_today_date(request):
    """
    :param request: http data
    :return: a naive date object of today's date
    """

    today = get_start_of_today(request)
    today_date = today.date()

    return today_date


def get_date_last_incremented_user_tz_date(user_balance_streak_object, user_timezone_string):
    """
    Retrieves user's balance streak date_last_incremented as UTC, converts to user's TZ, converts to naive date
    :param user_balance_streak_object: a user's BalanceStreak object from database
    :param user_timezone_string: self-explanatory
    :return: a naive date object of a user's streak's date_last_incremented
    """

    # retrieve user's streak 'date_last_incremented' (Stored in UTC time)
    date_last_incremented_utc = user_balance_streak_object.date_last_incremented

    # convert date_last_incremented_utc to user TZ, get date
    date_last_incremented_user_tz = convert_to_user_tz(date_last_incremented_utc, user_timezone_string)
    date_last_incremented_user_tz_date = date_last_incremented_user_tz.date()

    return date_last_incremented_user_tz_date


def new_expiration_date(request):
    """
    Calculates a new expiration date for a user's balance streak as the end of the next day, converts to UTC
    :param request: http data
    :return: a new expiration date for a user's balance streak
    """

    # define start of today using user TZ, add 1 day for the start of tomorrow, add 23hrs 59mins for end of tomorrow
    start_of_today_user_tz = get_start_of_today(request)
    start_of_tomorrow_user_tz = start_of_today_user_tz + datetime.timedelta(days=1)
    end_of_tomorrow_user_tz = start_of_tomorrow_user_tz + datetime.timedelta(hours=23, minutes=59, seconds=59)

    # to keep database UTC, convert end of tomorrow to UTC
    end_of_tomorrow_utc = convert_to_utc(end_of_tomorrow_user_tz)

    expiration_date = end_of_tomorrow_utc

    return expiration_date


def update_balance_streak(request, expiration_date):
    """
    Updates/Saves a user's BalanceStreak with new streak value, expiration date(UTC), and date last incremented(UTC)
    :param expiration_date: an aware datetime object (UTC) that defines when user's balance streak will be reset
    :param request: http data
    :return:
    """

    # get user streak, increment by 1
    user_balance_streak = BalanceStreak.objects.get(owner__exact=request.user)
    user_balance_streak.balance_streak += 1

    # set new expiration date (UTC)
    user_balance_streak.expiration_date = expiration_date

    # update date_last_incremented (UTC)
    user_balance_streak.date_last_incremented = datetime.datetime.now(tz=pytz.UTC)

    # save new streak, incremented_date(UTC) and expiration_date(UTC) to database
    print("These values were saved to db:")
    print(f'expiration date: {expiration_date}')
    print(f'date last incremented: {datetime.datetime.now(tz=pytz.UTC)}')

    user_balance_streak.save(
        update_fields=[
            'balance_streak',
            'expiration_date',
            'date_last_incremented'
        ]
    )

    return f"{request.user}'s balance streak was updated"


def get_user_balance_streak_value(request):
    """

    :param request: http data
    :return: a user's balance streak value (int)
    """

    balance_streak_object = BalanceStreak.objects.get(owner__exact=request.user)
    balance_streak_value = balance_streak_object.balance_streak

    return balance_streak_value


def balance(request, daily_mind_queryset, daily_body_queryset, daily_soul_queryset):
    """
    Returns a boolean indicating if user has at least 1 activity for mind, body and soul
    :param request: http data
    :param daily_mind_queryset: Queryset of Activity objects relating to the Mind
    :param daily_body_queryset: Queryset of Activity objects relating to the Body
    :param daily_soul_queryset: Queryset of Activity objects relating to the Soul
    :return: boolean
    """

    mind_fulfilled = True if daily_mind_queryset else False
    body_fulfilled = True if daily_body_queryset else False
    soul_fulfilled = True if daily_soul_queryset else False

    # Get user timezone (string)
    user_timezone_string = get_user_timezone(request)

    # retrieve user's streak object
    user_balance_streak_object = get_user_balance_streak_object(request)

    # get current time for user's timezone
    current_time_user_tz = get_current_time_user_tz(user_timezone_string)

    # get user's streak expiration date (user TZ)
    balance_streak_expiration_date_user_tz = get_expiration_date_user_tz(user_balance_streak_object, user_timezone_string)

    # Check if we should reset the user's streak to 0
    if current_time_user_tz > balance_streak_expiration_date_user_tz:

        # add condition to check if streak == 0. If it does, no need to reset it.
        balance_streak_value = get_user_balance_streak_value(request)

        if balance_streak_value != 0:

            print("Streak reset to 0 (current time > expiration date)")
            reset_balance_streak(user_balance_streak_object)

    # If all true, user has found balance
    if mind_fulfilled and body_fulfilled and soul_fulfilled:

        found_balance = True

        # determine if balance streak should be incremented
        # get the naive date of the start of today (user TZ already applied)
        today_date = get_today_date(request)

        # get date of streak's date_last_incremented
        date_last_incremented_user_tz_date = get_date_last_incremented_user_tz_date(user_balance_streak_object, user_timezone_string)

        if today_date > date_last_incremented_user_tz_date:

            # Increment Streak (MBS fulfilled and today_date > date_last_incremented)

            # Get new expiration date for user's balance streak
            expiration_date = new_expiration_date(request)

            # Update/Save user's BalanceStreak
            update_balance_streak(request, expiration_date)

    else:
        found_balance = False

    # Convert bool to string for template evaluation (Jinja2), return user balance streak
    balance_streak_value = get_user_balance_streak_value(request)

    return {
        'found_balance': str(found_balance),
        'balance_streak_value': balance_streak_value
    }
