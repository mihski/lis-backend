from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User, Profile, Statistics
from lessons.models import Lesson, Course, LessonBlock
from resources.models import EmotionData, Resources


class TestFinishingLesson(TestCase):
    def setUp(self) -> None:
        self.course = Course.objects.create()
        self.lesson_block = LessonBlock.objects.create()
        self.lesson = Lesson.objects.create(
            course=self.course,
            local_id="asd",
            name='lesson 1',
            description='lesson 2',
            for_gender='any',
            time_cost=0,
            money_cost=0,
            energy_cost=0,
            content=self.lesson_block,
        )
        self.course.entry = self.lesson.local_id
        self.course.save()

        self.user = User.objects.create(username="test", email="test@mail.ru", password="test")
        self.profile = Profile.objects.create(user=self.user)
        self.resources = Resources.objects.create(user=self.profile)
        self.client = APIClient()
        self.client.force_login(self.user)

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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmotionData.objects.count(), 1)
        self.assertEqual(Statistics.objects.get(profile=self.profile).total_time_spend, 2)
