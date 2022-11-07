from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from lessons.models import Course

User = get_user_model()


class ProfileTestCase(TestCase):
    def setUp(self) -> None:
        Course.objects.create()
        self.user = User.objects.create(username="test1", email="test1@mail.ru", password="test1")
        self.client = APIClient()
        self.client.force_login(self.user)

    def test_replay(self) -> None:
        profile = self.user.profile.get()

        response = self.client.post("/api/replay/")
        self.assertEqual(response.status_code, 200)

        profile.refresh_from_db()
        self.assertIsNone(profile.user)

        self.assertTrue(self.user.profile.exists())
