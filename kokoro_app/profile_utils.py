# Helper file for profile page logic
from .models import ProfileBio


def get_biography(request):
    """
    :param request: http request data
    :return: a user's biography
    """

    biography = ProfileBio.objects.filter(owner__exact=request.user)

    return biography
