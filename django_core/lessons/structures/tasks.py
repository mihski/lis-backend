from abc import abstractmethod
from django.db import models
from lessons.structures import LessonBlockType
from helpers.mixins import ChildAccessMixin


class TaskBlock(models.Model, ChildAccessMixin):
    title = models.CharField(max_length=127)
    description = models.TextField()
    if_correct = models.CharField(max_length=1023)
    if_incorrect = models.CharField(max_length=1023)

    @abstractmethod
    def check_answer(self, answer):
        pass

    @abstractmethod
    def answer_details(self, answer):
        pass

    class Meta:
        abstract = True


class RadiosBlock(TaskBlock):
    type = LessonBlockType.radios

    variants = models.JSONField()
    correct = models.IntegerField()

    def check_answer(self, answer):
        return self.correct == answer


class CheckboxesBlock(TaskBlock):
    type = LessonBlockType.checkboxes

    variants = models.JSONField()
    correct = models.JSONField()

    def check_answer(self, answer):
        return sorted(answer) == sorted(self.correct)


class SelectsBlock(TaskBlock):
    type = LessonBlockType.selects

    body = models.TextField()
    selects = models.JSONField()
    correct = models.JSONField()

    def check_answer(self, answer):
        return True


class InputBlock(TaskBlock):
    type = LessonBlockType.input

    correct = models.JSONField()

    def check_answer(self, answer):
        return answer == self.correct


class NumberBlock(TaskBlock):
    type = LessonBlockType.number

    tolerance = models.IntegerField()
    correct = models.IntegerField()

    def check_answer(self, answer):
        dx = self.correct * self.tolerance / 100

        return self.correct - dx <= answer <= self.correct + dx


class RadiosTableBlock(TaskBlock):
    type = LessonBlockType.radiosTable

    columns = models.JSONField()
    rows = models.JSONField()
    is_radio = models.BooleanField()
    correct = models.JSONField()

    def check_answer(self, answer):
        return True


class ImageAnchorsBlock(TaskBlock):
    type = LessonBlockType.imageAnchors

    anchors = models.JSONField()
    options = models.JSONField()
    img_url = models.CharField(max_length=1027)
    correct = models.JSONField()

    def check_answer(self, answer):
        return True


class SortBlock(TaskBlock):
    type = LessonBlockType.sort

    options = models.JSONField()
    correct = models.JSONField()

    def check_answer(self, answer):
        return answer == self.correct


class ComparisonBlock(TaskBlock):
    type = LessonBlockType.comparison

    lists = models.JSONField()
    correct = models.JSONField()

    def check_answer(self, answer):
        return True
