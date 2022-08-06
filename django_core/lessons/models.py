from django.db import models


GENDERS = (
    ('any', 'Любой'),
    ('male', 'Мужской'),
    ('female', 'Женский'),
)


class EditorBlockModel(models.Model):
    block_id = models.IntegerField(default=None, null=True, blank=True)

    class Meta:
        abstract = True


class Course(models.Model):
    name = models.CharField(max_length=127)
    description = models.TextField()

    entry = models.IntegerField(default=-1)
    locale = models.JSONField(default=dict)


class Branching(EditorBlockModel):
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL, related_name='branchings')
    type = models.IntegerField()
    content = models.JSONField()


class Quest(EditorBlockModel):
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL, related_name='quests')

    name = models.CharField(max_length=127)
    description = models.TextField()

    entry = models.IntegerField()
    next = models.IntegerField()


class Laboratory(models.Model):
    name = models.CharField(max_length=127)


class LessonBlock(models.Model):
    locale = models.JSONField(default=dict)
    markup = models.JSONField(default=dict)
    entry = models.IntegerField(default=-1)


class Lesson(EditorBlockModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    quest = models.ForeignKey(Quest, null=True, on_delete=models.SET_NULL, related_name='lessons')
    laboratory = models.ForeignKey(Laboratory, on_delete=models.SET_NULL, null=True)

    name = models.CharField(max_length=127)
    description = models.TextField()
    for_gender = models.CharField(default='any', max_length=6, choices=GENDERS)

    time_cost = models.IntegerField()
    money_cost = models.IntegerField()
    energy_cost = models.IntegerField()

    bonuses = models.JSONField(default=dict)
    content = models.OneToOneField(LessonBlock, related_name='lesson', on_delete=models.CASCADE)


class Unit(EditorBlockModel):
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True)
    lesson_block = models.ForeignKey(LessonBlock, on_delete=models.SET_NULL, null=True, related_name='blocks')
    type = models.IntegerField()
    content = models.JSONField()
    next = models.JSONField()
