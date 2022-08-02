from django.db import models


GENDERS = (
    ('male', 'Мужской'),
    ('female', 'Женский'),
)


class Course(models.Model):
    name = models.CharField(max_length=127)
    description = models.TextField()


class Branching(models.Model):
    BRANCH_TYPES = (
        ('conditional', 'Условный бранчинг'),
        ('selective', 'Выборочный бранчинг'),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    branch_type = models.CharField(max_length=32, choices=BRANCH_TYPES)
    type = models.IntegerField()
    content = models.JSONField()


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

    time_cost = models.IntegerField()
    money_cost = models.IntegerField()
    energy_cost = models.IntegerField()

    bonuses = models.ForeignKey('resources.Bonuses', on_delete=models.CASCADE)


class LessonBlock(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    name = models.CharField(max_length=127)
    description = models.TextField()
    markup = models.TextField()

    entry = models.ForeignKey('lessons.Unit', on_delete=models.SET_NULL, null=True)
    next = models.ForeignKey('lessons.Unit', on_delete=models.SET_NULL, null=True, blank=True)


class UnitType(models.Model):
    name = models.CharField(max_length=60, unique=True)


class Unit(models.Model):
    question_type = models.ForeignKey(UnitType, on_delete=models.SET_NULL, null=True)
    lesson_block = models.ForeignKey(LessonBlock, on_delete=models.CASCADE)

    name = models.CharField(max_length=127)
    content = models.JSONField(default=dict)

    next = models.ManyToManyField('self', on_delete=models.SET_NULL, null=True, blank=True)
