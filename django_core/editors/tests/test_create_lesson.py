from django.test import TestCase
from rest_framework.test import APIClient
from lessons.models import Lesson, LessonBlock


def _create_lesson(content):
    # TODO: bonuses validations
    lesson = {
        'name': 't_key1',
        'timeCost': 1,
        'moneyCost': 2,
        'energyCost': 3,
        'bonuses': {1: {'energy': 1, 'money': 2}},
        'content': {
            'blocks': [
                {
                    'type': 100,
                    'next': [1, 2],
                    'content': content
                }
            ],
            'entry': 0,
            'locale': {
                'ru': {
                    't_key1': 'v_key1'
                },
                'en': {
                    't_key1': 'v_key1'
                },
            },
            'markup': {
                'ru': {
                    1: '###ru',
                },
                'en': {
                    1: '###en'
                }
            }
        },
        'next': 0
    }

    return lesson


class TestLessonCreating(TestCase):
    def setUp(self) -> None:
        self.replica_block = {
            'message': 'replica block message 1',
            'location': 1,
            'emotion': 2,
        }
        self.invalid_replica_block = {
            'message': 'replica block message 2',
            'location': 'asd',
            'emotion': 2
        }
        self.lesson = _create_lesson(self.replica_block)
        self.client = APIClient()

    def get_lessons(self):
        return Lesson.objects.all()

    def create_simple_lesson(self):
        self.assertEqual(len(self.get_lessons()), 0)
        response = self.client.post(
            '/api/editors/lessons/',
            self.lesson,
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.get_lessons()), 1)

    def test_creating_and_retrieving_simple_lesson(self):
        self.create_simple_lesson()
        response = self.client.get(
            '/api/editors/lessons/',
            self.lesson,
        )
        body = response.json()[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body['content']['blocks']), 1)
