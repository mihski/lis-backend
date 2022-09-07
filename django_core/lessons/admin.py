from django.contrib import admin

from lessons import models


admin.site.register(models.Course)
admin.site.register(models.NPC)
admin.site.register(models.Location)
