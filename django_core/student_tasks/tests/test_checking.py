from uuid import uuid4
from django.test import TestCase, Client
from rest_framework.test import APIClient

from accounts.models import User
from lessons.models import Course, Lesson, LessonBlock
from lessons.structures import LessonBlockType
from editors.serializers import UnitSerializer


class TaskCheckingTest(TestCase):
    def setUp(self) -> None:
        self.task_default = {
            'title': 'Title',
            'description': '',
            'ifCorrect': 'Супер!',
            'ifIncorrect': 'Попробуйте снова.'
        }
        self.radio = {
            "variants": [{
                "id": "1",
                "variant": 'I',
                "ifCorrect": "Верно",
                "ifIncorrect": "Не верно",
            }, {
                "id": "2",
                "variant": 'II',
                "ifCorrect": "Верно 2",
                "ifIncorrect": "Не верно 2",
            }
            ],
            "correct": ["1"],
        }
        self.course = Course.objects.create()
        self.lesson_block = LessonBlock.objects.create()
        self.lesson = Lesson.objects.create(
            course=self.course,
            name='lesson 1',
            description='lesson 2',
            for_gender='any',
            time_cost=0,
            money_cost=0,
            energy_cost=0,
            content=self.lesson_block,
        )

        self.admin_user = User.objects.create_superuser('admin', 'admin@mail.ru', 'admin')
        self.user = User.objects.create_user('test', 'test@mail.ru', 'test')

        self.admin_client = Client()
        self.admin_client.login(username='admin', password='admin')

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def create_unit(self, type: LessonBlockType, content):
        unit = UnitSerializer(data=dict(
            local_id=uuid4().hex,
            lesson=self.lesson.id,
            type=type.value,
            next=[],
            content={**self.task_default, **content},
        ))
        unit.is_valid()

        return unit.save()

    def test_checking_radio(self):
        unit = self.create_unit(LessonBlockType.checkboxes, self.radio)
        response = self.client.patch(
            f'/api/tasks/answers/{unit.local_id}/',
            {"answer": ["1", "2"]},
        )
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['is_correct'], True)

        response = self.client.patch(
            f'/api/tasks/answers/{unit.local_id}/',
            {"answer": ["1", "2"]},
        )
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['is_correct'], False)
