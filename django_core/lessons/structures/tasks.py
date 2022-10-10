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

    def get_details(self, answer: str) -> dict[str, str]:
        m_variants = {v["id"]: v for v in self.variants}
        if self.check_answer(answer):
            return {'task': self.if_correct, answer: m_variants[answer]['ifCorrect']}

        answer = str(answer)
        if answer not in m_variants:
            return {'task': "Такого варианта нет"}

        return {answer: m_variants[answer]['ifIncorrect'], 'task': self.if_incorrect}


class CheckboxesBlock(TaskBlock):
    type = LessonBlockType.checkboxes

    variants = models.JSONField()
    correct = models.JSONField()

    def check_answer(self, answer: list[str]) -> bool:
        return sorted(answer) == sorted(self.correct)

    def get_details(self, answer: list[str]) -> dict[str, str]:
        m_variants = {v["id"]: v for v in self.variants}
        details = {'task': self.if_correct if self.check_answer(answer) else self.if_incorrect}

        for answer_item in answer:
            if answer_item not in m_variants:
                details[answer_item] = "Такого варианта нет"
                continue

            field = "ifCorrect" if answer_item in self.correct else "ifIncorrect"
            details[answer_item] = m_variants[answer_item][field]

        return details


class SelectsBlock(TaskBlock):
    type = LessonBlockType.selects

    body = models.TextField()
    selects = models.JSONField()
    correct = models.JSONField()

    def check_answer(self, answer):
        return True


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
