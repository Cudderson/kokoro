from django.contrib import admin

# Register your models here.

from .models import Activity, PerfectBalance

admin.site.register(Activity)
admin.site.register(PerfectBalance)
