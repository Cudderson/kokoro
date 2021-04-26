from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from kokoro_app.models import ProfileImage

print("hello??")
# 'post_save' is a signal that fires after an object is saved
# We want a 'post_save' signal when a user is created
# 'User' model will be the sender
# Our receiver will perform a task once a user is created

# When a user is created, a post_save signal will be sent to receiver
# the receiver is the 'create_profile_image' function
# If a user is created (if created), create a profile image, with the instance
# being the User that was created
@receiver(post_save, sender=User)
def create_profile_image(sender, instance, created, **kwargs):
    if created:
        print("dayum")
        ProfileImage.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile_image(sender, instance, **kwargs):
    print(instance.profileimage)
    instance.profileimage.save()

