# File for 'balance' feature helper functions/calculations

from kokoro_app.models import Activity
import datetime


def balance(request):
    """Helper function for balance feature on home page"""

    # Get data only from 12:00AM (today)

    # this works, let's use this for now. The only problem is warning that the object is naive, not aware
    # a = Activity.objects.filter(date_added__gte=datetime.datetime.today())

    # return activities related to the mind that were submitted today
    daily_mind = Activity.objects.filter(
        owner__username=request.user,
        activity__iexact="Mind",
        date_added__gte=datetime.datetime.today(),
    )

    return daily_mind
