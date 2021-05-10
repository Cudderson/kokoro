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


class BalanceStreak(models.Model):
    """
    A user's streak of the amount of successive days where balance was found
    """

    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    balance_streak = models.PositiveSmallIntegerField(default=0)

    date_last_incremented = models.DateTimeField()

    expiration_date = models.DateTimeField()

    def __str__(self):
        """
        :return: string representation of the user's current balance streak
        """

        # convert int to string
        return str(self.balance_streak)


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
        perfect_balance = f'{self.perfect_mind},,, {self.perfect_body},,, {self.perfect_soul}'

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


class ProfileQuote(models.Model):
    """
    A user's displayed quote & author on their profile
    """

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    quote = models.CharField(max_length=180)

    quote_author = models.CharField(max_length=40)

    def __str__(self):
        """
        :return: string representation of user's quote & author
        """

        # 3-comma separator for reliable string-splitting (do for perfect too)
        return f'{self.quote},,, {self.quote_author}'


class ProfileImage(models.Model):
    """
    A user's photo/avi on their profile
    """

    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    image = models.ImageField(default='default.jpg', upload_to='profile_images')

    def __str__(self):

        return f"{self.owner}'s Profile Image"


class ProfileTimezone(models.Model):
    """
    A string of a user's timezone
    """

    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    user_timezone = models.CharField(default='UTC', max_length=50)

    def __str__(self):

        return self.user_timezone


class ContactInfo(models.Model):
    """
    A user's contact information (email/social media)
    """

    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    user_email = models.EmailField(null=True)

    def __str__(self):

        return f'{self.user_email}'


class ProfilePost(models.Model):
    """
    A Profile Post/Blog for a user's profile
    """

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    date_published = models.DateTimeField(auto_now_add=True)

    headline = models.CharField(max_length=80)

    content = models.TextField()

    post_slug = models.SlugField(max_length=80, unique=True)

    class Meta:
        ordering = ['-date_published']

    def __str__(self):

        return self.headline


class PinnedProfilePost(models.Model):
    """
    A Profile Post/Blog for a user's profile that belongs to another user
    """

    # using this method, A pinned post is indeed deleted when OG is deleted

    original = models.ForeignKey(ProfilePost, on_delete=models.CASCADE)

    pinned_by = models.ForeignKey(User, on_delete=models.CASCADE)

    date_published = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f'Original: {self.original} Pinned By: {self.pinned_by}'


class Friendships(models.Model):
    """
    Represents a User's friendship with other Users
    """

    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner')

    friendships = models.ManyToManyField(User, blank=True)

    class Meta:
        verbose_name_plural = 'Friendships'

    def __str__(self):
        return f'{self.owner}'


class FriendshipRequest(models.Model):
    """
    Represents a friendship request between two users
    """

    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)

    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)

    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'Pending Request from {self.from_user} to {self.to_user}'
