import glob
import os

from django.core.management.base import BaseCommand, CommandError
from accounts.models import (
    ProfileAvatarClothes,
    ProfileAvatarHead,
    ProfileAvatarFace,
    ProfileAvatarHair,
    ProfileAvatarBrows,
)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.PART_PROCESSOR = {
            "Brows": self.process_brows,
            "Face": self.process_face,
            "Hair": self.process_hair,
            "Head": self.process_head,
            "Clothes": self.process_clothes,
        }

    def _get_element_with_substr(self, elements: list[str], substr: str):
        for element in elements:
            if substr.lower() in element.lower():
                return element

    def process_brows(self, part_type_folder: str, gender: str) -> None:
        parts = os.listdir(part_type_folder)
        ProfileAvatarBrows.objects.get_or_create(
            gender=gender,
            angry_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "angry")
            ),
            usual_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "usual")
            ),
            fair_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "fair")
            ),
            happy_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "happy")
            ),
        )

    def process_face(self, part_type_folder: str, gender: str) -> None:
        parts = os.listdir(part_type_folder)
        ProfileAvatarFace.objects.get_or_create(
            gender=gender,
            angry_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "angry")
            ),
            usual_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "usual")
            ),
            fair_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "fair")
            ),
            happy_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "happy")
            ),
        )

    def process_hair(self, part_type_folder: str, gender: str):
        parts = os.listdir(part_type_folder)

        back_hair_element = self._get_element_with_substr(parts, "back")
        back_part_path = None

        if back_hair_element:
            back_part_path = os.path.join(
                part_type_folder,
                back_hair_element
            )

        ProfileAvatarHair.objects.get_or_create(
            gender=gender,
            back_part=back_part_path,
            front_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "front")
            ),
        )

    def process_head(self, part_type_folder: str, gender: str):
        parts = os.listdir(part_type_folder)
        ProfileAvatarHead.objects.get_or_create(
            gender=gender,
            usual_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "head")
            ),
        )

    def process_clothes(self, part_type_folder: str, gender: str):
        parts = os.listdir(part_type_folder)
        ProfileAvatarClothes.objects.get_or_create(
            gender=gender,
            angry_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "angry")
            ),
            usual_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "usual")
            ),
            fair_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "fair")
            ),
            happy_part=os.path.join(
                part_type_folder,
                self._get_element_with_substr(parts, "happy")
            ),
        )

    def process_folder(self, folder_name: str, gender: str) -> None:
        folder = os.path.join("media", folder_name)
        parts_names = os.listdir(folder)
        unexist_parts = set(self.PART_PROCESSOR.keys()) - set(parts_names)

        if unexist_parts:
            raise CommandError(f"There is no parts: {unexist_parts}")

        for part_name in self.PART_PROCESSOR:
            part_folder = os.path.join(folder, part_name)
            part_processor = self.PART_PROCESSOR[part_name]

            for part_type_folder in glob.glob(os.path.join(part_folder, "*")):
                part_processor(part_type_folder, gender)

    def handle(self, *args, **options):
        if (
            not os.path.isdir("media/man_parts") or
            not os.path.isdir("media/woman_parts")
        ):
            raise CommandError("There are no man_parts or woman_parts folder in media")

        self.process_folder("man_parts", "male")
        self.process_folder("woman_parts", "female")
