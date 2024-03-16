from django.db import models
from django.core.validators import URLValidator, MaxValueValidator


class Assignment(models.Model):
    title = models.CharField(max_length=100, verbose_name='название')
    description = models.TextField(verbose_name='описание')
    max_score = models.IntegerField(null=False, blank=False, verbose_name='максимальный балл', validators=[
        MaxValueValidator(10)])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Итоговое задание'
        verbose_name_plural = 'Итоговые задания'


class StudentAssignment(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, verbose_name='задание')
    answer = models.TextField(verbose_name='ответ', validators=[URLValidator()])
    completed_date = models.DateTimeField(null=True, blank=True, auto_now=True, verbose_name='дата выполнения')
    profile = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name='профиль'
    )
    score = models.IntegerField(null=True, blank=True, verbose_name='балл', validators=[
        MaxValueValidator(10)])
    reviewe = models.TextField(null=True, blank=True, verbose_name='отзыв')
    reviewed = models.BooleanField(default=False, verbose_name='проверено')
    accepted = models.BooleanField(default=False, verbose_name='принято')

    def __str__(self):
        return f'{self.profile} - {self.assignment}'

    class Meta:
        unique_together = ('assignment', 'profile')
        verbose_name = 'Студенческое задание'
        verbose_name_plural = 'Студенческие задания'
