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
    :return: ...
    """

    try:
        new_display_name = display_name_form.save(commit=False)
        new_display_name.owner = request.user
        new_display_name.save()
    except Exception as e:
        print(e)
        raise Http404("Something went wrong while saving your display name.")

    return True

# repeat the above for saving the other forms
