# Helper file for profile page logic
from django.http import Http404
from .models import ProfileBio


def get_biography(request):
    """
    :param request: http request data
    :return: a user's biography
    """

    biography = ProfileBio.objects.filter(owner__exact=request.user)

    return biography


# attempting to use this file to take the load off of the view function
# saving the form seems to be the bulk to remove
def save_new_display_name(request, display_name_form):
    """
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

