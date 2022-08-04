from django.db import models


GENDERS = (
    ('male', 'Мужской'),
    ('female', 'Женский'),
)


class Course(models.Model):
    name = models.CharField(max_length=127)
    description = models.TextField()


class Branching(models.Model):
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL)
    type = models.IntegerField()
    content = models.JSONField()


class Quest(models.Model):
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL, related_name='quests')

    lessons = models.JSONField()
    name = models.CharField(max_length=127)
    description = models.TextField()

    entry = models.IntegerField()
    next = models.IntegerField()


class Laboratory(models.Model):
    name = models.CharField(max_length=127)


class LessonBlock(models.Model):
    locale = models.JSONField()
    markup = models.JSONField()

    entry = models.IntegerField()


class Lesson(models.Model):
    quest = models.ForeignKey(Quest, null=True, on_delete=models.SET_NULL)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.SET_NULL, null=True)

    name = models.CharField(max_length=127)
    description = models.TextField()
    for_gender = models.CharField(max_length=6, choices=GENDERS)

    time_cost = models.IntegerField()
    money_cost = models.IntegerField()
    energy_cost = models.IntegerField()

    bonuses = models.JSONField()
    content = models.OneToOneField(LessonBlock, related_name='lesson', null=True, on_delete=models.CASCADE)


class Unit(models.Model):
    lesson_block = models.ForeignKey(
        LessonBlock,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blocks'
    )

    type = models.IntegerField()
    content = models.JSONField()
    next = models.JSONField()
