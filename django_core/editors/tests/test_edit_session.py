from django.test import TestCase, Client

from accounts.models import User
from editors.models import EditorSession
from lessons.models import Course, Quest


class TestEditorSession(TestCase):
    def setUp(self) -> None:
        self.course = Course.objects.create()
        self.quest = Quest.objects.create(local_id="lesson 1")

        self.user = User.objects.create_user("regular", "regular@mail.com", "password")
        self.super_user = User.objects.create_superuser("admin", "admin@mail.com", "password")
        self.super_user2 = User.objects.create_superuser("admin2", "admin2@mail.com", "password")

        self.client = Client()

    def start_session(self, **kwargs):
        response = self.client.post(
            f"/api/editors/sessions/",
            kwargs,
            format="json"
        )
        return response

    def end_session(self, **kwargs):
        response = self.client.post(
            f"/api/editors/sessions/end_session/",
            kwargs,
            format="json"
        )
        return response

    def filter_sessions(self, course_id: int, local_ids: str = ''):
        response = self.client.get(
            f"/api/editors/sessions/?course={course_id}&local_ids={local_ids}",
        )
        return response

    def test_start_session(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.start_session(course=self.course.id)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(EditorSession.objects.count(), 1)
        self.client.logout()

    def test_unauth_start_session(self):
        response = self.start_session(course=self.course.id)
        self.assertEqual(response.status_code, 403)

    def test_regular_user_start_session(self):
        self.client.login(username=self.user.username, password="password")
        response = self.start_session(course=self.course.id)
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_forbidden_user_start_session(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.start_session(course=self.course.id)
        self.assertEqual(response.status_code, 201)
        response = self.start_session(course=self.course.id)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(EditorSession.objects.count(), 1)
        self.client.logout()

        self.client.login(username=self.super_user2, password="password")
        response = self.start_session(course=self.course.id)
        print(response.json())
        self.assertEqual(response.status_code, 400)
        self.client.logout()

    def test_start_two_sessions(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.start_session(course=self.course.id)
        self.assertEqual(response.status_code, 201)
        self.client.login(username=self.super_user2.username, password="password")
        response = self.start_session(course=self.course.id, local_id=self.quest.local_id)
        self.assertEqual(response.status_code, 201)
        self.client.logout()

    def test_end_user_session(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.start_session(course=self.course.id)
        self.assertEqual(response.status_code, 201)
        response = self.end_session(course=self.course.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EditorSession.objects.count(), 0)

    def test_end_unexist_user_session(self):
        self.client.login(username=self.super_user.username, password="password")
        response = self.end_session(course=self.course.id)
        self.assertEqual(response.json()["detail"]["user"], "there is no session for user")
        self.assertEqual(response.status_code, 400)

    def test_check_filter_course(self):
        self.client.login(username=self.super_user.username, password="password")
        self.start_session(course=self.course.id)
        self.start_session(course=self.course.id, local_id=self.quest.local_id)
        response = self.filter_sessions(course_id=self.course.id, local_ids='')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

        response = self.filter_sessions(course_id=self.course.id, local_ids=','.join([self.quest.local_id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
