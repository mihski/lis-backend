from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User


class ResourceTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='test1', email='test1@mail.ru', password='test1')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_resource_retrieving(self):
        response = self.client.get("/api/resources/retrieve_resources/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['timeAmount'], 0)
        self.assertEqual(response.json()['energyAmount'], 0)
        self.assertEqual(response.json()['moneyAmount'], 0)

    def test_resource_updating(self):
        cases = [
            ((5, 10, 3), True),  # (timeDelta, moneyDelta, energyDelta), is_successful
            ((0, -20, 3), False),
            ((-1, 30, 3), False),
            ((0, -4, -1), True),
        ]
        response = self.client.get("/api/resources/retrieve_resources/")
        time_amount = response.json()['timeAmount']
        money_amount = response.json()['moneyAmount']
        energy_amount = response.json()['energyAmount']

        for (time_delta, money_delta, energy_delta), is_successful in cases:
            response = self.client.patch(
                "/api/resources/update/",
                {
                    "timeDelta": time_delta,
                    "moneyDelta": money_delta,
                    "energyDelta": energy_delta,
                }
            )

            if not is_successful:
                self.assertNotEqual(response.status_code, 200)
                continue

            self.assertEqual(response.status_code, 200)
            time_amount += time_delta
            money_amount += money_delta
            energy_amount += energy_delta
