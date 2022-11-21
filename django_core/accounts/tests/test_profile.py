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
from accounts.serializers import ProfileStatisticsSerializer
from lessons.models import NPC, Course, Lesson, LessonBlock, Unit
from lessons.exceptions import NPCIsNotScientificDirectorException, FirstScientificDirectorIsNotDefaultException
from resources.models import Resources, EmotionData
from resources.serializers import EmotionDataSerializer
from resources.utils import get_max_energy_by_position
from resources.exceptions import NotEnoughEnergyException
from student_tasks.models import StudentTaskAnswer

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
            NPC(uid="TEST3", is_scientific_director=False),
            NPC(uid="C4", is_scientific_director=True)
        ]
        cls.npcs = NPC.objects.bulk_create(npcs)
        cls.default_npc = cls.npcs[-1]

    def _create_emotion_data(self) -> None:
        profile = self._get_profile()

        self.lesson = Lesson.objects.create(
            local_id="n_001", name="n_001_name",
            time_cost=0, energy_cost=0, money_cost=0,
            content=LessonBlock.objects.create(),
            course=self.course
        )

        emotions = [
            EmotionData(profile=profile, emotion=1, comment="1", lesson=self.lesson),
            EmotionData(profile=profile, emotion=2, comment="2", lesson=self.lesson),
            EmotionData(profile=profile, emotion=3, comment="3", lesson=self.lesson),
        ]
        self.emotions = EmotionData.objects.bulk_create(emotions)

    def _create_answered_tasks(self) -> None:
        profile = self._get_profile()
        units = [
            Unit(
                lesson=self.lesson,
                type=300 + x,
                content=dict(),
                next=list()
            )
            for x in range(10)
        ]
        tasks = Unit.objects.bulk_create(units)

        answered_tasks = [
            StudentTaskAnswer(
                profile=profile,
                task=tasks[i],
                is_correct=i % 2
            )
            for i in range(len(tasks))
        ]
        StudentTaskAnswer.objects.bulk_create(answered_tasks)

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

    def test_update_scientific_director(self):
        position = UniversityPosition.INTERN
        max_energy = get_max_energy_by_position(position)
        self._update_university_position(position)

        sd_npc = self.npcs[1]
        body = {"scientific_director": sd_npc.id}

        response = self.client.put(path=self.API_URL, data=body)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        profile = self._get_profile()
        profile.refresh_from_db()
        self.assertEqual(profile.scientific_director, sd_npc)
        self.assertEqual(
            profile.resources.energy_amount,
            max_energy - settings.CHANGE_SCIENTIFIC_DIRECTOR_ENERGY_COST
        )

    def test_choosing_invalid_scientific_director(self):
        body = {"scientific_director": self.npcs[2].id}
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

    def test_first_scientific_director_not_decrease_energy(self) -> None:
        """
            По умолчанию энергии 0.
            Если будет попытка снятия энергии,
            тест полетит.
        """
        test_user = User.objects.create_user(
            username="test2",
            email="test2@test.com",
            password="test123"
        )
        client = APIClient()
        client.force_authenticate(test_user)

        npc_id = self.default_npc.id
        body = {"scientific_director": npc_id}
        response = client.put(self.API_URL, body)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["scientific_director"], npc_id)

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

    def test_album_retrieve(self) -> None:
        self._create_emotion_data()
        self._create_answered_tasks()
        profile = self._get_profile()

        url = self.API_URL + "album/"
        response = self.client.get(path=url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["statistics"],
            ProfileStatisticsSerializer(instance=profile.statistics).data
        )
        serialized_emotions = EmotionDataSerializer(data=self.emotions, many=True)
        serialized_emotions.is_valid()

        self.assertEqual(
            response.json()["emotions"],
            serialized_emotions.data
        )

    def test_set_first_scientific_director_is_not_default_raises_exception(self):
        user = User.objects.create_user(
            username="test_user",
            email="test@test.com",
            password="123"
        )
        client = APIClient()
        client.force_authenticate(user)

        body = {"scientific_director": self.npcs[0].id}
        response = client.put(self.API_URL, data=body)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_code"], FirstScientificDirectorIsNotDefaultException.default_code)
