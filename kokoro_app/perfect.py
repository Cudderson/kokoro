# Helper functions for 'perfect balance' feature on profile page

from kokoro_app.models import PerfectBalance


def get_perfect_balance_data(request):
    """
    Checks for existence of a user's 'perfect balance' preferences
    :param request: request data
    :return: user data or string "False"
    """

    # set perfect_balance to false if user hasn't created one yet (empty querySet)
    perfect_balance = PerfectBalance.objects.filter(owner=request.user)

    # convert queryset result to string, then to list, then capitalize for UI
    perfect_balance = str(perfect_balance[0])
    perfect_balance = perfect_balance.split(", ")
    perfect_balance = [activity.capitalize() for activity in perfect_balance]

    if not perfect_balance:
        # Convert boolean to string for template comparison
        perfect_balance = str(False)

    return perfect_balance
