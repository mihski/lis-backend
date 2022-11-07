from typing import Any

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from lessons.models import (
    Lesson,
    Quest,
    Branching,
    ProfileBranchingChoice,
    LessonBlock,
    Course
)
from lessons.exceptions import BranchingAlreadyChosenException
from resources.exceptions import NotEnoughMoneyException

User = get_user_model()


class BranchingTestCase(TestCase):
    API_URL = "/api/lessons/branchings/"

    @classmethod
    def setUpClass(cls):
        super(BranchingTestCase, cls).setUpClass()
        cls.course = Course.objects.create(id=1, name="test")
        cls._create_fixtures()
        cls.user = User.objects.create_user(
            username="test",
            email="test@mail.ru",
            password="test"
        )
        cls.profile = cls.user.profile.get(course_id=cls.course)
        cls.resources = cls.profile.resources

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @classmethod
    def _create_fixtures(cls):
        """
            Создает тестовые данные
        """
        cls.quest = Quest.objects.create(local_id="n_quest", name="n_quest_name")
        block = LessonBlock.objects
        lessons = [
            Lesson(
                local_id="n_001", name="n_001_name", time_cost=0,
                energy_cost=0, money_cost=100, content=block.create(),
                course=cls.course
            ),
            Lesson(
                local_id="n_002", name="n_002_name", time_cost=0,
                energy_cost=0, money_cost=200, content=block.create(),
                course=cls.course
            ),
            Lesson(
                local_id="n_003", name="n_003_name", time_cost=0,
                energy_cost=0, money_cost=300, quest=cls.quest,
                content=block.create(), course=cls.course
            )
        ]
        cls.lessons = Lesson.objects.bulk_create(lessons)
        cls.branching = Branching.objects.create(
            local_id="n_branching",
            type=1,  # profile_parameter <-| BranchingType
            content=dict()
        )

    def _update_money(self, money_amount: int) -> None:
        self.resources.money_amount = money_amount
        self.resources.save()

    def _send_patch_request(self) -> Any:
        return self.client.patch(
            path=self.API_URL + "n_branching/",
            data={"choose_local_id": "n_quest,n_001,n_002"}
        )

    def test_branching_was_selected(self) -> None:
        self._update_money(600)
        response = self._send_patch_request()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile_branching = ProfileBranchingChoice.objects.filter(
            profile=self.profile,
            branching=self.branching
        )
        self.assertTrue(profile_branching.exists())
        self.assertEqual(
            profile_branching.first().choose_local_id,
            "n_quest,n_001,n_002"
        )

    def test_branching_already_chosen_exception(self) -> None:
        self._update_money(600)
        self._send_patch_request()
        response = self._send_patch_request()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_code"], BranchingAlreadyChosenException.default_code)

    def test_not_enough_money_to_select_branching_exception(self) -> None:
        self._update_money(0)
        response = self._send_patch_request()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_code"], NotEnoughMoneyException.default_code)
