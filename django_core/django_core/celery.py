import os

from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging  # noqa

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_core.settings")

app = Celery("django_core")
app.config_from_object("django.conf:settings", namespace="CELERY")


@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig  # noqa
    from django.conf import settings  # noqa

    dictConfig(settings.LOGGING)


app.autodiscover_tasks()


app.conf.beat_schedule = {
    "refill_resources_every_night": {
        "task": "resources.tasks.refill_resources",
        "schedule": crontab(minute="0", hour="0")
    },
    "upload_statistics_every_night": {
        "task": "accounts.tasks.upload_statistics",
        "schedule": crontab(minute="0", hour="0")
    }
}
