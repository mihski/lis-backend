import logging

import datetime as dt

from accounts.choices import UniversityPosition
from accounts import models

logger = logging.Logger(__file__)


POSITION_ENERGY_MAX_DATA = {
    UniversityPosition.STUDENT: 0,
    UniversityPosition.INTERN: 10,
    UniversityPosition.LABORATORY_ASSISTANT: 9,
    UniversityPosition.ENGINEER: 9,
    UniversityPosition.JUN_RESEARCH_ASSISTANT: 8,
}


def get_max_energy_by_position(position: str) -> int:
    position = UniversityPosition(position)
    return POSITION_ENERGY_MAX_DATA[position]


def check_ultimate_is_active(profile: "models.Profile") -> bool:
    finish_dt = profile.ultimate_finish_datetime

    if not finish_dt and profile.ultimate_activated:
        logger.warning("ultimate was not activated while finish_dt exists")
        profile.ultimate_activated = False
        profile.save()

    if not profile.ultimate_activated:
        return False

    return finish_dt > dt.datetime.now().replace(
        tzinfo=finish_dt.astimezone().tzinfo
    )


def get_ultimate_remaining_time(profile) -> int:
    if not check_ultimate_is_active(profile):
        return 0

    finish_dt = profile.ultimate_finish_datetime
    tz_info = finish_dt.astimezone().tzinfo

    time_remaining: dt.timedelta = finish_dt - dt.datetime.now().replace(
        tzinfo=tz_info
    )
    return time_remaining.seconds


def get_ultimate_finish_dt(ultimate_duration: int) -> dt.datetime:
    return dt.datetime.now() + dt.timedelta(seconds=ultimate_duration)
