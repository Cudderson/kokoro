# File for 'balance' feature helper functions/queries
# includes BalanceStreak help too
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


# defining helper functions for balance() below:
def get_user_timezone(request):
    """
    :param request: http request data
    :return: user's timezone (string)
    """

    user_timezone_object = ProfileTimezone.objects.filter(owner__exact=request.user)[0]
    user_timezone_string = str(user_timezone_object)

    return user_timezone_string


def get_user_balance_streak_object(request):
    """
    :param request: http data
    :return: user's BalanceStreak object from database
    """

    balance_streak_object = BalanceStreak.objects.filter(owner__exact=request.user)[0]

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

    ### When done, add prints and make sure cudderson's streak increments only once, and correct exp_date and D_L_I are saved

    ### I'll try to identify what each code block does, with the goal of cleaning this function and moving logic to other functions
    ### 1. See if any variables are shared into the 4 blocks

    ### block1: user_timezone preference, current_time(UTC and userTZ), user streak expiration date(UTC and userTZ)

    ### block2: checks condition using current_time(userTZ) and balance streak exp date(userTZ)
    ###         user balance_streak_object, then adjusts expiration date(UTC) & resets streak, saves object

    ### block 3: triggers only if all 3 activities fulfilled:
    ###          user balance_streak_object, start_of_today from func, convert to naive date
    ###          user date_last_incremented(UTC and userTZ), user TZ preference,

    ### block 4: user BalanceStreak object, increments streak, new expiration date using userTZ(defined in block 3)
    ###          converts expiration_date to UTC and defines new date_last_incremented(UTC), saves user BalanceStreak object

    ### Summary: Block 1 retrieves variables/calculations for the Block 2 condition.
    ###          Block 3 doesn't use anything from Block 2, apart from user TZ (should probably be defined more globally)
    ###          Block 3 handles what to do if MBS are satisfied. found_balance is set to true, and date() variables are defined for Block 4 condition
    ###          Block 4 increments balance_streak (MBS are fulfilled and today's date is greater than the date it was last incremented
    ###          Block 4 borrows user_timezone_string from Block 3. Also uses userTZ to define new expiration_date, then converts
    ###          it to UTC, and defines date_last_incremented in UTC. Saves BalanceStreak object for user

    ### Blocks 1 and 3 define variables for the conditions of Block 2 and 4.
    ### The goal is to take some of the load off of this function
    ### I guess I can start with Block 1 and move along. (committing at this point in case I want ot go back to this point.)

    ### Function ideas that would be helpful:
    ### - a function that retrieves user's ProfileTimezone object
    ### - a function that retrieves user's BalanceStreak object
    ### - a function that converts aware datetime objects to UTC
    ### - a function that converts aware datetime objects to userTZ

    ### I can start with those, and maybe can add some object saving functions afterwards.
    ### I have created the above functions. In future, will be helpful to add type-checking handlers

    ### Next, I will attempt to factor out logic from balance(), and call my new functions instead (committing here)

    # check expiration_date of balance streak
    # If current time(UTC) is greater than expiration date(UTC), reset streak to 0
    # get user's saved time zone (type = queryset)

    ### get and convert user timezone preference to string
    user_timezone_object = ProfileTimezone.objects.filter(owner__exact=request.user)[0]
    # convert to string
    user_timezone_string = str(user_timezone_object)

    ### define the current UTC time and retrieve user's streak expiration date
    current_time = datetime.datetime.now(tz=pytz.UTC)
    print(f'current time utc: {current_time}')
    balance_streak_expiration_date = BalanceStreak.objects.filter(owner__exact=request.user)[0].expiration_date
    print(f'streak expiration date: {balance_streak_expiration_date}')

    ### Convert current UTC time to current time of user's TZ
    current_time = current_time.astimezone(pytz.timezone(user_timezone_string))

    ### Use 'user_timezone_string' from above to convert user's expiration date to their TZ
    balance_streak_expiration_date = balance_streak_expiration_date.astimezone(pytz.timezone(user_timezone_string))
    print(f'current time user TZ: {current_time}')
    print(f'streak expiration date user tz: {balance_streak_expiration_date}')

    ### check if we should reset the user's streak to 0
    if current_time > balance_streak_expiration_date:
        # add condition to check if streak == 0. If it does, no need to reset it.
        ...
        print("Streak reset to 0 (current time > expiration date)")

        ### get user's BalanceStreak entry, set new expiration date to now (streak is at 0, doesn't matter)
        ### set user's streak to 0
        balance_streak_object = BalanceStreak.objects.filter(owner__exact=request.user)[0]

        balance_streak_object.expiration_date = datetime.datetime.now(tz=pytz.timezone('UTC'))
        balance_streak_object.balance_streak = 0

        ### save new BalanceStreak entry for user
        balance_streak_object.save()

    # If all true, user has found balance
    if mind_fulfilled and body_fulfilled and soul_fulfilled:
        # **********************************************
        # Let's try to put it all together:
        found_balance = True

        # determine if balance streak should be incremented
        # get date of today and date of date_last_incremented

        ### get just the naive date of the start of today (user TZ already applied)
        today = get_start_of_today(request)
        today_date = today.date()

        ### retrieve user's streak 'date_last_incremented' (Stored in UTC time)
        date_last_incremented_utc = BalanceStreak.objects.filter(owner__exact=request.user)[0].date_last_incremented

        ### retrieve user's saved time zone (type = queryset), convert to string
        user_timezone_object = ProfileTimezone.objects.filter(owner__exact=request.user)[0]
        user_timezone_string = str(user_timezone_object)

        ### convert date_last_incremented_utc to user TZ, get date
        date_last_incremented_user_tz = date_last_incremented_utc.astimezone(pytz.timezone(user_timezone_string))
        date_last_incremented_user_tz_date = date_last_incremented_user_tz.date()

        ### remember we are in 'balance fulfilled' block
        ### Check if we should increment streak based on the date_last_incremented (User TZ)


        if today_date > date_last_incremented_user_tz_date:

            ### incrementing streak logic

            ### get user streak, increment by 1
            balance_streak = BalanceStreak.objects.get(owner__exact=request.user)
            balance_streak.balance_streak += 1

            ### add expiration date before saving
            ### should calculate user's local expiration time, then convert to utc

            ### define start of today using user TZ, add 1 day for the start of tomorrow, add 23hrs 59mins for end of tomorrow
            start_of_today_user_tz = datetime.datetime.now(tz=pytz.timezone(user_timezone_string)).replace(hour=0, minute=0, second=0, microsecond=0)
            start_of_tomorrow_user_tz = start_of_today_user_tz + datetime.timedelta(days=1)
            end_of_tomorrow_user_tz = start_of_tomorrow_user_tz + datetime.timedelta(hours=23, minutes=59, seconds=59)

            ### to keep database UTC, convert end of tomorrow to UTC
            end_of_tomorrow_utc = end_of_tomorrow_user_tz.astimezone(pytz.timezone('UTC'))

            ### add expiration date to database
            expiration_date = end_of_tomorrow_utc
            balance_streak.expiration_date = expiration_date

            # add date_last_incremented too
            ### Shouldn't we first define datetime.datetime.now(tz=pytz.timezone(user_timezone_string)) and then convert to UTC?
            ### converting, then converting to UTC doesn't change anything except for the presentation:
            ### therefore, we should save everything in UTC, and the user TZ conversion should be accurate in logic
            balance_streak.date_last_incremented = datetime.datetime.now(tz=pytz.UTC)

            ### save new streak, incremented_date(UTC) and expiration_date(UTC) to database
            print("These values were saved to db:")
            print(f'expiration date: {expiration_date}')
            print(f'date last incremented: {datetime.datetime.now(tz=pytz.UTC)}')
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
