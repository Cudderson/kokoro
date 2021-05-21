# Helper file for profile page logic
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from itertools import chain


def get_profile_to_visit(request):
    """
    Use request data to determine the id of a user's profile page to render
    :param request: http data
    :return: a unique id of a User object
    """

    if 'profile_to_visit' in request.GET:

        # User is requesting the profile of a different user (search form)
        user_id = request.GET.get('profile_to_visit')

    elif 'profile_to_visit' in request.session:

        # User is requesting the profile of a different user (notification)
        user_id = request.session['profile_to_visit']
        # remove variable from session to avoid cross-ups
        del request.session['profile_to_visit']

    else:
        # Logged in user is requesting their own profile
        user_id = request.user.id

    try:
        return user_id

    except Exception as e:
        raise Http404("Something went wrong while retrieving the profile you requested.", e)


def get_user_display_name(user, model):
    """
    Retrieves ProfileDisplayName object for User from database
    :param user: User object
    :param model: Model ProfileDisplayName
    :return: ProfileDisplayName object for User
    """

    try:
        display_name = model.objects.get(owner__exact=user.id)
    except ObjectDoesNotExist:
        display_name = ""

    return display_name


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


def get_user_biography(user, model):
    """
    Retrieves ProfileBiography object for User
    :param user: User object
    :param model: Model ProfileBio
    :return: ProfileBio object
    """

    try:
        biography = model.objects.get(owner__exact=user.id)
    except ObjectDoesNotExist:
        biography = ""

    return biography


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


def save_new_quote(request, quote_form, current_quote):
    """
    Save a validated form submitted by user
    :param request: http post data
    :param quote_form: a validated form for changing user's profile quote
    :param current_quote: ProfileQuote object for user
    :return: n/a
    """

    try:
        current_quote.quote = quote_form['quote'].value()
        current_quote.quote_author = quote_form['quote_author'].value()

        current_quote.save(
            update_fields=[
                'quote',
                'quote_author'
            ]
        )
    except Exception as e:
        raise Http404("Something went wrong while saving your quote.", e)


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


def get_quote_data(user, model):
    """

    :param user:
    :param model:
    :return:
    """

    # 'quote_data' is 'quote_data_queryset' parsed to a dictionary
    try:
        quote_data_queryset = model.objects.get(owner__exact=user.id)
    except ObjectDoesNotExist:
        quote_data_queryset = ""

    quote_data = parse_quote_data(quote_data_queryset)

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


def get_perfect_balance_queryset(user, model):
    """

    :param user:
    :param model:
    :return:
    """

    try:
        perfect_balance_queryset = model.objects.get(owner=user.id)
    except ObjectDoesNotExist:
        perfect_balance_queryset = ""

    return perfect_balance_queryset


def sort_posts_together(profile_posts, pinned_posts):
    """
    Sorts ProfilePost & PinnedPost objects together by date_published (reversed)
    :param profile_posts: ProfilePost objects belonging to user (queryset)
    :param pinned_posts: PinnedProfilePost objects belonging to user (queryset)
    :return: Sorted list of ProfilePost and PinnedProfilePost objects
    """

    try:
        # Sort querysets into one list using 'date_published' field, reverse
        posts = sorted(
            chain(profile_posts, pinned_posts),
            key=lambda post_or_pinned: post_or_pinned.date_published, reverse=True
        )
    except Exception as e:
        raise Http404("Something went wrong while sorting posts.", e)

    return posts


def get_profile_posts(user, model):
    """

    :param user:
    :param model:
    :return:
    """

    profile_posts = model.objects.filter(author__exact=user.id)

    return profile_posts


def get_pinned_profile_posts(user, model):
    """

    :param user:
    :param model:
    :return:
    """

    pinned_posts = model.objects.filter(pinned_by__exact=user.id)

    return pinned_posts


def get_user_contact_info(user, model):
    """

    :param user:
    :param model:
    :return:
    """

    try:
        contact_info = model.objects.filter(owner__exact=user.id)
    except ObjectDoesNotExist:
        contact_info = ""

    return contact_info


def get_profile_data(user, profile_models):
    """
    Retrieves User data needed for views.profile
    :param user: User object
    :param profile_models: django Models relating to a User's profile
    :return: dictionary of profile data for a User
    """

    biography = get_user_biography(user, profile_models['biography_model'])

    display_name = get_user_display_name(user, profile_models['display_name_model'])

    contact_info = get_user_contact_info(user, profile_models['contact_info_model'])

    quote_data = get_quote_data(user, profile_models['quote_model'])

    # 'perfect_balance' is 'perfect_balance_queryset' parsed into a list
    perfect_balance_queryset = get_perfect_balance_queryset(user, profile_models['perfect_balance_model'])
    perfect_balance = get_perfect_balance_data(perfect_balance_queryset)

    # get ProfilePost and PinnedProfilePost objects belonging to user
    profile_posts = get_profile_posts(user, profile_models['post_model'])
    pinned_posts = get_pinned_profile_posts(user, profile_models['pinned_post_model'])

    # returns list of User ProfilePost & PinnedPost objects sorted together by date_published (reversed)
    posts = sort_posts_together(profile_posts, pinned_posts)

    profile_data = {
        'biography': biography,
        'display_name': display_name,
        'contact_info': contact_info,
        'quote_data': quote_data,
        'perfect_balance': perfect_balance,
        'posts': posts,
    }

    return profile_data
