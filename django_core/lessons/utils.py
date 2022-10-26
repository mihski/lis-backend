from accounts.models import Profile
from accounts.serializers import ProfileSerializer
from lessons.models import UnitAffect
from resources.utils import get_max_energy_by_position


def process_affect(affect: UnitAffect, profile: Profile = None) -> None:
    if affect and affect.code in [UnitAffect.UnitCodeType.LABORATORY_CHOICE, UnitAffect.UnitCodeType.JOB_CHOICE]:
        serializer = ProfileSerializer(
            instance=profile,
            data=affect.content,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if affect.code == UnitAffect.UnitCodeType.JOB_CHOICE:
            profile.resources.energy_amount = get_max_energy_by_position(profile.university_position)
            profile.resources.save()
