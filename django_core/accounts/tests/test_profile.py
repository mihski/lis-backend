from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status

from accounts.choices import UniversityPosition
from accounts.models import (
    Profile,
    Statistics,
    ProfileAvatarHead,
    ProfileAvatarFace,
    ProfileAvatarHair,
    ProfileAvatarBrows,
    ProfileAvatarClothes
)
from lessons.models import NPC, Course
from lessons.exceptions import NPCIsNotScientificDirectorException
from resources.models import Resources
from resources.utils import get_max_energy_by_position
from resources.exceptions import NotEnoughEnergyException

User = get_user_model()


class ProfileTestCase(TestCase):
    API_URL = "/api/profile/"

    @classmethod
    def setUpClass(cls) -> None:
        super(ProfileTestCase, cls).setUpClass()
        cls.course = Course.objects.create()
        cls.user = User.objects.create_user(
            username="test",
            email="test@mail.ru",
            password="test"
        )

        cls._create_npcs()

        cls.profile = cls.user.profile.get()
        cls.profile.scientific_director = cls.npcs[0]
        cls.profile.save()

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @classmethod
    def _create_npcs(cls) -> None:
        npcs = [
            NPC(uid="TEST1", is_scientific_director=True),
            NPC(uid="TEST2", is_scientific_director=True),
            NPC(uid="TEST3", is_scientific_director=False)
        ]
        cls.npcs = NPC.objects.bulk_create(npcs)

    def _get_profile(self) -> Profile:
        return self.user.profile.get(course=self.course)

    def _update_university_position(self, position: UniversityPosition) -> None:
        self.profile.university_position = position.value
        self.profile.save()
        self.profile.refresh_from_db()

    def test_profile_related_entities_created(self) -> None:
        """
            Тест на проверку автоматического создания
            моделей профиля -> статистики -> ресурсов
            через django lifecycle
        """
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        self.assertTrue(Statistics.objects.filter(profile=self.user.profile.get(course=self.course)).exists())
        self.assertTrue(Resources.objects.filter(user=self.user.profile.get(course=self.course)).exists())

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
        self._update_university_position(UniversityPosition.INTERN)

        sd_npc = self.npcs[1]
        body = {"scientific_director": sd_npc.id}

        response = self.client.put(path=self.API_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile = self._get_profile()
        profile.refresh_from_db()
        self.assertEqual(profile.scientific_director, sd_npc)

    def test_choosing_invalid_scientific_director(self):
        body = {"scientific_director": self.npcs[-1].id}
        response = self.client.put(path=self.API_URL, data=body)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.json()["error_code"], NPCIsNotScientificDirectorException.default_code)

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

    def test_energy_decrease_on_change_scientific_director(self) -> None:
        self._update_university_position(UniversityPosition.LABORATORY_ASSISTANT)
        max_energy = get_max_energy_by_position(UniversityPosition.LABORATORY_ASSISTANT)

        sd_npc = self.npcs[1]
        body = {"scientific_director": sd_npc.id}

        response = self.client.put(path=self.API_URL, data=body)

        profile = self._get_profile()
        profile.refresh_from_db()
        energy_delta = max_energy - settings.CHANGE_SCIENTIFIC_DIRECTOR_ENERGY_COST

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["scientific_director"], sd_npc.id)
        self.assertEqual(profile.resources.energy_amount, energy_delta)

    def test_not_enough_energy_on_change_scientific_director(self) -> None:
        response = self.client.put(
            self.API_URL,
            data={"scientific_director": self.npcs[1].id}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_code"], NotEnoughEnergyException.default_code)

    def test_replay(self) -> None:
        profile = self._get_profile()
        response = self.client.post("/api/replay/")
        profile.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(profile.user)
        self.assertTrue(self.user.profile.exists())
