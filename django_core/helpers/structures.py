from collections import defaultdict, deque
from functools import cached_property, lru_cache

from lessons.serializers import UnitSerializer
from lessons.models import Unit, Lesson
from lessons.structures import LessonBlockType


class LessonUnitsNode:
    def __init__(self, unit: Unit, children: list['LessonUnitsNode'] = None):
        self.unit = unit
        self.local_id = unit.local_id
        self.type = unit.type
        self.is_task = str(self.type).startswith("3")
        self.children = children or []


class LessonUnitsTree:
    """
        Класс, предоставляющий список юнитов конкретного урока
        в отсортированном и необходимом виде
    """
    def __init__(self, lesson: Lesson) -> None:
        """
            Конструктор дерева юнитов урока
            :param queryset: конкретный урок
            :param from_unit_id: опциональный параметр, начальный unit
        """
        self.lesson: Lesson = lesson
        self.units = list(Unit.objects.filter(lesson=self.lesson))
        self.m_units = {unit.local_id: unit for unit in self.units}

        self.block_units_type = [
            LessonBlockType.replica.value,
            LessonBlockType.email.value,
            LessonBlockType.a16_button.value,
            *range(LessonBlockType.radios.value, LessonBlockType.comparison.value + 1)
        ]

        self.tree: LessonUnitsNode = LessonUnitsNode(self.m_units[self.lesson.content.entry])
        self.tree_elements: dict[str, LessonUnitsNode] = {}

        self._build_tree()

    def _build_tree(self):
        queue = [self.tree]
        visited = defaultdict(bool)
        i = 0

        while i < len(queue):
            node = queue[i]

            if visited[node.local_id]:
                i += 1
                continue

            visited[node.local_id] = True
            self.tree_elements[node.local_id] = node

            for local_id in self.m_units[node.local_id].next:
                child_node = LessonUnitsNode(self.m_units[local_id])
                node.children.append(child_node)
                queue.append(child_node)

            i += 1

    @lru_cache(maxsize=1)
    def make_lessons_queue(self, from_unit_id: str = None) -> tuple[int, int, list[dict]]:
        first_location_id = first_npc_id = None
        node = self.tree_elements[from_unit_id or self.lesson.content.entry]
        queue = []

        while not queue or node:
            queue.append(UnitSerializer(node.unit).data)

            if len(queue) > 1 and node.type in self.block_units_type:
                break

            first_location_id = first_location_id or queue[-1].get('content', {}).get('location')
            first_npc_id = first_npc_id or queue[-1].get('content', {}).get('npc')

            if len(node.children) >= 2:
                replica_units = [child.unit for child in node.children]
                queue.append({'type': 218, 'variants': UnitSerializer(replica_units, many=True).data})
                break

            node = node.children[0] if node.children else None

        if from_unit_id:
            # except pointed
            queue = queue[1:]

        return first_location_id, first_npc_id, queue

    @cached_property
    def task_count(self):
        stack = deque([self.tree])
        visited = defaultdict(bool)

        max_task_count = 0
        current_task_count = 0

        while stack:
            node = stack[-1]
            visited[node.local_id] = True

            current_task_count += node.is_task
            max_task_count = max(current_task_count, max_task_count)

            has_next_child = False
            for child in node.children:
                if not visited[child.local_id]:
                    stack.append(child)
                    has_next_child = True
                    break

            if not has_next_child:
                current_task_count -= stack.pop().is_task

        return max_task_count
