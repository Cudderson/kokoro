from django.contrib import admin

# Register your models here.

from .models import Activity, PerfectBalance, ProfileBio, ProfileDisplayName, ProfileQuote

admin.site.register(Activity)
admin.site.register(PerfectBalance)
admin.site.register(ProfileBio)
admin.site.register(ProfileDisplayName)
admin.site.register(ProfileQuote)
