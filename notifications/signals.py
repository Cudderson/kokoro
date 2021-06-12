# signals for sending(creating) notifications

from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver

from kokoro_app.models import FriendshipRequest, Friendships, PinnedProfilePost, ProfilePost
from .models import Notification

from django.core.signals import request_finished

from django.core.exceptions import ValidationError


# Use this  to test signals if not working
# @receiver(request_finished)
# def test_signal(sender, **kwargs):
#     print("Your signal is working.")


# This signal is being called twice.. *NEED TO FIX*
@receiver(post_save, sender=FriendshipRequest, dispatch_uid="my_unique_identifier")
def create_friendship_request_notification(sender, instance, created, **kwargs):
    """
    Create a Notification when a FriendshipRequest object is created
    :param sender:
    :param instance: FriendshipRequest object
    :param created: boolean indicating creation of FriendshipRequest object
    :param kwargs:
    :return:
    """

    # prints out the actual instance object of FriendshipRequest that was saved
    # prints twice, possibly due to HTTPReferrer??
    print(instance, "OK")

    if created:

        friendship_request_notification = Notification(
            type=1,
            recipient=instance.to_user,
            sent_from=instance.from_user,
            message=f"{instance.from_user} sent you a friendship request!",
            reference=instance,
        )

        try:
            friendship_request_notification.full_clean()
            print("CLEAN")
            friendship_request_notification.save()
        except ValidationError as e:
            print(e)


@receiver(pre_delete, sender=FriendshipRequest)
def accept_friendship_request_notification(sender, instance, **kwargs):
    """
    Creates a Notification object when a FriendshipRequest is deleted (provided that accepted == True)
    :param sender:
    :param instance: FriendshipRequest object
    :param kwargs:
    :return:
    """

    # FriendshipRequest.accepted == True when accepted, before deletion
    if instance.accepted:

        friendship_accepted_notification = Notification(
            type=2,
            recipient=instance.from_user,
            sent_from=instance.to_user,
            message=f'{instance.to_user} accepted your friendship request!',
            reference=instance,
        )

        try:
            friendship_accepted_notification.full_clean()
            friendship_accepted_notification.save()
            print("Accepted FriendshipRequest Notification created!")
        except ValidationError as e:
            print(e)


@receiver(post_save, sender=PinnedProfilePost)
def pinned_profile_post_notification(sender, instance, created, **kwargs):
    """
    Create a Notification object when someone pins a post to their profile (PinnedProfilePost object created)
    :param sender:
    :param instance: PinnedProfilePost object
    :param created: boolean indicating the creation of a PinnedProfilePost object
    :param kwargs:
    :return:
    """

    if created:

        # follow FK to original ProfilePost author/headline
        original_author = instance.original.author
        original_headline = instance.original.headline

        pinned_post_notification = Notification(
            type=3,
            recipient=original_author,
            sent_from=instance.pinned_by,
            message=f"{instance.pinned_by} pinned your post '{original_headline}' to their profile!",
            reference=instance
        )

        try:
            pinned_post_notification.full_clean()
            pinned_post_notification.save()
            print("ayo")
        except ValidationError as e:
            print(e)


@receiver(post_save, sender=ProfilePost)
def new_profile_post_notification(sender, instance, created, **kwargs):
    """
    Create a Notification object for all friends of user when ProfilePost is published by user
    :param sender:
    :param instance: ProfilePost object
    :param created: boolean indicating the creation of a ProfilePost object
    :param kwargs:
    :return:
    """

    if created:

        # get author of the ProfilePost object
        # author_id = instance.author.id
        # for some reason, with MySQL, only this works: ??
        author_id = instance.author

        # get user friendships
        # return type = <class 'kokoro_app.models.Friendships'> (ManyRelatedManager object)
        friendships, created = Friendships.objects.get_or_create(owner=author_id)

        # convert ManyRelatedManager object into Queryset
        friendships = friendships.friendships.all()

        # create Notification object for each friend
        for friend in friendships:
            new_post_notification = Notification(
                type=4,
                recipient=friend,
                sent_from=instance.author,
                message=f"{instance.author} just published a new post, '{instance.headline}'. Check it out!",
                reference=instance
            )

            try:
                new_post_notification.full_clean()
                new_post_notification.save()
            except Exception as e:
                print(e)
