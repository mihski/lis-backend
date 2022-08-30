from django.db import models
from django.conf import settings


class StudentTaskAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey('lessons.Unit', on_delete=models.CASCADE)

    answer = models.JSONField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"TaskAnswer[{self.id}] {self.user} {self.task}"
