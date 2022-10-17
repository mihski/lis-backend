from collections import defaultdict, deque, namedtuple
from functools import cached_property, lru_cache

from lessons.serializers import UnitDetailSerializer
from lessons.models import Unit, Lesson
from lessons.structures import LessonBlockType
from helpers.abstract_tree import AbstractNode, AbstractNodeTree


class LessonUnitsNode(AbstractNode):
    def __init__(self, unit: Unit, children: list['LessonUnitsNode'] = None):
        self.unit = unit
        self.local_id = unit.local_id
        self.type = unit.type
        self.is_task = str(self.type).startswith("3")
        self.children = set(children or [])

    @property
    def id(self):
        return self.local_id

    @property
    def next_ids(self):
        return self.unit.next

    @property
    def obj(self):
        return self.unit

    def __eq__(self, other):
        return self.local_id == other.local_id

    def __hash__(self):
        return hash(self.local_id)


class LessonUnitsTree(AbstractNodeTree):
    """
        Класс, предоставляющий список юнитов конкретного урока
        в отсортированном и необходимом виде
    """
    node_cls = LessonUnitsNode
    tree_elements: dict[str, LessonUnitsNode]

    def __init__(self, lesson: Lesson) -> None:
        self.lesson: Lesson = lesson
        self.units = list(Unit.objects.filter(lesson=self.lesson))
        self.m_units = {unit.local_id: unit for unit in self.units}

        self.block_units_type = [
            LessonBlockType.replica.value,
            LessonBlockType.email.value,
            LessonBlockType.a16_button.value,
            *range(LessonBlockType.radios.value, LessonBlockType.comparison.value + 1)
        ]

        super().__init__()

    def _get_first_element(self):
        if self.lesson.content.entry:
            return self._get_element_by_id(self.lesson.content.entry)

        return namedtuple('Unit', ('local_id', 'type', 'next'))(-1, 0, [])

    def _get_element_by_id(self, element_id: str):
        return self.m_units[element_id]

    def _generate_a18(self, units: list[Unit]) -> dict:
        return {'type': 218, 'content': {'variants': UnitDetailSerializer(units, many=True).data}}

    @lru_cache(maxsize=1)
    def make_lessons_queue(self, from_unit_id: str = None, hide_task_answers: bool = False) -> tuple[int, int, list[dict]]:
        if not self.lesson.content.entry:
            return -1, -1, []

        first_location_id = first_npc_id = None
        node = self.tree_elements[from_unit_id or self.lesson.content.entry]
        queue = []

        while not queue or node:
            if node.type != LessonBlockType.replica.value:
                unit_data = UnitDetailSerializer(node.unit).data
            else:
                unit_data = self._generate_a18([node.unit])

            queue.append(unit_data)

            if len(queue) > 1 and node.type in self.block_units_type:
                break

            first_location_id = first_location_id or queue[-1].get('content', {}).get('location')
            first_npc_id = first_npc_id or queue[-1].get('content', {}).get('npc')

            if len(node.children) >= 2:
                replica_units = [child.obj for child in node.children]
                queue.append(self._generate_a18(replica_units))
                break

            node = list(node.children)[0] if node.children else None

        if from_unit_id:
            # except pointed
            queue = queue[1:]

        return first_location_id, first_npc_id, queue

    @cached_property
    def task_count(self):
        if not self.lesson.content.entry:
            return 0

        stack = deque([self.tree])
        visited = defaultdict(bool)

        max_task_count = 0
        current_task_count = 0

        while stack:
            node = stack[-1]
            visited[node.local_id] = True

            has_next_child = False
            for child in node.children:
                if not visited[child.local_id]:
                    current_task_count += child.is_task
                    max_task_count = max(current_task_count, max_task_count)
                    stack.append(child)
                    has_next_child = True
                    break

            if not has_next_child:
                current_task_count -= stack.pop().is_task

        return max_task_count
