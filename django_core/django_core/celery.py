import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_core.settings")

app = Celery("django_core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "refill_resources_every_night": {
        "task": "resources.tasks.refill_resources",
        "schedule": crontab(minute="0", hour="0")
    },
}
д