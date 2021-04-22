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

    def __str__(self):
        """
        :return: string representation of user's 'perfect balance' preferences
        """

        # package activities for admin-panel and template
        perfect_balance = f'{self.perfect_mind}, {self.perfect_body}, {self.perfect_soul}'

        return perfect_balance


class ProfileBio(models.Model):
    """
    A user's biography section on their profile
    """

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    biography = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'biographies'

    def __str__(self):
        """
        :return: string representation of a user's biography
        """

        return self.biography


class ProfileDisplayName(models.Model):
    """
    A user's display name on their profile
    """

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    display_name = models.CharField(max_length=40)

    def __str__(self):
        """
        :return: string representation of a user's display name
        """

        return self.display_name
