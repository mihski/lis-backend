from django.core.management import BaseCommand

from helpers.google_sheets import GoogleSheetsConnection, GoogleSheetsAdapter
from helpers.course_tree import CourseLessonsTree
from accounts.models import Profile
from lessons.models import Course, Branching, ProfileCourseDone

connection = GoogleSheetsConnection().get_connection()


class Command(BaseCommand):
    def handle(self, *args, **options):
        users_data = []
        course = Course.objects.first()
        profiles = Profile.objects.filter(course=course, user__isnull=False).all()
        course_tree = CourseLessonsTree(course)

        for id_, profile in enumerate(profiles, start=1):
            course_map = course_tree.get_map_for_profile(profile)
            active_id = course_tree.get_active(profile)

            if active_id == len(course_map) or isinstance(course_map[active_id], Branching):
                current_entity = course_map[active_id - 1]
            else:
                current_entity = course_map[active_id]

            current_quest = course.locale["ru"].get(quest.name, "-") if (quest := current_entity.quest) else "-"
            current_entity = course.locale["ru"].get(current_entity.name, "-")

            users_data.append([profile.isu, profile.username, profile.user.email, current_entity, current_quest])

        GoogleSheetsAdapter(connection).upload_statistics(users_data)
