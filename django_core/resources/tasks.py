from django.db.models import QuerySet

from django_core.celery import app
from resources.models import Resources
from accounts.models import UniversityPosition

POSITION_ENERGY_MAX_DATA = {
    UniversityPosition.STUDENT: 0,
    UniversityPosition.INTERN: 10,
    UniversityPosition.LABORATORY_ASSISTANT: 9,
    UniversityPosition.ENGINEER: 9,
    UniversityPosition.JUN_RESEARCH_ASSISTANT: 8,
}


@app.task
def refill_resources() -> None:
    """
        Задача для обновления ресурсов в фоне
    """
    resources_qs: QuerySet[Resources] = Resources.objects.all()
    update_list = []

    for resource in resources_qs:
        university_position = resource.user.university_position
        position = UniversityPosition.from_str(university_position)

        energy = POSITION_ENERGY_MAX_DATA[position]
        resource.energy_amount = energy
        update_list.append(resource)

    Resources.objects.bulk_update(update_list, ["energy_amount"])
