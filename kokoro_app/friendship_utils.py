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

    try:
        # create FriendRequest object and save
        new_friendship_request, created = FriendshipRequest.objects.get_or_create(from_user=from_user, to_user=to_user)
        new_friendship_request.save()
        print("Friendship Request Sent!")
    except Exception as e:
        print(e)
        raise Http404("Something went wrong while processing your friendship request.")

    return True


def accept_friendship_request(request, sent_by):
    """
    Helper function for accepting(saving) a Friendships object and deleting the corresponding FriendRequest object
    :param request: http post data
    :param sent_by: unique id (str) of a User object
    :return: boolean indicating success or failure
    """

    # get id of sender from template form
    sent_by_id = int(sent_by)

    # get User object of the friend to add
    new_friend = User.objects.get(id__exact=sent_by_id)

    try:
        # create Friendship instance for current user
        # 'get_or_create' returns tuple containing the object, and if object was created or not
        user_friendships, created_for_user = Friendships.objects.get_or_create(owner=request.user)
        new_friend_friendships, created_for_friend = Friendships.objects.get_or_create(owner=new_friend)
    except Exception as e:
        print(e)
        raise Http404("Something went wrong while retrieving friendships.")

    try:
        # add new friend to user's friendships (Friendship.friendships (MTMField)
        user_friendships.friendships.add(new_friend)

        # add user to new friend's friendships
        new_friend_friendships.friendships.add(request.user)

        print(f'{request.user} is now friends with {new_friend}')
    except Exception as e:
        raise Http404("Something went wrong while establishing friendship.")

    try:
        # Get friendship request object to delete
        friendship_request = FriendshipRequest.objects.get(from_user=new_friend, to_user=request.user)
        friendship_request.delete()
    except Exception as e:
        raise Http404("Something went wrong deleting the friendship request. Friendship still established.")

    # Return True if no exceptions were raised
    return True
