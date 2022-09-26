from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import User, Profile
from lessons.models import NPC


class ProfileTestCase(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user("test", "test@mail.ru", "test")
        self.profile = Profile.objects.create(user=user)

        self.sd_npc = NPC.objects.create(uid="C1", is_scientific_director=True)
        self.not_sd_npc = NPC.objects.create(uid="C2", is_scientific_director=False)

        self.client = APIClient()
        self.client.force_login(user)

    def test_setting_name_and_gender(self) -> None:
        first_name = "first_name"
        gender = "male"

        response = self.client.put(
            f"/api/accounts/profile/",
            {"first_name": first_name, "gender": gender}
        )
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()

        self.assertEqual(self.profile.first_name, first_name)
        self.assertEqual(self.profile.gender, gender)

    def test_setting_avatar(self) -> None:
        response = self.client.put(
            f"/api/accounts/profile/",
            {"head_form": "1", "face_form": "2", "hair_form": "3", "dress_form": "4"}
        )
        self.assertEqual(response.status_code, 200)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.head_form, "1")
        self.assertEqual(self.profile.face_form, "2")
        self.assertEqual(self.profile.hair_form, "3")
        self.assertEqual(self.profile.dress_form, "4")

    def test_choosing_scientific_director(self):
        response = self.client.put(
            f"/api/accounts/profile/",
            {"scientific_director": self.sd_npc.id}
        )
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.scientific_director, self.sd_npc)

    def test_choosing_invalid_scientific_director(self):
        response = self.client.put(
            f"/api/accounts/profile/",
            {"scientific_director": self.not_sd_npc.id}
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue("scientific_director" in response.json())

    def test_get_profile(self):
        response = self.client.get(f"/api/accounts/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("first_name" in response.json())
        self.assertTrue("head_form" in response.json())
