from django.db import models
from django.contrib.auth.models import User


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

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    activity = models.CharField(max_length=4, choices=ACTIVITY_TYPES)

    description = models.CharField(max_length=100)

    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'activities'

    def __str__(self):
        """
        :return: string representation of model
        """

        return self.activity.title() + ": " + self.description.title()


class PerfectBalance(models.Model):
    """
    A user's 'perfect balance' section on profile page
    """

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # a user's favorite mind, body, and soul activities
    perfect_mind = models.CharField(max_length=100)
    perfect_body = models.CharField(max_length=100)
    perfect_soul = models.CharField(max_length=100)

    # package preferences for admin-panel (will need to parse-string for template)
    perfect_balance = f'M:{perfect_mind}, B:{perfect_body}, S:{perfect_soul}'

    def __str__(self):
        """
        :return: string representation of user's 'perfect balance' preferences
        """

        return self.perfect_balance
