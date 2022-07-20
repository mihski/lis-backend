from django.db import models
from django.conf import settings


class EmotionData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    emotion_content = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_created=True)


class Resources(models.Model):
    RESOURCE_TYPE = (
        ('energy', 'Энергия'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPE)
    amount = models.IntegerField(default=0)
