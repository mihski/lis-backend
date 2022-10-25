from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User, Profile, Statistics
from lessons.models import NPC


class ProfileTestCase(TestCase):
    API_URL = "/api/profile/"

    def setUp(self) -> None:
        user = User.objects.create_user(
            username="test",
            email="test@mail.ru",
            password="test"
        )
        self.profile = Profile.objects.create(user=user)
        self.statistics = Statistics.objects.create(profile=self.profile)

        self.sd_npc = NPC.objects.create(uid="C1", is_scientific_director=True)
        self.not_sd_npc = NPC.objects.create(uid="C2", is_scientific_director=False)

        self.client = APIClient()
        self.client.force_login(user)

    def test_setting_name_and_gender(self) -> None:
        body = {"username": "test", "gender": "male"}

        response = self.client.put(path=self.API_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.username, body["username"])
        self.assertEqual(self.profile.gender, body["gender"])

    def test_setting_avatar(self) -> None:
        body = {"head_form": "1", "face_form": "2", "hair_form": "3", "dress_form": "4"}
        response = self.client.put(path=self.API_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.head_form, "1")
        self.assertEqual(self.profile.face_form, "2")
        self.assertEqual(self.profile.hair_form, "3")
        self.assertEqual(self.profile.dress_form, "4")

    def test_choosing_scientific_director(self):
        body = {"scientific_director": self.sd_npc.id}
        response = self.client.put(path=self.API_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.scientific_director, self.sd_npc)

    def test_choosing_invalid_scientific_director(self):
        body = {"scientific_director": self.not_sd_npc.id}
        response = self.client.put(path=self.API_URL, data=body)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("scientific_director" in response.json())

    def test_retrieve_profile(self):
        response = self.client.get(path=self.API_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("username" in response.json())
        self.assertTrue("head_form" in response.json())

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

        self.statistics.refresh_from_db()
        self.assertEqual(self.statistics.total_time_spend, body["total_time_spend"])

    def test_retrieve_statistics_without_profile_raises_exception(self):
        url = self.API_URL + "statistics/"
        self.profile.delete()

        response = self.client.get(path=url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            response.json()["detail"],
            "You should to create a profile to get access for requested resource",
        )

    def test_update_non_existent_statistics_raises_exception(self):
        url = self.API_URL + "statistics/update/"
        body = {"total_time_spend": 2}
        self.statistics.delete()

        response = self.client.patch(path=url, data=body)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            response.json()["detail"],
            "Your profile doesn't have any statistics"
        )
