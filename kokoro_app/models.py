from django.db import models


# Create your models here.
class Activity(models.Model):
    """
    An activity related to the mind, body, or soul
    """

    ACTIVITY_TYPES = (
        ('mind', 'Mind'),
        ('body', 'Body'),
        ('soul', 'Soul'),
    )

    activity = models.CharField(max_length=4, choices=ACTIVITY_TYPES)

    description = models.CharField(max_length=100)

    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'activities'

    def __str__(self):
        """
        :return: string representation of model
        """

        return self.description
