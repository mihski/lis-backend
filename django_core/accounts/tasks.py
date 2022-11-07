import cvzone
import cv2
import numpy as np

from django.core.files.base import ContentFile
from django.db.models.fields.files import ImageFieldFile
from PIL import Image

from accounts.models import Profile, ProfileAvatarBodyPart
from django_core.celery import app


def _overlay_one_another(backgroud, overlay_image):
    background = backgroud[:, :, :3]
    new_img = cvzone.overlayPNG(background, overlay_image, [0, 0])
    return new_img


def _get_part(body_part: ProfileAvatarBodyPart, state: str = "usual"):
    image_field_file = getattr(body_part, f"{state}_part", None)

    if not image_field_file:
        image_field_file = body_part.usual_part  # noqa

    pil_image = Image.open(image_field_file.path.replace("/django_core/media/", "./"))

    return np.asarray(pil_image)


def _generate_img(profile: Profile, state: str = "usual"):
    result_img = np.zeros_like(_get_part(profile.head_form))

    if profile.hair_form.back_part:
        result_img = _get_part(profile.hair_form, "back")

    result_img = _overlay_one_another(result_img, _get_part(profile.head_form))
    result_img = _overlay_one_another(result_img, _get_part(profile.hair_form, "front"))
    result_img = _overlay_one_another(result_img, _get_part(profile.face_form, state))
    result_img = _overlay_one_another(result_img, _get_part(profile.brows_form, state))
    result_img = _overlay_one_another(result_img, _get_part(profile.cloth_form, state))
    result_img = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)

    _, alpha = cv2.threshold(cv2.cvtColor(result_img, cv2.COLOR_RGB2GRAY), 0, 255, cv2.THRESH_BINARY)
    b, g, r = cv2.split(result_img)
    rgba = [b, g, r, alpha]
    dst = cv2.merge(rgba, 4)

    return dst


def _set_image_field(profile: Profile, body_part: ImageFieldFile, state: str) -> None:
    state_img = _generate_img(profile, state)
    success, image_png = cv2.imencode('.png', state_img)

    if success:
        file = ContentFile(image_png.tobytes())
        body_part.save(f'{state}_avatar.png', file)


def _delete_previous_photos(profile: Profile) -> None:
    profile.usual_image.delete(save=False)
    profile.angry_image.delete(save=False)
    profile.fair_image.delete(save=False)
    profile.happy_image.delete(save=False)
    profile.save()


@app.task
def generate_profile_images(profile_id: int) -> None:
    # TODO 2: delete duplicating

    profile = Profile.objects.get(id=profile_id)
    _set_image_field(profile, profile.usual_image, "usual")
    _set_image_field(profile, profile.angry_image, "angry")
    _set_image_field(profile, profile.fair_image, "fair")
    _set_image_field(profile, profile.happy_image, "happy")
    profile.save()
