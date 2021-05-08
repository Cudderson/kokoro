# signals for sending(creating) notifications

from django.db.models.signals import post_save, post_delete, m2m_changed
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
            unread=True,
        )

        try:
            friendship_request_notification.full_clean()
            print("CLEAN")
            friendship_request_notification.save()
        except ValidationError as e:
            print(e)
            pass


@receiver(m2m_changed, sender=FriendshipRequest)
def accept_friendship_request_notification(sender, instance):
    # FriendshipRequest objects are deleted when:
    # user cancels request
    # recipient accepts or denies

    # we only want a notification on a friendship request acceptance.
    # could add field 'accepted' to FriendshipRequest, and when it's accepted, the value==True.
    # then this post/pre_delete signal could trigger
    # if accepted == True, then create the notification

    # alternatively, I could send a signal when a User's Friendships model adds a user to the MTM field
    # this seems better

    # thirdly, I could manually call a create_noti() function in the code where a friendship_request is accepted.
    # but this would require importing the Notification model, maybe not a big deal



# this first one seems to be working great.
# I'm afraid of hidden circular dependancy issues, though. I want to get a few more done before committing.
# What else needs a notification?
# FriendshipRequest creation [x]
# Friendship Request acceptance []


