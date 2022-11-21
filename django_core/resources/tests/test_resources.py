from datetime import timedelta

from django.test import TestCase, override_settings
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User, UniversityPosition
from lessons.models import Course
from resources.tasks import refill_resources
from resources.utils import get_max_energy_by_position


class ResourcesTestCase(TestCase):
    START_COURSE_DATE = settings.START_COURSE_DATE

    @classmethod
    def setUpClass(cls):
        super(ResourcesTestCase, cls).setUpClass()
        cls.course = Course.objects.create()
        cls.user = User.objects.create(username="test1", email="test1@mail.ru", password="test1")
        cls.profile = cls.user.profile.get(course=cls.course)
        cls.resources = cls.profile.resources

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def __update_university_position(self, position: UniversityPosition) -> None:
        self.profile.university_position = position.value
        self.profile.save()

    def test_resource_retrieving(self) -> None:
        response = self.client.get("/api/resources/retrieve/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["energyAmount"], 0)
        self.assertEqual(response.json()["moneyAmount"], 10000)
        self.assertEqual(response.json()["maxEnergyAmount"], 0)
        self.assertEqual(
            response.json()["timeAmount"],
            int(self.START_COURSE_DATE.timestamp()) * 1000
        )

    def test_energy_not_decrease_after_changing_uni_position(self) -> None:
        self.__update_university_position(UniversityPosition.INTERN)
        self.__update_university_position(UniversityPosition.ENGINEER)

        self.resources.refresh_from_db()
        self.assertEqual(self.resources.energy_amount, get_max_energy_by_position(UniversityPosition.INTERN))

    def test_resource_updating(self) -> None:
        position = UniversityPosition.INTERN
        self.__update_university_position(position)

        cases = [
            # (timeDelta, moneyDelta, energyDelta), is_successful
            ((5, 10, -3), True),
            ((0, -12000, 3), False),
            ((-1, 30, 3), False),
            ((0, -4, -2), True),
        ]

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
        profile_timestamp = int((self.START_COURSE_DATE + timedelta(days=5)).timestamp()) * 1000
        print(response.json())
        self.assertEqual(response.json()["timeAmount"], profile_timestamp) # = 5 + 0
        self.assertEqual(response.json()["moneyAmount"], 10006)  # = 12000 + 10 - 4
        self.assertEqual(response.json()["energyAmount"], 7)  # = 10 - 5

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPOGATES=True, BROKER_BACKEND="memory")
    def test_celery_refill_energy(self) -> None:
        self.client.get("/api/resources/retrieve/")

        position = UniversityPosition.INTERN
        max_energy = get_max_energy_by_position(position)
        self.__update_university_position(position)

        refill_resources.delay()
        self.assertEqual(self.resources.energy_amount, max_energy)
