from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import (
    Profile,
    Statistics,
    ProfileAvatarHead,
    ProfileAvatarFace,
    ProfileAvatarHair,
    ProfileAvatarBrows,
    ProfileAvatarClothes
)
from lessons.models import NPC
from resources.models import Resources

User = get_user_model()


class ProfileTestCase(TestCase):
    API_URL = "/api/profile/"

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="test",
            email="test@mail.ru",
            password="test"
        )
        self.sd_npc = NPC.objects.create(uid="C1", is_scientific_director=True)
        self.not_sd_npc = NPC.objects.create(uid="C2", is_scientific_director=False)

        self.client = APIClient()
        self.client.force_login(self.user)

    def _get_profile(self) -> Profile:
        return self.user.profile.get()

    def test_profile_related_entities_created(self) -> None:
        """
            Тест на проверку автоматического создания
            моделей профиля -> статистики -> ресурсов
            через django lifecycle
        """
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        self.assertTrue(Statistics.objects.filter(profile=self.user.profile.get()).exists())
        self.assertTrue(Resources.objects.filter(user=self.user.profile.get()).exists())

    def test_setting_name_and_gender(self) -> None:
        body = {"username": "test", "gender": "male"}
        profile = self._get_profile()
        response = self.client.put(path=self.API_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile.refresh_from_db()
        self.assertEqual(profile.username, body["username"])
        self.assertEqual(profile.gender, body["gender"])

    def _generate_avatar_parts(self) -> None:
        ProfileAvatarHead.objects.create()
        ProfileAvatarFace.objects.create()
        ProfileAvatarHair.objects.create()
        ProfileAvatarBrows.objects.create()
        ProfileAvatarClothes.objects.create()

    def test_setting_avatar(self) -> None:
        self._generate_avatar_parts()
        body = {
            "head_form": 1,
            "face_form": 1,
            "hair_form": 1,
            "brows_form": 1,
            "cloth_form": 1,
        }
        profile = self._get_profile()
        response = self.client.put(path=self.API_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile.refresh_from_db()
        for key, value in body.items():
            self.assertEqual(getattr(profile, key).id, value)

    def test_choosing_scientific_director(self):
        body = {"scientific_director": self.sd_npc.id}
        response = self.client.put(path=self.API_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile = self._get_profile()
        profile.refresh_from_db()
        self.assertEqual(profile.scientific_director, self.sd_npc)

    def test_choosing_invalid_scientific_director(self):
        body = {"scientific_director": self.not_sd_npc.id}
        response = self.client.put(path=self.API_URL, data=body)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("scientific_director" in response.json())

    def test_retrieve_profile(self):
        response = self.client.get(path=self.API_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.json()["username"])
        self.assertIsNone(response.json()["gender"])

    def test_retrieve_statistics(self):
        url = self.API_URL + "statistics/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["quests_done"], 0)
        self.assertEqual(response.json()["lessons_done"], 0)
        self.assertEqual(response.json()["total_time_spend"], 0)

    def test_update_statistics(self):
        url = self.API_URL + "statistics/update/"
        body = {
            "quests_done": 2,
            "lessons_done": 2,
            "total_time_spend": 2
        }

        response = self.client.patch(path=url, data=body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for key, value in body.items():
            self.assertEqual(response.json()[key], value)

    def test_partial_update_statistics(self):
        url = self.API_URL + "statistics/update/"
        body = {"total_time_spend": 2}

        response = self.client.patch(path=url, data=body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile_statistics = self._get_profile().statistics
        profile_statistics.refresh_from_db()
        self.assertEqual(profile_statistics.total_time_spend, body["total_time_spend"])
