# Helper file for profile page logic
from django.http import Http404


def save_new_display_name(request, display_name_form, current_display_name):
    """
    Save a validated form submitted by user
    :param request: http post data
    :param display_name_form: a validated form for changing user's display name
    :param current_display_name: ProfileDisplayName object for user
    :return: n/a
    """

    try:
        current_display_name.display_name = display_name_form['display_name'].value()
        current_display_name.save(
            update_fields=[
                'display_name'
            ]
        )
    except Exception as e:
        raise Http404("Something went wrong while saving your display name.", e)


# repeat the above for saving the other forms
def save_new_biography(request, bio_form, current_biography):
    """
    Save a validated form submitted by user
    :param request: http post data
    :param bio_form: a validated form for changing user's biography
    :param current_biography: Biography object for user
    :return: n/a
    """

    try:
        current_biography.biography = bio_form['biography'].value()

        current_biography.save(
            update_fields=[
                'biography'
            ]
        )

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


def save_new_perfect_balance(request, perfect_form, current_perfect_balance):
    """
    Save a validated form submitted by user
    :param request: http post data
    :param perfect_form: validated form for changing user's perfect balance
    :param current_perfect_balance: PerfectBalance object belonging to user
    :return: n/a
    """

    try:
        # apply form values to existing PerfectBalance object
        current_perfect_balance.perfect_mind = perfect_form['perfect_mind'].value()
        current_perfect_balance.perfect_body = perfect_form['perfect_body'].value()
        current_perfect_balance.perfect_soul = perfect_form['perfect_soul'].value()

        # update fields and save
        current_perfect_balance.save(
            update_fields=[
                'perfect_mind',
                'perfect_body',
                'perfect_soul'
            ]
        )
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
