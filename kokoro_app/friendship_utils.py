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
        # new code testing pre_delete signal (works)
        friendship_request.accepted = True
        friendship_request.delete()
    except Exception as e:
        raise Http404("Something went wrong deleting the friendship request. Friendship still established.")

    # Return True if no exceptions were raised
    return True


def cancel_friendship_request(request, friendship_request):
    """
    Cancel a friendship request sent by user (delete FriendshipRequest object)
    :param friendship_request: unique id of a FriendshipRequest object
    :param request: http post data
    :return: redirect to friendship_requests.html
    """

    # convert from str >> int
    friendship_request_id = int(friendship_request)

    try:
        # get matching FriendRequest object
        request_to_cancel = FriendshipRequest.objects.get(id__exact=friendship_request_id)

        # delete request
        request_to_cancel.delete()

    except Exception as e:
        raise Http404("Something went wrong cancelling your friendship request.")

    # return True if no Exception raised
    return True


def decline_friendship_request(request, friendship_request):
    """
    Decline a friendship request sent to the user (Delete FriendshipRequest object)
    :param request: http post data
    :param friendship_request: unique id of a FriendshipRequest object
    :return: boolean indicating success or failure
    """

    # convert from str >> int
    friendship_request_id = int(friendship_request)

    try:
        # get matching FriendRequest object
        request_to_decline = FriendshipRequest.objects.get(id__exact=friendship_request_id)

        # delete request
        request_to_decline.delete()

    except Exception as e:
        raise Http404("Something went wrong cancelling your friendship request.")

    # Return True if no Exceptions raised
    return True


def remove_friendship(request, friendship_to_remove_id):
    """
    Remove a friendship from a user's friendships (Delete User from Friendships object)
    :param request: http post data
    :param friendship_to_remove_id: unique id (str) of a User object
    :return: redirect to view_friendships.html
    """

    try:
        # convert str to int
        friendship_to_remove_id = int(friendship_to_remove_id)
        # get User object matching the id passed from template
        friendship_to_remove = User.objects.get(id__exact=friendship_to_remove_id)
    except Exception as e:
        raise Http404("Something went wrong identifying the friendship to remove.")

    try:
        # get current user's Friendships ManyRelatedManager
        user_friendships, created = Friendships.objects.get_or_create(owner=request.user)
        # get friendship_to_remove's Friendships ManyRelatedManager
        friendship_to_remove_friendships, created = Friendships.objects.get_or_create(owner=friendship_to_remove)
    except Exception as e:
        raise Http404("Something went wrong while identifying friendships.")

    try:
        # remove friendship_to_remove from user's Friendships.friendships field (MTM)
        # remove user from friendship_to_remove's Friendship.friendships field (MTM)
        user_friendships.friendships.remove(friendship_to_remove)
        friendship_to_remove_friendships.friendships.remove(request.user)
    except Exception as e:
        raise Http404("Something went wrong while removing your friendship.")

    # return True if no Exceptions raised
    return True
