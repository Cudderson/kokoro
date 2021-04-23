# Helper file for profile page logic
from .models import ProfileBio, ProfileDisplayName


def get_biography(request):
    """
    :param request: http request data
    :return: a user's biography
    """

    biography = ProfileBio.objects.filter(owner__exact=request.user)

    return biography


def get_display_name(request):
    """
    :param request: http request data
    :return: a user's display name for profile
    """

    display_name = ProfileDisplayName.objects.filter(owner__exact=request.user)

    return display_name
