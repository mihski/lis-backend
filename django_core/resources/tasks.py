from django.db.models import QuerySet

from django_core.celery import app
from resources.models import Resources
from accounts.models import UniversityPosition

ENERGY_DATA = {
    UniversityPosition.STUDENT.value: 0,
    UniversityPosition.INTERN.value: 10,
    UniversityPosition.LABORATORY_ASSISTANT.value: 9,
    UniversityPosition.ENGINEER.value: 9,
    UniversityPosition.JUN_RESEARCH_ASSISTANT.value: 8,
}


@app.task
def refill_resources() -> None:
    """
        Задача для обновления ресурсов в фоне
    """
    queryset: QuerySet[Resources] = Resources.objects.all()

    for item in queryset:
        university_position = item.user.university_position
        energy = ENERGY_DATA[university_position]
        item.energy_amount = energy
        item.save()
