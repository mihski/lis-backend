from django.core.management import BaseCommand

from accounts.models import Profile
from lessons.models import ProfileLessonDone, Unit, Lesson


class Command(BaseCommand):
    def handle(self, *args, **options):
        lessons_done = ProfileLessonDone.objects.select_related("profile").all()
        profiles = Profile.objects.select_related("statistics").all()

        for profile in profiles:
            print(f"For profile {profile.user.username}")

            statistics = profile.statistics
            profile_lessons = Lesson.objects.filter(
                id__in=lessons_done.filter(profile=profile).values_list("lesson", flat=True)
            )

            statistics.quests_done = profile_lessons.filter(quest__isnull=True, next__in=["", "-1"]).count()
            statistics.lessons_done = Unit.objects.filter(lesson__in=profile_lessons, type__gte=300, type__lt=400).count()
            statistics.save()

            print(f"Quests done:", statistics.quests_done)
            print(f"Lessons done:", statistics.lessons_done)
