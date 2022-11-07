from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from lessons.models import Lesson, Course, LessonBlock, UnitAffect, Quest, Unit
from resources.models import EmotionData

User = get_user_model()


class TestFinishingLesson(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestFinishingLesson, cls).setUpClass()

        cls.course = Course.objects.create(id=1)
        cls.lesson_block = LessonBlock.objects.create()
        cls.lesson = Lesson.objects.create(
            course=cls.course,
            quest=Quest.objects.create(),
            local_id="asd",
            name='lesson 1',
            description='lesson 2',
            for_gender='any',
            time_cost=0,
            money_cost=0,
            energy_cost=0,
            content=cls.lesson_block,
        )
        cls.lesson.profile_affect = UnitAffect.objects.create(code="salary", content={"amount": 2500})
        cls.lesson.save()

        cls.course.entry = cls.lesson.local_id
        cls.course.save()

        cls.user = User.objects.create(username="test", email="test@mail.ru", password="test")
        cls.profile = cls.user.profile.get(course=cls.course)

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_finishing_lesson(self):
        response = self.client.post(
            f"/api/lessons/lessons/{self.lesson.local_id}/finish/",
            {
                "emotion": {
                    "comment": "cool!",
                    "emotion": 1,
                },
                "duration": 2
            },
            format="json"
        )
        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmotionData.objects.count(), 1)
        self.assertEqual(self.profile.statistics.total_time_spend, 2)
        self.assertEqual(self.profile.resources.money_amount, 12500)  # 10000 (init) + 2500 (salary)

    def test_finishing_lesson_statistic(self):
        [Unit.objects.create(type=290 + i, lesson=self.lesson, content={}, next="") for i in range(20)]

        response = self.client.post(
            f"/api/lessons/lessons/{self.lesson.local_id}/finish/",
            {
                "emotion": {
                    "comment": "cool!",
                    "emotion": 1,
                },
                "duration": 2
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()

        statistics = self.profile.statistics

        self.assertEqual(statistics.quests_done, 1)
        self.assertEqual(statistics.lessons_done, 10)
