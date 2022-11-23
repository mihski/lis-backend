from collections import defaultdict
from typing import Any

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from accounts.serializers import ProfileStatisticsSerializer
from lessons.exceptions import BlockEntityIsUnavailableException
from lessons.models import (
    Lesson,
    Course,
    LessonBlock,
    UnitAffect,
    Quest,
    ProfileLessonDone,
    Branching
)
from resources.models import EmotionData

User = get_user_model()


class TestFinishingLesson(TestCase):
    API_URL = "/api/lessons/lessons/"

    @classmethod
    def setUpClass(cls):
        super(TestFinishingLesson, cls).setUpClass()

        cls.course = Course.objects.create()
        cls.quest = Quest.objects.create(local_id="q_000", entry="l_001")

        cls._create_lessons_chain()
        cls.lesson = cls.lessons[0]
        cls.lesson.profile_affect = UnitAffect.objects.create(code="salary", content={"amount": 2500})
        cls.lesson.save()

        cls.course.entry = cls.lesson.local_id
        cls.course.save()

        cls.user = User.objects.create(username="test", email="test@mail.ru", password="test")
        cls.profile = cls.user.profile.get(course=cls.course)

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def tearDown(self) -> None:
        ProfileLessonDone.objects.all().delete()

    @classmethod
    def create_lesson(cls, lesson_id: int, quest: Quest) -> Lesson:
        return Lesson(
            course=cls.course, quest=quest,
            local_id=f"l_00{lesson_id}", name=f"l_00{lesson_id}_name",
            description="fixture", for_gender="any",
            time_cost=0, money_cost=0,
            energy_cost=0, next=f"l_00{lesson_id + 1}",
            content=LessonBlock.objects.create(
                locale={
                    "ru": dict(), "en": dict()
                }
            )
        )

    @classmethod
    def _create_lessons_chain(cls) -> None:
        """
            Создает цепочку уроков: l_000 -> l_003
            в рамках одного квеста (cls.quest)
        """
        lessons: list[Lesson] = []
        for i in range(4):
            lessons.append(cls.create_lesson(i, cls.quest))

        lessons[-1].next = ""
        cls.lessons = Lesson.objects.bulk_create(lessons)

        # Работа с локалями
        locales_en = defaultdict()
        locales_ru = defaultdict()
        locales = {
            "en": locales_en,
            "ru": locales_ru
        }

        for lesson in lessons:
            update_dict = {"{}".format(lesson.name): "Test"}
            locales_ru.update(update_dict)
            locales_en.update(update_dict)

        # Обновляем локали
        cls.course.locale = locales
        cls.course.save()

    def _finish_lesson(self, lesson) -> Any:
        return self.client.post(
            self.API_URL + f"{lesson.local_id}/finish/",
            {
                "emotion": {
                    "comment": "cool!",
                    "emotion": 1,
                },
                "duration": 2
            },
            format="json"
        )

    def test_finishing_lesson(self):
        response = self._finish_lesson(self.lesson)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmotionData.objects.count(), 1)
        self.assertEqual(self.profile.statistics.total_time_spend, 2)
        self.assertEqual(ProfileLessonDone.objects.filter(profile=self.profile).count(), 1)
        self.assertEqual(self.profile.resources.money_amount, 12500)  # 10000 (init) + 2500 (salary)

    def test_has_access_to_lesson(self) -> None:
        """ Первый урок всегда доступен """
        response = self.client.get(
            self.API_URL + self.lesson.local_id + "/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_to_forbidden_lesson_raises_exception(self) -> None:
        """ Первый урок не пройден -> второй не доступен """
        response = self.client.get(
            self.API_URL + self.lessons[1].local_id + "/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_code"], BlockEntityIsUnavailableException.default_code)

    def test_access_to_lesson_after_previous_finished(self) -> None:
        """
            Второй урок станет доступен, когда первый пройден
        """
        response = self.client.get(
            self.API_URL + self.lessons[1].local_id + "/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self._finish_lesson(self.lesson)

        response = self.client.get(
            self.API_URL + self.lessons[1].local_id + "/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_finish_if_no_access(self) -> None:
        response = self._finish_lesson(self.lessons[-1])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_code"], BlockEntityIsUnavailableException.default_code)

    def test_quest_accessible_after_previous_completed(self) -> None:
        new_quest = Quest.objects.create(local_id="q_002", entry="l_004")
        self.quest.next = "q_002"
        self.quest.save()

        new_lesson = self.create_lesson(4, new_quest)
        new_lesson.next = ""
        new_lesson.save()

        response = self.client.get(self.API_URL + new_lesson.local_id + "/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Завершение квеста
        for lesson in self.lessons:
            self._finish_lesson(lesson)

        response = self._finish_lesson(new_lesson)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
