from django.apps import AppConfig


class LessonConfig(AppConfig):
    name = "lessons"

    def ready(self):
        import lessons.signals
