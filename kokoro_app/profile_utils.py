# Helper file for profile page logic
from django.http import Http404


def save_new_display_name(request, display_name_form):
    """
    Save a validated form submitted by user
    :param request: http post data
    :param display_name_form: a validated form for changing user's display name
    :return: n/a
    """

    try:
        new_display_name = display_name_form.save(commit=False)
        new_display_name.owner = request.user
        new_display_name.save()
    except Exception:
        raise Http404("Something went wrong while saving your display name.")


# repeat the above for saving the other forms
def save_new_biography(request, bio_form):
    """
    Save a validatedform submitted by user
    :param request: http post data
    :param bio_form: a validated form for changing user's biography
    :return: n/a
    """

    try:
        new_bio_form = bio_form.save(commit=False)
        new_bio_form.owner = request.user
        new_bio_form.save()
    except Exception:
        raise Http404(f"Something went wrong while saving your biography.")


def save_new_quote(request, quote_form):
    """
    Save a validated form submitted by user
    :param request: http post data
    :param quote_form: a validated form for changing user's profile quote
    :return: n/a
    """

    try:
        new_quote = quote_form.save(commit=False)
        new_quote.owner = request.user
        new_quote.save()
    except Exception:
        raise Http404("Something went wrong while saving your quote.")


def parse_quote_data(quote_data_queryset):
    """
    Takes in a django queryset of a user's profile quote and converts to dictionary
    :param quote_data_queryset: a django queryset
    :return: parsed dictionary of the queryset
    """

    if quote_data_queryset:
        quote_data = {
            'quote': quote_data_queryset.quote,
            'quote_author': quote_data_queryset.quote_author
        }
    else:
        quote_data = {'quote': '', 'quote_author': ''}

    return quote_data


def save_new_perfect_balance(request, perfect_form):
    """
    Save a validated form submitted by user
    :param request: http post data
    :param perfect_form: validated form for changing user's perfect balance
    :return: n/a
    """

    try:
        new_form = perfect_form.save(commit=False)
        new_form.owner = request.user
        new_form.save()
    except Exception:
        raise Http404("Something went wrong while saving your perfect balance activities.")


def get_perfect_balance_data(perfect_balance_queryset):
    """
    Takes in a django queryset of a user's perfect balance and converts it to a list
    :param perfect_balance_queryset: a django queryset
    :return: parsed list of the queryset
    """

    if perfect_balance_queryset:
        perfect_balance = {
            'perfect_mind': perfect_balance_queryset.perfect_mind,
            'perfect_body': perfect_balance_queryset.perfect_body,
            'perfect_soul': perfect_balance_queryset.perfect_soul,
        }
    else:
        perfect_balance = {
            'perfect_mind': "",
            'perfect_body': "",
            'perfect_soul': "",
        }

    return perfect_balance
