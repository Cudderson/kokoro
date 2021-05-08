from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Notification(models.Model):
    """
    Represents a notification for a particular user
    """

    # who the notification is being sent to
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient')

    # who the notification is coming from
    sent_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_from')

    # text describing the notification
    message = models.CharField(max_length=100)

    # the object that the notification is referencing
    reference = models.CharField(max_length=100)

    # describes if the notification has been viewed yet by recipient
    unread = models.BooleanField(default=True)

    def __str__(self):

        return f'Notification for {self.recipient}'
