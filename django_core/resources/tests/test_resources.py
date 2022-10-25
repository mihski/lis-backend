from datetime import timedelta

from django.test import TestCase, override_settings
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User, Profile, UniversityPosition
from resources.tasks import refill_resources
from resources.utils import get_max_energy_by_position


class ResourcesTestCase(TestCase):
    START_COURSE_DATE = settings.START_COURSE_DATE

    def setUp(self) -> None:
        user = User.objects.create(username="test1", email="test1@mail.ru", password="test1")
        self.profile = Profile.objects.create(user=user)
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def __update_university_position(self, position: UniversityPosition) -> None:
        self.profile.university_position = position.value
        self.profile.save()

    def test_update_not_creates_resources(self) -> None:
        response = self.client.patch(
            "/api/resources/update/",
            {
                "timeDelta": 0,
                "moneyDelta": 0,
                "energyDelta": 0,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_resource_retrieving(self) -> None:
        response = self.client.get("/api/resources/retrieve/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["energyAmount"], 0)
        self.assertEqual(response.json()["moneyAmount"], 0)
        self.assertEqual(response.json()["maxEnergyAmount"], 0)
        self.assertEqual(
            response.json()["timeAmount"],
            self.START_COURSE_DATE.timestamp()
        )

    def test_energy_update_related_to_max_energy(self) -> None:
        energy_data = {
            UniversityPosition.INTERN: get_max_energy_by_position(UniversityPosition.INTERN),
            UniversityPosition.ENGINEER: get_max_energy_by_position(UniversityPosition.ENGINEER),
        }

        for position, max_energy in energy_data.items():
            self.__update_university_position(position)
            response = self.client.get("/api/resources/retrieve/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["energyAmount"], max_energy)

    def test_resource_updating(self) -> None:
        position = UniversityPosition.INTERN
        self.__update_university_position(position)

        cases = [
            # (timeDelta, moneyDelta, energyDelta), is_successful
            ((5, 10, -3), True),
            ((0, -20, 3), False),
            ((-1, 30, 3), False),
            ((0, -4, -2), True),
        ]

        self.client.get("/api/resources/retrieve/")  # <- creates resources
        for (time_delta, money_delta, energy_delta), is_successful in cases:
            patch_response = self.client.patch(
                "/api/resources/update/",
                {
                    "timeDelta": time_delta,
                    "moneyDelta": money_delta,
                    "energyDelta": energy_delta,
                },
            )

            if not is_successful:
                self.assertEqual(patch_response.status_code, status.HTTP_400_BAD_REQUEST)
                continue
            self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        response = self.client.get("/api/resources/retrieve/")
        profile_timestamp = (self.START_COURSE_DATE + timedelta(days=5)).timestamp()
        self.assertEqual(response.json()["timeAmount"], profile_timestamp) # = 5 + 0
        self.assertEqual(response.json()["moneyAmount"], 6)  # = 10 - 4
        self.assertEqual(response.json()["energyAmount"], 5)  # = 10 - 5

    def test_raise_exception_without_profile(self):
        self.profile.delete()
        response = self.client.get("/api/resources/retrieve/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.json()["detail"], "You should to create a profile to get access for requested resource",
        )

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True, BROKER_BACKEND="memory")
    def test_celery_refill_energy(self) -> None:
        self.client.get("/api/resources/retrieve/")

        position = UniversityPosition.INTERN
        max_energy = get_max_energy_by_position(position)
        self.profile.university_position = position.value
        self.profile.save()

        refill_resources.delay()
        self.assertEqual(self.profile.resources.energy_amount, max_energy)
