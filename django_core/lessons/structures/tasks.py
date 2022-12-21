import random
from abc import abstractmethod
from collections import defaultdict

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

    def shuffle_content(self, content: dict) -> dict:
        return content

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

        has_false = False

        for answer_item in answer:
            if answer_item not in m_variants:
                details[answer_item] = False
                has_false = True
                continue

            details[answer_item] = answer_item in self.correct
            has_false = has_false or (answer_item not in self.correct)

        has_false = has_false or (not self.check_answer(answer))

        if has_false and len(details) <= 5:
            for key in details:
                details[key] = False

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
        return answer.lower() in [v.lower() for v in self.correct['ru']]


class NumberBlock(TaskBlock):
    type = LessonBlockType.number

    tolerance = models.FloatField()
    correct = models.FloatField()

    def check_answer(self, answer):
        dx = self.correct * self.tolerance

        return self.correct - dx <= answer <= self.correct + dx


class RadiosTableBlock(TaskBlock):
    type = LessonBlockType.radiosTable

    columns = models.JSONField()
    rows = models.JSONField()
    is_radio = models.BooleanField()
    correct = models.JSONField()

    def check_answer(self, answer: dict[str, list[str]]) -> bool:
        for row, choose in answer.items():
            if sorted(self.correct[row]) != sorted(choose):
                return False

        return True

    def get_details(self, answer):
        details = defaultdict(lambda: defaultdict(bool))

        for row, choose in answer.items():
            for variant in choose:
                details[row][variant] = variant in self.correct[row]

        return details


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

    def shuffle_content(self, content: dict) -> dict:
        if len(content["options"]) == 1:
            return content["options"]

        random.shuffle(content["options"])

        answer = list(map(lambda x: x["id"], content["options"]))

        if self.check_answer(answer):
            return self.shuffle_content(content)

        return content

    def check_answer(self, answer: list[str]) -> bool:
        return answer == self.correct

    def get_details(self, answer: list[str]) -> list[int]:
        numbers = []

        for i, option_id in enumerate(answer):
            if self.correct[i] == option_id:
                numbers.append(i)

        return numbers


class ComparisonBlock(TaskBlock):
    type = LessonBlockType.comparison

    lists = models.JSONField()
    correct = models.JSONField()

    def check_answer(self, answer: list[tuple[str, str]]) -> bool:
        return len(self.get_details(answer)) == len(self.correct)

    def get_details(self, answer: list[tuple[str, str]]) -> list[int]:
        numbers = []

        m_correct = {
            **{option_1: option_2 for option_1, option_2 in self.correct},
            **{option_2: option_1 for option_1, option_2 in self.correct}
        }

        for i, (option_1, option_2) in enumerate(answer):
            if m_correct[option_1] == option_2:
                numbers.append(i)

        return numbers

    def shuffle_content(self, content: dict) -> dict:
        options_1 = content["lists"][0]
        options_2 = content["lists"][1]

        if len(options_1) == 1 and len(options_2) == 1:
            return content

        random.shuffle(options_1)
        random.shuffle(options_2)

        answer = list(zip(
            list(map(lambda x: x["id"], options_1)),
            list(map(lambda x: x["id"], options_2)),
        ))

        if self.check_answer(answer):
            return self.shuffle_content(content)

        return content
