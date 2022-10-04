from lessons.serializers import UnitSerializer
from lessons.models import Unit, Lesson
from lessons.structures import LessonBlockType


class LessonUnitsTree:
    """
        Класс, предоставляющий список юнитов конкретного урока
        в отсортированном и необходимом виде
    """
    def __init__(self, lesson: Lesson, from_unit_id: str = None) -> None:
        """
            Конструктор дерева юнитов урока
            :param queryset: конкретный урок
            :param from_unit_id: опциональный параметр, начальный unit
        """
        self.lesson: Lesson = lesson
        self.units = list(Unit.objects.filter(lesson=self.lesson))
        self.from_unit_id = from_unit_id
        self.m_units = {unit.local_id: unit for unit in self.units}

        self.npc_id = None
        self.location_id = None

        self.block_units_type = self._get_blocking_units()
        self.queue = []

        self._make_lessons_queue()

    def _get_blocking_units(self):
        """ Генерация списка блокирующих элементов """
        return [
            LessonBlockType.replica.value,  # A0
            LessonBlockType.email.value,  # A7
            LessonBlockType.a16_button.value,  # A16
            *range(LessonBlockType.radios.value, LessonBlockType.comparison.value + 1)
        ]

    def _make_lessons_queue(self):
        head = self.m_units[self.from_unit_id or self.lesson.content.entry]
        queue = []

        while head and head.type not in self.block_units_type:
            queue.append(UnitSerializer(head).data)

            self.npc_id = self.npc_id or queue[-1].get('npc')
            self.location_id = self.location_id or queue[-1].get('location')

            if len(head.next) >= 2:
                replica_units = [self.m_units[local_id] for local_id in head.next]
                queue.append({'type': 218, 'content': {
                    'variants': UnitSerializer(replica_units, many=True).data
                }})
                break

            if not head.next:
                break

            head = self.m_units[head.next[0]]

        self.queue = queue

    @property
    def data(self):
        return self.queue
