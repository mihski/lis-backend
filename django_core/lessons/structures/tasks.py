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
    def get_details(self, answer):
        pass

    class Meta:
        abstract = True


class RadiosBlock(TaskBlock):
    type = LessonBlockType.radios

    variants = models.JSONField()
    correct = models.CharField(max_length=127)

    def check_answer(self, answer: str) -> bool:
        return self.correct == str(answer)

    def get_details(self, answer: str) -> dict[str, bool]:
        m_variants = {v["id"]: v for v in self.variants}
        if self.check_answer(answer):
            return {answer: True}

        answer = str(answer)

        if answer not in m_variants:
            return {answer: False}

        return {answer: False}


class CheckboxesBlock(TaskBlock):
    type = LessonBlockType.checkboxes

    variants = models.JSONField()
    correct = models.JSONField()

    def check_answer(self, answer: list[str]) -> bool:
        return sorted(answer) == sorted(self.correct)

    def get_details(self, answer: list[str]) -> dict[str, bool]:
        m_variants = {v["id"]: v for v in self.variants}
        details = {}

        for answer_item in answer:
            if answer_item not in m_variants:
                details[answer_item] = False
                continue

            details[answer_item] = answer_item in self.correct

        return details


class SelectsBlock(TaskBlock):
    type = LessonBlockType.selects

    body = models.TextField()
    selects = models.JSONField()
    correct = models.JSONField()

    def check_answer(self, answer: dict[str, str]) -> bool:
        for select_id, variant_id in answer.items():
            if self.correct[select_id] != variant_id:
                return False

        return True

    def get_details(self, answer: dict[str, str]) -> dict[str, bool]:
        details = {}

        for select_id, variant_id in answer.items():
            details[select_id] = self.correct[select_id] == variant_id

        return details


class InputBlock(TaskBlock):
    type = LessonBlockType.input

    correct = models.JSONField(default={'ru': [], 'en': []})

    def check_answer(self, answer):
        return answer == self.correct


class NumberBlock(TaskBlock):
    type = LessonBlockType.number

    tolerance = models.FloatField()
    correct = models.FloatField()

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
