from django.test import TestCase
from rest_framework.test import APIClient
from lessons.models import Lesson, Unit
from lessons.structures.lectures import ReplicaBlock
from editors.serializers import LessonBlockType
from editors.models import Block


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
            'blocks': [unit],
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


def _create_quests(lessons_ids):
    return {
        'lessons': lessons_ids,
        'description': 'quest 1',
        'entry': 0,
        'next': 0,
    }


class TestLessonCreating(TestCase):
    def setUp(self) -> None:
        self.replica_block = {
            'message': 'replica block message 1',
            'location': 1,
            'emotion': 2,
        }
        self.replica_unit = _create_unit(self.replica_block, LessonBlockType.replica)
        self.replica_unit_with_coords = self.replica_unit | {
            'x': 21.2,
            'y': 54.4
        }
        self.client = APIClient()

    def get_lessons(self):
        return Lesson.objects.all()

    def get_units(self):
        return Unit.objects.all()

    def create_replica_unit(self):
        blocks_count = Block.objects.all().count()

        response = self.client.post(
            '/api/editors/units/',
            self.replica_unit_with_coords,
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            Block.objects.all().count(),
            blocks_count + 1
        )

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
        unit_data = self.create_replica_unit()
        lesson = _create_simple_lesson(unit_data)

        response = self.client.post(
            '/api/editors/lessons/',
            lesson,
            format='json'
        )
        self.assertEqual(response.status_code, 201)

        return response.json()

    def test_creating_and_retrieving_simple_lesson(self):
        self.assertEqual(len(self.get_lessons()), 0)

        lesson_data = self.create_simple_lesson()

        response = self.client.get(f'/api/editors/lessons/{lesson_data["id"]}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], lesson_data['id'])
        self.assertEqual(len(response.json()['content']['blocks']), 1)
        self.assertEqual(len(self.get_units()), 1)

    def test_patching_lesson(self):
        lesson_data = self.create_simple_lesson()
        lesson_data['content']['blocks'][0]['next'] = [1]
        lesson_data['timeCost'] = 3
        lesson_data['content']['blocks'][0]['content']['emotion'] = 3

        response = self.client.patch(
            f'/api/editors/lessons/{lesson_data["id"]}/',
            lesson_data,
            format='json'
        )
        new_lesson_data = response.json()
        self.assertEqual(response.status_code, 200)

        # check that we didn't change ids
        self.assertEqual(lesson_data['id'], new_lesson_data['id'])
        self.assertEqual(
            new_lesson_data['content']['id'],
            lesson_data['content']['id'],
        )
        self.assertEqual(
            sorted([b['id'] for b in new_lesson_data['content']['blocks']]),
            sorted([b['id'] for b in lesson_data['content']['blocks']]),
        )
        self.assertTrue(all(
            nb['content']['id'] == b['content']['id']
            for nb, b in zip(
                sorted(lesson_data['content']['blocks'], key=lambda x: x['id']),
                sorted(new_lesson_data['content']['blocks'], key=lambda x: x['id']),
            )
        ))

        # check we changed exact properties
        self.assertEqual(
            new_lesson_data['content']['blocks'][0].pop('next'),
            [1]
        )
        self.assertEqual(
            new_lesson_data.pop('timeCost'),
            3,
        )
        self.assertEqual(
            new_lesson_data['content']['blocks'][0]['content'].pop('emotion'),
            3,
        )
        lesson_data['content']['blocks'][0].pop('next')
        lesson_data.pop('timeCost')
        lesson_data['content']['blocks'][0]['content'].pop('emotion')

        self.assertEqual(new_lesson_data, lesson_data)

    def create_simple_quest(self, lesson_ids):
        response = self.client.post(
            '/api/editors/quests/',
            _create_quests(lesson_ids),
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_patching_quest(self):
        quest = self.create_simple_quest([])
        quest['lessons'] = [1, 2]

        response = self.client.patch(
            f'/api/editors/quests/{quest["id"]}/',
            quest,
            format='json'
        )
        new_quest = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(new_quest['lessons'], [1, 2])
