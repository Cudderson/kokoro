from django.db import models


# Create your models here.
class MindActivity(models.Model):
    """
    An activity related to the mind
    """

    activity = models.CharField(max_length=100)

    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'mind_activities'

    def __str__(self):
        """
        :return: string representation of model
        """

        return self.activity

