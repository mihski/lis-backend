from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User, Profile, UniversityPosition
from resources.tasks import refill_resources, ENERGY_DATA


class ResourcesTestCase(TestCase):
    def setUp(self) -> None:
        user = User.objects.create(username="test1", email="test1@mail.ru", password="test1")
        self.profile = Profile.objects.create(user=user)
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_resource_retrieving(self) -> None:
        response = self.client.get("/api/resources/retrieve/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["timeAmount"], 0)
        self.assertEqual(response.json()["energyAmount"], 0)
        self.assertEqual(response.json()["moneyAmount"], 0)

    def test_resource_updating(self) -> None:
        cases = [
            # (timeDelta, moneyDelta, energyDelta), is_successful
            ((5, 10, 3), True),
            ((0, -20, 3), False),
            ((-1, 30, 3), False),
            ((0, -4, -1), True),
        ]

        self.client.get("/api/resources/retrieve/")  # -> creates resources with 0 values
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
        self.assertEqual(response.json()["timeAmount"], 5)
        self.assertEqual(response.json()["moneyAmount"], 6)
        self.assertEqual(response.json()["energyAmount"], 2)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True, BROKER_BACKEND="memory")
    def test_celery_refill_energy(self) -> None:
        self.client.get("/api/resources/retrieve/")

        self.profile.university_position = UniversityPosition.INTERN.value
        self.profile.save()

        refill_resources.delay()
        self.assertEqual(self.profile.resources.energy_amount, ENERGY_DATA[UniversityPosition.INTERN.value])
