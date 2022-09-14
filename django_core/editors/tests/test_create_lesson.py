from uuid import uuid4

from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User
from lessons.models import Lesson, Unit, Course, Quest, Branching
from lessons.structures.lectures import ReplicaBlock
from editors.serializers import LessonBlockType, LessonBlock
from editors.models import Block


def _create_unit(lesson_id, content, lesson_type: LessonBlockType):
    return {
        'local_id': 'asdasd',
        'lesson': lesson_id,
        'type': lesson_type.value,
        'next': [1, 2],
        'content': content
    }


def _create_simple_lesson(course_id, units=None, local_id='lesson_1'):
    # TODO: bonuses validations
    content = {}

    if units:
        content = {
            'blocks': units,
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
        }

    lesson = {
        'local_id': local_id,
        'name': 't_key1',
        'course': course_id,
        'timeCost': 1,
        'moneyCost': 2,
        'energyCost': 3,
        'bonuses': {1: {'energy': 1, 'money': 2}},
        'next': 0,
        'x': 10,
        'y': 20,
    }

    return lesson | content


def _create_quests(course_id, lessons, branchings = [], local_id=None):
    return {
        'name': 'Quest',
        'local_id': local_id or str(uuid4()),
        'course': course_id,
        'description': 'quest 1',
        'lessons': lessons,
        'branchings': branchings,
        'next': 0,
    }


def _create_course():
    return {
        'name': 'course 1',
        'description': 'course description 1',
    }


def _create_conditional_branching():
    return {
        '1': '123',
        '2': '321',
    }


def _create_selective_branching():
    return {
        'min': 2,
        'list': ['123', '321']
    }


def _create_branching(br_type: int, local_id=None):
    return {
        'local_id': local_id or str(uuid4()),
        'type': br_type,
        'content': _create_conditional_branching() if br_type == 1 else _create_selective_branching()
    }


class TestLessonCreating(TestCase):
    def setUp(self) -> None:
        self.course = Course.objects.create(name='course 1', description='course 2')
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
        self.replica_block = {
            'message': 'replica block message 1',
            'location': 1,
            'emotion': 2,
        }
        self.client = APIClient()
        self.super_user = User.objects.create_superuser("admin", "admin@mail.com", "password")
        self.client.login(username=self.super_user.username, password="password")

    def get_lessons(self):
        return Lesson.objects.all()

    def get_units(self):
        return Unit.objects.all()

    def create_simple_lesson(self, units=None, local_id=None):
        from editors.serializers import LessonSerializer
        lesson = Lesson.objects.create(
            course=self.course,
            content=LessonBlock.objects.create(),
            time_cost=0,
            money_cost=0,
            energy_cost=0,
        )

        return LessonSerializer(lesson).data

    def test_creating_and_retrieving_simple_lesson(self):
        lesson_data = self.create_simple_lesson()

        response = self.client.get(f'/api/editors/lessons/{lesson_data["id"]}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], lesson_data['id'])
        self.assertEqual(len(self.course.lessons.all()), 2)
        self.assertEqual(Block.objects.count(), 1)

    def create_replica_unit(self, lesson_id):
        replica_unit = _create_unit(
            self.lesson.id,
            self.replica_block,
            LessonBlockType.replica,
        )
        response = self.client.post(
            '/api/editors/units/',
            replica_unit,
            format='json'
        )
        self.assertEqual(response.status_code, 201)

        return response.json()

    def test_creating_and_retrieving_replica_unit(self):
        unit_data = self.create_replica_unit(self.lesson.id)

        response = self.client.get(f'/api/editors/units/{unit_data["id"]}/')
        self.assertEqual(response.status_code, 200)

        replica_blocks = ReplicaBlock.objects.all()
        self.assertEqual(len(self.get_units()), 1)
        self.assertEqual(len(replica_blocks), 1)
        self.assertEqual(
            response.json()['content']['id'],
            replica_blocks[0].id
        )

    def test_retrieving_lesson_with_units(self):
        self.create_replica_unit(self.lesson.id)
        response = self.client.get(f'/api/editors/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, 200)

        lesson_data = response.json()

        self.assertEqual(lesson_data['id'], self.lesson.id)
        self.assertEqual(len(lesson_data['content']['blocks']), 1)

    def test_patching_lesson(self):
        lesson_data = self.create_simple_lesson()
        lesson_data['content']['blocks'].append(_create_unit(
            lesson_data['id'],
            self.replica_block,
            LessonBlockType.replica,
        ))

        lesson_data['content']['blocks'][0]['next'] = [1]
        lesson_data['timeCost'] = 3
        lesson_data['content']['blocks'][0]['content']['emotion'] = 3

        response = self.client.patch(
            f'/api/editors/lessons/{lesson_data["id"]}/',
            lesson_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        new_lesson_data = response.json()

        # check that we didn't change ids
        self.assertEqual(lesson_data['id'], new_lesson_data['id'])
        self.assertEqual(
            new_lesson_data['content']['id'],
            lesson_data['content']['id'],
        )

        # check we changed exact properties
        self.assertEqual(
            new_lesson_data['content']['blocks'][0].pop('next'),
            [1]
        )
        self.assertNotEqual(
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
        new_lesson_data['content']['blocks'][0]['content'].pop('id')

    def create_simple_quest(self, course_id, lessons, local_id=None):
        response = self.client.post(
            '/api/editors/quests/',
            _create_quests(course_id, lessons, local_id),
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_retrieving_quest(self):
        lesson = _create_simple_lesson(self.course.id)
        quest_data = self.create_simple_quest(self.course.id, [lesson])
        response = self.client.get(
            f'/api/editors/quests/{quest_data["id"]}/',
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lesson.objects.filter(quest_id=quest_data['id']).count(), 1)

    def test_patching_quest(self):
        Lesson.objects.all().delete()

        lesson = self.create_simple_lesson()
        lesson2 = _create_simple_lesson(self.course.id, local_id='lesson_2')

        quest = self.create_simple_quest(self.course.id, [lesson, lesson2])
        quest['x'] = 12.4
        quest['y'] = 42

        response = self.client.patch(
            f'/api/editors/quests/{quest["id"]}/',
            quest,
            format='json'
        )
        self.assertEqual(response.status_code, 200)

        new_quest = response.json()

        self.assertEqual(len(new_quest['lessons']), 2)
        self.assertTrue(lesson['id'] in {new_quest['lessons'][i]['id'] for i in range(2)})
        self.assertEqual(Block.objects.count(), 3)

    def test_create_simple_course(self):
        response = self.client.post(
            '/api/editors/courses/',
            _create_course(),
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Course.objects.count(), 2)

    def create_simple_course(self):
        response = self.client.post(
            f'/api/editors/courses/',
            _create_course(),
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_retrieving_course(self):
        course_data = self.create_simple_course()
        response = self.client.get(
            f'/api/editors/courses/{course_data["id"]}/',
            format='json'
        )
        self.assertEqual(response.status_code, 200)

    def test_patching_course(self):
        from editors.serializers import CourseSerializer
        course_data = CourseSerializer(self.course).data

        course_data['entry'] = 'asd'
        course_data['name'] = 'course 1 patched'
        course_data['lessons'] = [
            _create_simple_lesson(course_data['id'], local_id='lesson 3'),
        ]
        course_data['quests'] = [
            _create_quests(
                course_data['id'],
                [_create_simple_lesson(course_data['id'], local_id='lesson 4')],
                [_create_branching(3)],
            )
        ]
        course_data['branchings'] = [
            _create_branching(1),
            _create_branching(2)
        ]

        response = self.client.patch(
            f'/api/editors/courses/{course_data["id"]}/',
            course_data,
            format='json'
        )

        from pprint import pprint
        pprint(response.json())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(course_data['name'], 'course 1 patched')
        self.assertEqual(len(response.json()['lessons']), 1)
        self.assertEqual(Lesson.objects.filter(course__id=course_data['id']).count(), 2)
        self.assertEqual(len(response.json()['quests']), 1)
        self.assertEqual(Quest.objects.filter(course__id=course_data['id']).count(), 1)
        self.assertEqual(len(response.json()['quests'][0]['branchings']), 1)
        self.assertEqual(Branching.objects.filter(course__id=course_data['id']).count(), 3)
