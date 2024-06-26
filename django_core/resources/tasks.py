import logging

from django.db.models import QuerySet

from django_core.celery import app
from resources.models import Resources
from resources.utils import get_max_energy_by_position
from accounts.models import Profile

logger = logging.getLogger('celery')


@app.task
def refill_resources() -> None:
    """
        Задача для обновления ресурсов в фоне
    """
    resources_qs: QuerySet[Resources] = Resources.objects.all()
    update_list = []

    logger.info('Старт задачи обновления ресурсов')
    for resource in resources_qs:
        profile = resource.user
        logger.info(f'Пользователь: {profile.isu} - {profile.username}')
        logger.info(f'Должность: {profile.university_position}')
        logger.info(f'Было энергии: {resource.energy_amount}')

        energy = get_max_energy_by_position(profile.university_position)
        resource.set_energy(energy)
        logger.info(f'Стало энергии: {resource.energy_amount}')
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
