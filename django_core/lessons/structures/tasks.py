from django.db import models


class TaskBlock(models.Model):
    title = models.CharField(max_length=127)
    description = models.TextField()
    if_correct = models.CharField(max_length=1023)
    if_incorrect = models.CharField(max_length=1023)

    class Meta:
        abstract = True


class RadiosBlock(TaskBlock):
    variants = models.JSONField()
    correct = models.IntegerField()


class CheckboxesBlock(TaskBlock):
    variants = models.JSONField()
    correct = models.JSONField()


class SelectsBlock(TaskBlock):
    body = models.TextField()
    selects = models.JSONField()
    correct = models.JSONField()


class InputBlock(TaskBlock):
    correct = models.JSONField()


class NumberBlock(TaskBlock):
    tolerance = models.IntegerField()
    correct = models.IntegerField()


class RadiosTableBlock(TaskBlock):
    columns = models.JSONField()
    rows = models.JSONField()
    is_radio = models.BooleanField()
    correct = models.JSONField()


class ImageAnchorsBlock(TaskBlock):
    anchors = models.JSONField()
    options = models.JSONField()
    img_url = models.CharField(max_length=1027)
    correct = models.JSONField()


class SortBlock(TaskBlock):
    options = models.JSONField()
    correct = models.JSONField()


class ComparisonBlock(TaskBlock):
    lists = models.JSONField()
    correct = models.JSONField()
