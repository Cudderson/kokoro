# signals for sending(creating) notifications

from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver

from kokoro_app.models import FriendshipRequest, PinnedProfilePost
from .models import Notification

from django.core.signals import request_finished

from django.core.exceptions import ValidationError

# django.db.models.signals.m2m_changed
# Sent when a ManyToManyField on a model is changed.

# Use this  to test signals if not working
# @receiver(request_finished)
# def test_signal(sender, **kwargs):
#     print("Your signal is working.")


# we want to trigger a signal when certain events happen
# Let's start with one, when a FriendshipRequest object is created

# This signal is being called twice.. *NEED TO FIX*
@receiver(post_save, sender=FriendshipRequest, dispatch_uid="my_unique_identifier")
def create_friendship_request_notification(sender, instance, created, **kwargs):
    """
    Create a Notification when a FriendshipRequest object is created
    :param sender:
    :param instance:
    :param created:
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
    :param instance:
    :param created:
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


# What else needs a notification?
# FriendshipRequest creation [x]
# Friendship Request acceptance [x]
# When someone pins your post [x]

# I like this start so far.
# Before building out all notifications, we should now work on the template (base.html) and incorporate notifications there
