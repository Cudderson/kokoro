# signals for sending(creating) notifications

from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver

from kokoro_app.models import FriendshipRequest
from .models import Notification

from django.core.signals import request_finished

from django.core.exceptions import ValidationError

# django.db.models.signals.m2m_changed
# Sent when a ManyToManyField on a model is changed.


@receiver(request_finished)
def test_signal(sender, **kwargs):
    print("Your signal is working.")


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
            pass


@receiver(pre_delete, sender=FriendshipRequest)
def accept_friendship_request_notification(sender, instance, **kwargs):

    # FriendshipRequest.accepted == True when accepted, before deletion
    if instance.accepted:

        friendship_accepted_notification = Notification(
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
            pass


# What else needs a notification?
# FriendshipRequest creation [x]
# Friendship Request acceptance [x]
# When someone pins your post []
