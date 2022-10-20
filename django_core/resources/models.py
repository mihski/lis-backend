from django.db import models

from accounts.models import Profile


class EmotionData(models.Model):
    """
        Таблица БД для хранения эмоций персонажа (профиля)
    """
    user =  models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="emotions")
    emotion_content = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_created=True)

    class Meta:
        app_label = "resources"
        verbose_name = "EmotionData"
        verbose_name_plural = "EmotionsData"

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name} - {self.user.user.username}"

    def __str__(self) -> str:
        return repr(self)


class Resources(models.Model):
    """
        Таблица БД для хранения ресурсов персонажа (профиля)
    """
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="resources")
    time_amount = models.PositiveIntegerField(default=0)
    money_amount = models.PositiveIntegerField(default=0)
    energy_amount = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = "resources"
        verbose_name = "Resources"
        verbose_name_plural = "Resources"

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name} - {self.user.user.username}"

    def __str__(self) -> str:
        return repr(self)
