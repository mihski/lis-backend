from accounts.models import UniversityPosition

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
