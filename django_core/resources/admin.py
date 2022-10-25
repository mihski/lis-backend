from django.contrib import admin

from resources import models


class EmotionDataAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "created_at")
    ordering = ("-created_at",)


class ResourcesAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "energy_amount", "time_amount", "money_amount")
    list_filter = ("energy_amount", "time_amount", "money_amount")
    ordering = ("-energy_amount", "-time_amount", "-money_amount")
    search_fields = ("user__user__username",)


admin.site.register(models.EmotionData, EmotionDataAdmin)
admin.site.register(models.Resources, ResourcesAdmin)
