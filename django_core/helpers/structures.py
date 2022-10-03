import json
from typing import List

from django.db.models import QuerySet

from lessons.models import Unit, Lesson
from lessons.structures import LessonBlockType


class LessonUnitsTree:
    """
        Класс, предоставляющий список юнитов конкретного урока
        в отсортированном и необходимом виде
    """
    def __init__(self, lesson: QuerySet[Lesson], from_unit_id: str = None) -> None:
        """
            Конструктор дерева юнитов урока
            :param queryset: конкретный урок
            :param from_unit_id: опциональный параметр, начальный unit
        """
        self.lesson: Lesson = lesson.first()
        self.units_queryset: QuerySet[Unit] = Unit.objects.filter(lesson=lesson)
        self.first_unit: Unit = self.__get_first_unit(from_unit_id)
        self.__generate_blocking_units()

    def __generate_blocking_units(self):
        """ Генерация списка блокирующих элементов """
        self.block_units = [
            LessonBlockType.replica,  # A0
            LessonBlockType.email,  # A7
            LessonBlockType.a16_button,  # A16
        ]
        # Блокирующие блоки практических занятий
        self.block_units += [
            block_type for block_type in range(LessonBlockType.radios.value, LessonBlockType.comparison.value + 1)
        ]

    def __get_first_unit(self, from_unit_id: str | None) -> Unit:
        """ Получение начала юнитов по id или корневой юнит """
        first_unit = self.units_queryset.get_or_none(local_id=from_unit_id)  # todo: check None
        if first_unit is None:
            entry_id = self.lesson.content.entry
            return self.units_queryset.filter(local_id=entry_id).first()
        return first_unit

    def __check_is_blocking_unit(self, unit: Unit) -> bool:
        """ Проверка текущего юнита на принадлежность к блокирующим юнитам """
        return unit.type in self.block_units

    def __get_next_unit(self, unit: Unit) -> List[Unit]:
        """ Получение следующих юнитов относительно переданного юнита """
        units = json.loads(unit.next)  # может быть больше 1 (реплики например)
        units_list = []
        for unit_id in units:
            unit = self.units_queryset.get(local_id=unit_id)
            if self.__check_is_blocking_unit(unit):
                return []
            units_list.append(unit)
        return units_list

    def get_queryset(self) -> List[Unit]:
        current_unit = self.first_unit
        queryset = [current_unit]

        while next_units := self.__get_next_unit(current_unit):
            if len(next_units) == 1:
                queryset.append(next_units[0])
            else:  # 2 и более. Пример: реплики
                unit_content = json.loads(current_unit.сontent)
                unit_content["variants"] += [json.loads(x.content) for x in next_units]  # content
                current_unit.content = unit_content

            current_unit = next_units[0]
        return queryset
