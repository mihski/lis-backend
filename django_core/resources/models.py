from django.db import models


class EmotionData(models.Model):
    """
        Таблица БД для хранения эмоций персонажа (профиля)
    """
    profile = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE, related_name="emotions")
    lesson = models.ForeignKey("lessons.Lesson", on_delete=models.CASCADE)
    emotion = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now=True)

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
    user = models.OneToOneField("accounts.Profile", on_delete=models.CASCADE, related_name="resources")
    time_amount = models.PositiveIntegerField(default=0)
    money_amount = models.PositiveIntegerField(default=0)
    energy_amount = models.PositiveIntegerField(default=0)

    class Meta:
        app_label = "resources"
        verbose_name = "Resources"
        verbose_name_plural = "Resources"

    def set_energy(self, energy_amount: int) -> None:
        self.energy_amount = max(self.energy_amount, energy_amount)

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name} - {self.user.user.username}"

    def __str__(self) -> str:
        return repr(self)
