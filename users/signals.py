from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from kokoro_app.models import ProfileImage, ProfileTimezone, BalanceStreak

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
        BalanceStreak.objects.create(owner=instance)


@receiver(post_save, sender=User)
def save_profile_defaults(sender, instance, **kwargs):
    instance.profileimage.save()
    instance.profiletimezone.save()
    instance.balancestreak.save()
