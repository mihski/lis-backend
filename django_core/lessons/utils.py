from accounts.models import Profile
from accounts.serializers import ProfileSerializer
from lessons.models import UnitAffect


def process_affect(affect: UnitAffect, profile: Profile = None) -> None:
    if affect and affect.code in [UnitAffect.UnitCodeType.LABORATORY_CHOICE, UnitAffect.UnitCodeType.JOB_CHOICE]:
        serializer = ProfileSerializer(
            instance=profile,
            data=affect.content,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
