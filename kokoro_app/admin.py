from django.contrib import admin

# Register your models here.

from .models import Activity, PerfectBalance, ProfileBio, ProfileDisplayName, ProfileQuote, \
                    ProfileImage, ProfileTimezone, BalanceStreak, ContactInfo, ProfilePost, PinnedProfilePost,\
                    FriendshipRequest, Friendships, SupportReport

admin.site.register(Activity)
admin.site.register(PerfectBalance)
admin.site.register(ProfileBio)
admin.site.register(ProfileDisplayName)
admin.site.register(ProfileQuote)
admin.site.register(ProfileImage)
admin.site.register(ProfileTimezone)
admin.site.register(BalanceStreak)
admin.site.register(ContactInfo)
admin.site.register(PinnedProfilePost)
admin.site.register(Friendships)
admin.site.register(FriendshipRequest)
admin.site.register(SupportReport)


class ProfilePostAdmin(admin.ModelAdmin):
    """
    Custom Admin-Panel display for Profile Posts
    """

    list_display = ('headline', 'author', 'post_slug', 'date_published')

    search_fields = ['author', 'headline', 'content']

    # automatically creates slug based off post headline
    prepopulated_fields = {'post_slug': ('headline',)}


admin.site.register(ProfilePost, ProfilePostAdmin)
