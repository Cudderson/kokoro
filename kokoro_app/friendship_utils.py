# File for handling operations on the Friendships and FriendshipRequest models
from .models import User, Friendships, FriendshipRequest
from django.http import Http404


def send_friendship_request(request, sending_to_id):
    """
    Helper function for sending a friendship request from one User to another
    :param request: http post data
    :param sending_to_id: unique id (str) of a User object
    :return: boolean indicating operation success or failure
    """

    # logged in user
    from_user = request.user

    try:
        # convert str of id to int
        sending_to_id = int(sending_to_id)

        # get User object of user to send friend request to
        sending_to = User.objects.get(id__exact=sending_to_id)
        to_user = sending_to
    except Exception as e:
        print(e)
        raise Http404(f"Couldn't retrieve user.")

    print(f'It appears that {from_user} is sending a friendship request to {to_user}')

    try:
        # create FriendRequest object and save
        new_friendship_request, created = FriendshipRequest.objects.get_or_create(from_user=from_user, to_user=to_user)
        new_friendship_request.save()
        print("Friendship Request Sent!")

    except Exception as e:
        print(e)
        raise Http404("Something went wrong while processing your friendship request.")

    return True
