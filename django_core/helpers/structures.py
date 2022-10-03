from typing import List, Tuple

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
        self.units_queryset: QuerySet[Unit] = Unit.objects.filter(lesson=self.lesson)
        self.first_unit: Unit = self.__get_first_unit(from_unit_id)
        self.__generate_blocking_units()
        self.__generate_additional_data()

    def __generate_additional_data(self):
        """
            Удобный метод для хранения необходимых данных юнитов без лишних прогонов
        """
        self.npc_id = None
        self.location_id = None

    def __generate_blocking_units(self):
        """ Генерация списка блокирующих элементов """
        self.block_units = [
            LessonBlockType.replica.value,  # A0
            LessonBlockType.email.value,  # A7
            LessonBlockType.a16_button.value,  # A16
        ]
        # Блокирующие блоки практических занятий
        self.block_units += [
            block_type for block_type in range(LessonBlockType.radios.value, LessonBlockType.comparison.value + 1)
        ]

    def __get_first_unit(self, from_unit_id: str | None) -> Unit:
        """ Получение начала юнитов по id или корневой юнит урока """
        if from_unit_id is None:
            entry_id = self.lesson.content.entry
            return self.units_queryset.filter(local_id=entry_id).first()

        return self.units_queryset.filter(local_id=from_unit_id).first()

    def __check_is_blocking_unit(self, unit: Unit) -> bool:
        """ Проверка текущего юнита на принадлежность к блокирующим юнитам """
        return unit.type in self.block_units

    def __fill_additional_data(self, unit: Unit):
        """
            В процессе перебора всех юнитов находит первые вхождения необходимых параметров
        """
        unit_content: dict = unit.content

        # находим 1ое вхождение location в юнитах
        if self.location_id is None:
            location = unit_content.get("location", None)
            if location is not None:
                self.location_id = location
        # находим 1ое вхождение npc в юнитах
        if self.npc_id is None:
            npc_id = unit_content.get("npc", None)
            if npc_id is not None:
                self.npc_id = npc_id


    def __get_next_unit(self, unit: Unit) -> List[Unit]:
        """ Получение следующих юнитов относительно переданного юнита """

        # TODO: протетстить если до конца уйдет (не найдет блокирующий юнит)
        units_list = []
        for unit_id in unit.next:  # может быть больше 1 (реплики например)
            next_unit = self.units_queryset.get(local_id=unit_id)
            if self.__check_is_blocking_unit(next_unit):
                return []
            units_list.append(next_unit)
        return units_list

    def get_queryset(self) -> List[Unit]:
        """ Получение отсортированных юнитов от корня """
        current_unit = self.first_unit
        queryset = [current_unit]
        print(current_unit)
        while next_units := self.__get_next_unit(current_unit):
            # проверяем текущий unit на наличие доп информации
            self.__fill_additional_data(current_unit)
            # если 1 лист
            if len(next_units) == 1:
                queryset.append(next_units[0])
                current_unit = next_units[0]
            else:  # если 2 и более. Пример: реплики
                unit_content = current_unit.сontent
                for unit in next_units:
                    self.__fill_additional_data(unit)
                    # TODO: а так вообще работает?
                    unit_content["variants"] += unit.content
                    current_unit.content = unit_content
                    current_unit.save()
                queryset.append(current_unit)
                current_unit = self.__get_next_unit(next_units[0])

        # добавление блокирующего юнита
        queryset.append(Unit.objects.filter(local_id=queryset[-1].next[0]).first())
        return queryset

    def get_additional_data(self) -> Tuple[int, int]:
        """ Возвращает необходимые id первого вхождения параметров """
        return self.location_id, self.npc_id
