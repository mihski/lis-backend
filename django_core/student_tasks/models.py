from django.db import models
from accounts.models import Profile
from rest_framework.validators import ValidationError

from lessons.models import Unit


def validate_is_task(unit: int | Unit) -> Unit:
    if isinstance(unit, int):
        unit = Unit.objects.get(id=unit)

    if not (300 < unit.type < 400):
        raise ValidationError(f"task field should be a task. type({unit.type}) is not a task value")

    return unit


class StudentTaskAnswer(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="tasks_done")
    task = models.ForeignKey('lessons.Unit', on_delete=models.CASCADE, validators=[validate_is_task])

    answer = models.JSONField(default=dict)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"TaskAnswer[{self.id}] {self.profile} - {self.task}"
