from django.db import models

PROFILE_GENDER = (
    ("male", "Мужской"),
    ("female", "Женский"),
)


LABORATORIES = (
    ("it", "IT"),
    ("ls", "Науки о жизни"),
    ("mi", "Менеджмент и инновации"),
    ("ctm", "Компьютерные технологии и управления"),
    ("pts", "Физико-технические науки"),
)

LANGUAGES = (
    ("ru", "RU"),
    ("en", "EN")
)

class UniversityPosition(models.TextChoices):
    """
        Роль персонажа в университете
    """
    STUDENT = "Студент"
    INTERN = "Стажер"
    LABORATORY_ASSISTANT = "Лаборант"
    ENGINEER = "Инженер"
    JUN_RESEARCH_ASSISTANT = "Мл. научный сотрудник"
