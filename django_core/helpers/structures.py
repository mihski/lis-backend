from abc import ABC, abstractmethod
from collections import defaultdict, deque
from functools import cached_property, lru_cache

from lessons.serializers import UnitDetailSerializer
from lessons.models import Unit, Lesson, Course, Quest, Branching
from lessons.structures import LessonBlockType, BranchingType


class AbstractNode(ABC):
    children: set['AbstractNode']

    @abstractmethod
    def obj(self):
        pass

    @abstractmethod
    def id(self):
        pass

    @abstractmethod
    def next_ids(self):
        pass


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


class AbstractNodeTree(ABC):
    node_cls = None

    def __init__(self):
        self.tree = self.node_cls(self._get_first_element())
        self.tree_elements: dict[str, AbstractNode] = {self.tree.id: self.tree}
        self._build_tree()

    @abstractmethod
    def _get_first_element(self):
        pass

    @abstractmethod
    def _get_element_by_id(self, element_id: str):
        pass

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

            for child_local_id in node.next_ids:
                if child_local_id not in self.tree_elements:
                    self.tree_elements[child_local_id] = self.node_cls(
                        self._get_element_by_id(child_local_id)
                    )

                child = self.tree_elements[child_local_id]

                node.children.add(child)
                queue.append(child_local_id)

            i += 1


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
        return self._get_element_by_id(self.lesson.content.entry)

    def _get_element_by_id(self, element_id: str):
        return self.m_units[element_id]

    def _generate_a18(self, units: list[Unit]) -> dict:
        return {'type': 218, 'content': {'variants': UnitDetailSerializer(units, many=True).data}}

    @lru_cache(maxsize=1)
    def make_lessons_queue(self, from_unit_id: str = None) -> tuple[int, int, list[dict]]:
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


class CourseLessonNode(AbstractNode):
    def __init__(self, course_block: CourseBlockType, children: list['CourseLessonNode'] = None):
        self.course_block = course_block
        self.local_id = course_block.local_id
        self.children = set(children or [])

        self.is_branching = isinstance(self.course_block, Branching)

    @property
    def obj(self):
        return self.course_block

    @property
    def id(self):
        return self.local_id

    @property
    def next_ids(self):
        if self.is_branching:
            if self.course_block.type == BranchingType.gender.value:
                return self.course_block.content['next'].values()

            if self.course_block.type == BranchingType.six_from_n.value:
                return [self.course_block.content['next']]

            if self.course_block.type == BranchingType.one_from_n.value:
                return self.course_block.content['next']

        return self.course_block.next


class CourseLessonsTree(AbstractNodeTree):
    node_cls = CourseLessonNode
    tree_elements: dict[str, CourseLessonNode]

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

        super().__init__()

    def get_quest_number(self, lesson: Lesson) -> int:
        queue = [(0, self.tree)]  # quest_number, node
        visited = defaultdict(bool)

        i = 0

        while i < len(queue):
            quest_number, node = queue[i]

            if visited[node.id]:
                i += 1
                continue

            for child_local_id in node.next_ids:
                queue.append((quest_number + int(not node.is_branching), self._get_element_by_id(child_local_id)))

            i += 1

    def get_lesson_number(self, lesson: Lesson) -> int:
        return 0

    def _get_first_element(self):
        return self.m_blocks[self.course.entry]

    def _get_element_by_id(self, element_id: str):
        return self.m_blocks[element_id]