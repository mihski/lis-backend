from django.core.management import BaseCommand
from tqdm import tqdm

from helpers.google_sheets import GoogleSheetsConnection, GoogleSheetsAdapter
from helpers.course_tree import CourseLessonsTree
from accounts.models import Profile
from lessons.models import Course, Branching

connection = GoogleSheetsConnection().get_connection()


class Command(BaseCommand):

    def handle(self, *args, **options):
        users_data = []
        course = Course.objects.first()
        profiles = Profile.objects.filter(course=course, user__isnull=False).all()
        course_tree = CourseLessonsTree(course)

        with tqdm(total=len(profiles), ncols=100) as pbar:
            for id_, profile in enumerate(profiles, start=1):
                course_map = course_tree.get_map_for_profile(profile)
                active_id = course_tree.get_active(profile)

                if active_id > len(course_map):
                    current_entity = course_map[-1]

                elif (active_id == len(course_map) or
                      isinstance(course_map[active_id], Branching)):
                    current_entity = course_map[active_id - 1]
                else:
                    current_entity = course_map[active_id]

                current_quest = course.locale["ru"].get(quest.name, "-") if (
                    quest := current_entity.quest) else "-"
                if not isinstance(current_entity, Branching):
                    current_entity = course.locale["ru"].get(current_entity.name, "-")
                else:
                    current_entity = str(current_entity)

                users_data.append(
                    [
                        profile.isu,
                        profile.username,
                        profile.user.email,
                        current_entity,
                        current_quest,
                    ]
                )
                pbar.update(1)

        GoogleSheetsAdapter(connection).upload_statistics(users_data)
