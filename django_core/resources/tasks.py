from django.db.models import QuerySet

from django_core.celery import app
from resources.models import Resources
from resources.utils import get_max_energy_by_position
from accounts.models import UniversityPosition, Profile


@app.task
def refill_resources() -> None:
    """
        Задача для обновления ресурсов в фоне
    """
    resources_qs: QuerySet[Resources] = Resources.objects.all()
    update_list = []

    for resource in resources_qs:
        university_position = resource.user.university_position
        position = UniversityPosition(university_position)

        energy = get_max_energy_by_position(position)
        resource.set_energy(energy)
        update_list.append(resource)

    Resources.objects.bulk_update(update_list, ["energy_amount"])


@app.task
def deactivate_ultimate(profile_id: int) -> None:
    """
        Отложенная задача, которая отключает ультимейт
    """
    profile = Profile.objects.get(id=profile_id)
    profile.ultimate_activated = False
    profile.ultimate_finish_datetime = None
    profile.save()
