from django.db import models
from django.conf import settings


class EmotionData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    emotion_content = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_created=True)


class Resources(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_amount = models.PositiveIntegerField(default=0)
    money_amount = models.PositiveIntegerField(default=0)
    energy_amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Resource - {self.user.username}"
