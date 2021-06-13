from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from kokoro_app.models import ProfileImage, ProfileTimezone, BalanceStreak
import datetime
import pytz


# When a user is created, a post_save signal will be sent to receiver
# the receiver is the 'create_profile_defaults' function
# Default timezone UTC will be saved upon user creation

# create profile defaults when new User is registered
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
