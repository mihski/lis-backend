from email.policy import default
from django.db import models



GENDERS = (
    ('male', 'Мужской'),
    ('female', 'Женский'),
)

class Course(models.Model):
    name = models.CharField(max_length=127)
    description = models.TextField()


class Quest(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=127)
    description = models.TextField()


class Laboratory(models.Model):
    name = models.CharField(max_length=127)


class Lesson(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.SET_NULL, null=True)

    name = models.CharField(max_length=127)
    description = models.TextField()
    for_gender = models.CharField(max_length=6, choices=GENDERS)
    # TODO: подумать как разбить на разные подвиды ресурсов
    resources_amount = models.IntegerField()


class LessonBlock(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    name = models.CharField(max_length=127)
    description = models.TextField()


class QuestionType(models.Model):
    name = models.CharField(max_length=60, unique=True)


class Question(models.Model):
    question_type = models.ForeignKey(QuestionType, on_delete=models.SET_NULL, null=True)
    lesson_block = models.ForeignKey(LessonBlock, on_delete=models.CASCADE)
    name = models.CharField(max_length=127)
    question_content = models.JSONField(default=dict)
