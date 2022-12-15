from django.contrib import admin

from resources import models


@admin.register(models.EmotionData)
class EmotionDataAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "lesson", "emotion", "created_at")
    list_filter = ("profile", "lesson", "emotion")
    search_fields = ("profile__username", "lesson__local_id")
    ordering = ("-created_at",)


@admin.register(models.Resources)
class ResourcesAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "energy_amount", "time_amount", "money_amount")
    list_filter = ("energy_amount", "time_amount", "money_amount")
    ordering = ("-energy_amount", "-time_amount", "-money_amount")
    search_fields = ("user__username", "user__isu")
