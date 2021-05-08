from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from kokoro_app.models import ProfileImage, ProfileTimezone, BalanceStreak
import datetime
import pytz

# 'post_save' is a signal that fires after an object is saved
# We want a 'post_save' signal when a user is created
# 'User' model will be the sender

# When a user is created, a post_save signal will be sent to receiver
# the receiver is the 'create_profile_image' function
# If a user is created (if created), create a profile image, with the instance
# being the User that was created (ProfileImage has a default image)
# Default timezone UTC will be saved upon user creation

# User should also get an initial balance streak of 0 when created


@receiver(post_save, sender=User)
def create_profile_defaults(sender, instance, created, **kwargs):
    if created:
        ProfileImage.objects.create(owner=instance)
        ProfileTimezone.objects.create(owner=instance)
        # set an initial expiration date of now, date_last_incremented to 2 days ago to allow streak incrementation on day 1
        BalanceStreak.objects.create(owner=instance,
                                     date_last_incremented=datetime.datetime.now(tz=pytz.timezone('UTC')) - datetime.timedelta(days=2),
                                     expiration_date=datetime.datetime.now(tz=pytz.timezone('UTC')))
        instance.profileimage.save()
        instance.profiletimezone.save()
        instance.balancestreak.save()
