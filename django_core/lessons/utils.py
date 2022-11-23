from accounts.models import Profile
from accounts.serializers import ProfileSerializer
from helpers.course_tree import CourseLessonsTree
from lessons.models import UnitAffect, Lesson, Branching
from resources.utils import get_max_energy_by_position


def process_affect(affect: UnitAffect, profile: Profile) -> None:
    if affect and affect.code in [UnitAffect.UnitCodeType.LABORATORY_CHOICE, UnitAffect.UnitCodeType.JOB_CHOICE]:
        serializer = ProfileSerializer(
            instance=profile,
            data=affect.content,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if affect.code == UnitAffect.UnitCodeType.JOB_CHOICE:
            profile.resources.set_energy(get_max_energy_by_position(profile.university_position))
            profile.resources.save()


def check_entity_is_accessible(profile: Profile, entity: Lesson | Branching) -> bool:
    course_tree = CourseLessonsTree(entity.course)
    course_map = [block.local_id for block in course_tree.get_map_for_profile(profile)]

    if entity.local_id not in course_map:
        return False

    active_id = course_tree.get_active(profile)

    return course_map.index(entity.local_id) <= active_id
