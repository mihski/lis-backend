from uuid import uuid4

from django.test import TestCase, Client
from rest_framework.test import APIClient

from accounts.models import User
from lessons.models import Course, Lesson, LessonBlock, Unit
from lessons.structures import LessonBlockType


class TaskCheckingTest(TestCase):
    def setUp(self) -> None:
        self.radio = {
            "variants": ['I', 'you', 'he'],
            "correct": 1,
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
        local_id = str(uuid4())

        response = self.admin_client.patch(
            f'/api/editors/lessons/{self.lesson.id}/',
            json={
                'content': {
                    'blocks': [
                        {
                            'local_id': local_id,
                            'lesson': self.lesson.id,
                            'type': type.value,
                            'content': content,
                            'next': [],
                        }
                    ],
                    'entry': local_id,
                    'locale': {'ru': [], 'en': []},
                    'markup': {'ru': '', 'en': ''}
                }
            },
            format='json'
        )
        print(response.json())

        blocks = response.json()['content']['blocks']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(blocks), 1)

        return blocks[0]

    def test_checking_radio(self):
        unit_data = self.create_unit(LessonBlockType.radios, self.radio)
        response = self.client.patch(
            f'/api/checking/{unit_data["id"]}',
            {'answer': 3}
        )
        print(response.json())
        self.assertEqual(response.status_code, 200)
