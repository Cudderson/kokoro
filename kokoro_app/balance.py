from kokoro_app.models import Activity


def balance(request):
    """Helper function for balance feature on home page"""

    # Get data only from 12:00AM (today)
    daily_mind = Activity.objects.filter(

        owner__username=request.user,
        activity__iexact="Mind",

    )