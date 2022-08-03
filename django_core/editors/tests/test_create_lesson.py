from django.test import TestCase
from rest_framework.test import APIClient
from lessons.models import Lesson, Unit
from lessons.structures.lectures import ReplicaBlock
from editors.serializers import LessonBlockType


def _create_unit(content, lesson_type: LessonBlockType):
    return {
        'type': lesson_type.value,
        'next': [1, 2],
        'content': content
    }


def _create_simple_lesson(unit):
    # TODO: bonuses validations
    lesson = {
        'name': 't_key1',
        'timeCost': 1,
        'moneyCost': 2,
        'energyCost': 3,
        'bonuses': {1: {'energy': 1, 'money': 2}},
        'content': {
            'blocks': [
                unit
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
        self.replica_unit = _create_unit(self.replica_block, LessonBlockType.replica)
        self.lesson = _create_simple_lesson(self.replica_unit)
        self.client = APIClient()

    def get_lessons(self):
        return Lesson.objects.all()

    def get_units(self):
        return Unit.objects.all()

    def create_replica_unit(self):
        response = self.client.post(
            '/api/editors/units/',
            self.replica_unit,
            format='json'
        )
        self.assertEqual(response.status_code, 201)

        return response.json()

    def test_creating_and_retrieving_replica_unit(self):
        unit_data = self.create_replica_unit()

        response = self.client.get(f'/api/editors/units/{unit_data["id"]}/')
        self.assertEqual(response.status_code, 200)

        replica_blocks = ReplicaBlock.objects.all()
        self.assertEqual(len(self.get_units()), 1)
        self.assertEqual(len(replica_blocks), 1)
        self.assertEqual(
            response.json()['content']['id'],
            replica_blocks[0].id
        )

    def create_simple_lesson(self):
        response = self.client.post(
            '/api/editors/lessons/',
            self.lesson,
            format='json'
        )
        self.assertEqual(response.status_code, 201)

        return response.json()

    def test_creating_and_retrieving_simple_lesson(self):
        self.assertEqual(len(self.get_lessons()), 0)

        lesson_data = self.create_simple_lesson()

        response = self.client.get(
            f'/api/editors/lessons/{lesson_data["id"]}/',
            self.lesson,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], lesson_data['id'])
        self.assertEqual(len(response.json()['content']['blocks']), 1)
