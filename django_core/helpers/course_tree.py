from functools import lru_cache

from accounts.models import Profile
from lessons.models import Lesson, Course, Quest, Branching, ProfileBranchingChoice
from lessons.structures import BranchingType, BlockType
from helpers.abstract_tree import AbstractNode, AbstractNodeTree


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
    def next_ids(self) -> list[str]:
        if self.is_branching:
            if self.course_block.type == BranchingType.profile_parameter.value:
                return list(self.course_block.content['next'].values())

            if self.course_block.type == BranchingType.one_from_n.value:
                return self.course_block.content['next']

            if self.course_block.type == BranchingType.six_from_n.value:
                return [self.course_block.content['next']]

        if not self.course_block.next or self.course_block.next == "-1":
            return []

        return [self.course_block.next]


class CourseLessonsTree(AbstractNodeTree):
    node_cls = CourseLessonNode
    tree_elements: dict[str, CourseLessonNode]
    tree: CourseLessonNode

    def __init__(
        self,
        entity: Course | Quest,
    ) -> None:
        self.entity = entity

        blocks: list[CourseBlockType] = []

        blocks.extend(list(entity.lessons.all()))
        blocks.extend(list(entity.branchings.all()))

        if isinstance(entity, Course):
            blocks.extend(list(entity.quests.all()))

        self.m_blocks = {block.local_id: block for block in blocks}

        super().__init__()

    def get_quest_number(self, profile: Profile, lesson: Lesson) -> int:
        course_map = self.get_map_for_profile(profile)
        quest_index = 0
        prev_quest_index = None

        for course_map_cell in course_map:
            if isinstance(course_map_cell, Lesson):
                if course_map_cell.quest is None or course_map_cell.quest != prev_quest_index:
                    quest_index += 1

                prev_quest_index = course_map_cell.quest

                if lesson.local_id == course_map_cell.local_id:
                    return quest_index

        return -1

    def get_lesson_number(self, profile: Profile, lesson: Lesson) -> int:
        course_map = self.get_map_for_profile(profile)
        lesson_index = 0

        for course_map_cell in course_map:
            if isinstance(course_map_cell, Lesson):
                lesson_index += 1

                if lesson.local_id == course_map_cell.local_id:
                    return lesson_index

        return -1

    def _get_first_element(self):
        return self.m_blocks[self.entity.entry]

    def _get_element_by_id(self, element_id: str):
        return self.m_blocks[element_id]

    @lru_cache
    def get_max_depth(self):
        stack = [self.tree.local_id]
        depth = 0

        while stack:
            node = self.tree_elements[stack[-1]]

            if isinstance(node.course_block, Quest):
                quest_tree = CourseLessonsTree(node.course_block)
                quest_depth = quest_tree.get_max_depth()
                depth += quest_depth
            elif isinstance(node.course_block, Lesson):
                depth += 1
            elif isinstance(node.course_block, Branching):
                if node.course_block.type == BranchingType.six_from_n.value:
                    depth += 6
                if node.course_block.type != BranchingType.profile_parameter.value:
                    depth += 1

            if not node.next_ids:
                break

            stack.append(node.next_ids[0])

        return depth

    @lru_cache
    def get_map_for_profile(self, profile: Profile) -> list[Lesson | Branching | None]:
        stack: list[str] = [self.tree.local_id]
        map_list: list[CourseBlockType | None] = []

        while stack:
            node = self.tree_elements[stack[-1]]

            if isinstance(node.course_block, Branching):
                branch_type = BranchingType(node.course_block.type)

                if branch_type == BranchingType.profile_parameter:
                    br_key = (
                        profile.gender
                        if node.course_block.content["parameter"] == 2
                        else profile.laboratory
                    )

                    stack.append(node.course_block.content['next'][br_key])
                    continue

                map_list.append(node.course_block)

                choose_branch = (
                    ProfileBranchingChoice.objects
                    .filter(profile=profile, branching=node.course_block)
                    .first()
                )

                if not choose_branch or not choose_branch.choose_local_id:
                    break

                stack.extend(choose_branch.choose_local_id.split(','))
                continue
            elif isinstance(node.course_block, Quest):
                quest_tree = CourseLessonsTree(node.course_block)
                map_list.extend(quest_tree.get_map_for_profile(profile))

                if not node.course_block.next:
                    break

                stack.append(node.course_block.next)
            else:
                map_list.append(node.course_block)

                if not node.next_ids:
                    break

                stack.append(node.next_ids[0])

        return map_list

    def get_active(self, profile: Profile) -> int:
        return 0
