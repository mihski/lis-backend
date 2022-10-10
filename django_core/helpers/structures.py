from collections import defaultdict, deque
from functools import cached_property, lru_cache

from lessons.serializers import UnitDetailSerializer
from lessons.models import Unit, Lesson, Course, Quest, Branching
from lessons.structures import LessonBlockType


def generate_a18_data(units: list[Unit]) -> dict:
    return {'type': 218, 'content': {'variants': UnitDetailSerializer(units, many=True).data}}


class LessonUnitsNode:
    def __init__(self, unit: Unit, children: list['LessonUnitsNode'] = None):
        self.unit = unit
        self.local_id = unit.local_id
        self.type = unit.type
        self.is_task = str(self.type).startswith("3")
        self.children = set(children or [])

    def get_unit_data(self, hide_task_answers: bool = False):
        if self.unit.type != LessonBlockType.replica.value:
            unit_data = UnitDetailSerializer(self.unit).data
        else:
            unit_data = generate_a18_data([self.unit])

        if hide_task_answers:
            unit_data.get('content', {}).pop('correct', None)

        return unit_data

    def __eq__(self, other):
        return self.local_id == other.local_id

    def __hash__(self):
        return hash(self.local_id)


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
        self.tree_elements: dict[str, LessonUnitsNode] = {self.tree.local_id: self.tree}

        self._build_tree()

    def _build_tree(self):
        queue = [self.tree.local_id]
        visited = defaultdict(bool)
        i = 0

        while i < len(queue):
            node_local_id = queue[i]
            node = self.tree_elements[node_local_id]

            if visited[node_local_id]:
                i += 1
                continue

            visited[node_local_id] = True

            for child_local_id in self.m_units[node_local_id].next:
                if child_local_id not in self.tree_elements:
                    self.tree_elements[child_local_id] = LessonUnitsNode(self.m_units[child_local_id])

                child = self.tree_elements[child_local_id]

                node.children.add(child)
                queue.append(child_local_id)

            i += 1

    @lru_cache(maxsize=1)
    def make_lessons_queue(self, from_unit_id: str = None, hide_task_answers: bool = True) -> tuple[int, int, list[dict]]:
        first_location_id = first_npc_id = None
        node = self.tree_elements[from_unit_id or self.lesson.content.entry]
        queue = []

        while not queue or node:
            unit_data = node.get_unit_data()
            queue.append(unit_data)

            if len(queue) > 1 and node.type in self.block_units_type:
                break

            first_location_id = first_location_id or queue[-1].get('content', {}).get('location')
            first_npc_id = first_npc_id or queue[-1].get('content', {}).get('npc')

            if len(node.children) >= 2:
                replica_units = [child.unit for child in node.children]
                queue.append(generate_a18_data(replica_units))
                break

            node = list(node.children)[0] if node.children else None

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


CourseBlockType = Lesson | Quest | Branching


class CourseLessonNode:
    def __init__(self, course_block: CourseBlockType, children: list[CourseBlockType] = None):
        self.course_block = course_block
        self.local_id = course_block.local_id
        self.children = set(children or [])


class CourseLessonsTree:
    def __init__(self, course: Course) -> None:
        self.course = course

        self.lessons = list(Lesson.objects.filter(course=self.course, quest__isnull=True))
        self.quests = list(Quest.objects.filter(course=self.course))
        self.branchings = list(Branching.objects.filter(course=self.course))

        self.m_blocks = {
            **{lesson.local_id: lesson for lesson in self.lessons},
            **{quest.local_id: quest for quest in self.quests},
            **{branching.local_id: branching for branching in self.branchings},
        }

        self.tree = CourseLessonNode(self.m_blocks[self.course.entry])

        self._build_tree()

    def _build_tree(self) -> None:
        queue = [self.tree]
        i = 0

        while i < len(queue):
            node = queue[i]

            i += 1
