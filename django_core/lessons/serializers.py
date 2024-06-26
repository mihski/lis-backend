import datetime as dt
from functools import lru_cache

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import Sum
from django.db import transaction

from accounts.models import Profile
from lessons.models import (
    NPC,
    Location,
    Lesson,
    Unit,
    Course,
    Branching,
    CourseMapImg,
    ProfileBranchingChoice,
    Quest,
    Review,
    Question,
    UnitAffect,
    EmailTypes,
    ProfileCourseDone,
    ProfileLessonDone,
    ProfileLesson,
    ProfileLessonChunk
)
from lessons.structures import (
    BlockType,
    BranchingType,
    BranchingViewType
)
from lessons.structures.tasks import TaskBlock
from lessons.utils import process_affect
from lessons.exceptions import (
    BranchingAlreadyChosenException,
    BlockNotFoundException,
    NotEnoughBlocksToSelectBranchException
)
from helpers.course_tree import CourseLessonsTree
from resources.exceptions import NotEnoughMoneyException
from resources.serializers import EmotionDataSerializer
from resources.utils import get_salary_by_position

User = get_user_model()


class NPCSerializer(serializers.ModelSerializer):
    change_cost = serializers.IntegerField(read_only=True, default=settings.CHANGE_SCIENTIFIC_DIRECTOR_ENERGY_COST)

    class Meta:
        model = NPC
        fields = "__all__"


class LocationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class UnitAffectSerializer(serializers.ModelSerializer):
    method = serializers.CharField(default="PUT")

    class Meta:
        model = UnitAffect
        fields = ["code", "api_path", "method", "body"]


class UnitDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="local_id")
    content = serializers.SerializerMethodField()

    def get_content(self, unit: Unit) -> dict:
        if not (300 <= unit.type < 400):
            return unit.content

        task_models = {t_model.type.value: t_model for t_model in TaskBlock.get_all_subclasses()}
        task_model = task_models[unit.type]

        task_instance: TaskBlock = task_model.objects.filter(id=unit.content["id"]).only().first()
        task_instance.shuffle_content(unit.content)

        # возвращаем correct только для T2
        if "correct" in unit.content and unit.type != 302:
            unit.content.pop("correct")

        return unit.content

    class Meta:
        model = Unit
        fields = ["id", "type", "content"]


class LessonDetailSerializer(serializers.ModelSerializer):
    lesson_name = serializers.CharField(source="name")
    lesson_number = serializers.IntegerField(default=0)
    quest_number = serializers.IntegerField(default=0)
    tasks = serializers.IntegerField(default=0)
    bonuses = serializers.SerializerMethodField()

    def get_bonuses(self, lesson: Lesson) -> dict:
        if self.context.get("finished", False):
            return {"energy": 0, "money": 0}

        profile = self.context["request"].user.profile.get()

        if not profile.scientific_director_id:
            return {"energy": 0, "money": 0}

        scientific_director_id = profile.scientific_director.uid[1:]

        return lesson.bonuses[scientific_director_id]

    class Meta:
        model = Lesson
        fields = ["lesson_name", "lesson_number", "quest_number", "tasks", "bonuses"]


class LessonChoiceSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="local_id")
    type = serializers.ReadOnlyField(default="lesson")

    class Meta:
        model = Lesson
        fields = ["id", "type", "name", "description", "money_cost"]


class QuestChoiceSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="local_id")
    type = serializers.ReadOnlyField(default="quest")
    lessons = serializers.SerializerMethodField()
    money_cost = serializers.SerializerMethodField()

    def get_money_cost(self, quest: Quest) -> int:
        quest_tree = CourseLessonsTree(quest)
        profile = self.context['request'].user.profile.get(course_id=1)
        map_list = quest_tree.get_map_for_profile(profile)
        return sum([l.money_cost for l in map_list if isinstance(l, Lesson)])

    def get_lessons(self, obj: Quest) -> dict:
        quest_tree = CourseLessonsTree(obj)
        profile = self.context['request'].user.profile.get(course_id=1)
        lessons = quest_tree.get_map_for_profile(profile)
        return LessonChoiceSerializer(lessons, many=True).data

    class Meta:
        model = Quest
        fields = ["id", "type", "money_cost", "name", "description", "lessons"]


class CourseMapCell(serializers.ModelSerializer):
    MAP_CELL_TYPES = (
        (BlockType.lesson, "Урок"),
        (BlockType.branching, "Ветвление"),
        (BlockType.img, "Изображение"),
    )

    id = serializers.CharField(source="local_id")
    type = serializers.ChoiceField(choices=MAP_CELL_TYPES)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CourseMapLessonCell(CourseMapCell):
    name = serializers.CharField()
    type = serializers.ReadOnlyField(default=BlockType.lesson.value)
    quest = serializers.SerializerMethodField()
    energy_cost = serializers.IntegerField()

    class Meta:
        model = Lesson
        fields = ["id", "name", "type", "quest", "energy_cost"]

    def get_quest(self, obj: Lesson) -> dict:
        if not obj.quest:
            return {}

        return {"id": obj.quest.local_id, "name": obj.quest.name}


class CourseMapBranchingCell(CourseMapCell):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["type"] = BlockType.branching.value
        return data

    class Meta:
        model = Branching
        fields = ["id", "type"]


class CourseMapImgCell(CourseMapCell):
    type = serializers.ReadOnlyField(default=BlockType.img.value)
    image = serializers.SerializerMethodField()
    image_disabled = serializers.SerializerMethodField()

    def _get_absolute_url(self, photo_url: str) -> str:
        request = self.context.get('request')
        return request.build_absolute_uri(photo_url)

    def get_image(self, map_cell: CourseMapImg) -> str:
        return self._get_absolute_url(map_cell.image.url)

    def get_image_disabled(self, map_cell: CourseMapImg) -> str:
        return self._get_absolute_url(map_cell.image_disabled.url)

    class Meta:
        model = CourseMapImg
        fields = ["type", "image", "image_disabled"]


class BranchingDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="local_id")
    choices = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    locale = serializers.SerializerMethodField()

    def get_locale(self, obj: Branching) -> dict:
        return obj.course.locale

    def get_type(self, obj: Branching):
        if obj.type == BranchingType.profile_parameter.value:
            return BranchingViewType.parameter.value
        elif obj.type == BranchingType.six_from_n.value:
            return BranchingViewType.m_from_n.value

        quests = Quest.objects.filter(local_id__in=obj.content["next"])

        if quests.count() == len(obj.content["next"]):
            return BranchingViewType.fork.value

        return BranchingViewType.lessons_fork.value

    def get_choices(self, obj: Branching) -> None:
        lesson_local_ids = []

        if obj.type == BranchingType.six_from_n.value:
            lesson_local_ids.extend(obj.content['list'])

        if obj.type == BranchingType.one_from_n.value:
            lesson_local_ids.extend(obj.content['next'])

        lessons_data = LessonChoiceSerializer(
            Lesson.objects.filter(local_id__in=lesson_local_ids), many=True
        ).data
        quests_data = QuestChoiceSerializer(
            Quest.objects
            .filter(local_id__in=lesson_local_ids)
            .prefetch_related("lessons"),
            many=True,
            context=self.context
        ).data

        return lessons_data + quests_data

    class Meta:
        model = Branching
        fields = ["id", "choices", "type", "locale"]


class BranchingSelectSerializer(serializers.ModelSerializer):
    choose_local_id = serializers.CharField(write_only=True)

    class Meta:
        model = Branching
        fields = ["choose_local_id"]

    @lru_cache
    def _get_blocks(self, local_ids: str) -> list[Lesson | Quest]:
        blocks = [
            *(
                Lesson.objects.filter(quest__isnull=True, local_id__in=local_ids.split(","))
                .select_related("profile_affect")
            ),
            *(
                Quest.objects.filter(local_id__in=local_ids.split(","))
                .prefetch_related("lessons", "branchings")
            ),
        ]
        return blocks

    def validate_choose_local_id(self, choose_local_id: str) -> str:
        local_ids = ",".join(list(map(lambda x: x.strip(), choose_local_id.split(","))))
        blocks = self._get_blocks(local_ids)
        blocks_local_ids = [b.local_id for b in blocks]

        unexist_local_ids = set(local_ids.split(",")) - set(blocks_local_ids)

        if unexist_local_ids:
            raise BlockNotFoundException(f"There is no block on course with local_id: {unexist_local_ids}")

        return local_ids

    def validate(self, validated_data: dict) -> dict:
        profile: Profile = self.context["request"].user.profile.get(course_id=1)
        blocks = self._get_blocks(validated_data['choose_local_id'])

        if self.instance.type == BranchingType.one_from_n.value:
            if len(blocks) != 1:
                raise NotEnoughBlocksToSelectBranchException("There is no one lessons")

        elif self.instance.type == BranchingType.six_from_n.value:
            block_counts = sum([
                len(CourseLessonsTree(block).get_map_for_profile(profile)) if isinstance(block, Quest)
                else 1
                for block in blocks
            ])

            if block_counts != 6:
                raise NotEnoughBlocksToSelectBranchException("There is no exact six lessons")

        return validated_data

    def _process_callbacks(self, blocks: list[Lesson | Quest], profile: Profile) -> None:
        for block in blocks:
            if not isinstance(block, Lesson):
                continue
            process_affect(block.profile_affect, profile)

    def _collect_quest_price(self, quest: Quest) -> int:
        quest_tree = CourseLessonsTree(quest)
        profile = self.context['request'].user.profile.get(course_id=1)
        map_list = quest_tree.get_map_for_profile(profile)
        return sum([l.money_cost for l in map_list if isinstance(l, Lesson)])

    def _get_blocks_total_price(self, blocks: list[Quest | Lesson]) -> int:
        total_lessons_price = 0
        for block in blocks:
            total_lessons_price += (
                self._collect_quest_price(block) if isinstance(block, Quest)
                else block.money_cost
            )
        return total_lessons_price

    def update(self, branching: Branching, validated_data: dict) -> Branching:
        profile: Profile = self.context["request"].user.profile.get(course_id=1)
        choose_local_id = validated_data["choose_local_id"]

        profile_branching = ProfileBranchingChoice.objects.filter(profile=profile, branching=branching)
        if profile_branching.exists():
            raise BranchingAlreadyChosenException("You have already selected this branching")

        local_ids = ",".join(list(map(lambda x: x.strip(), choose_local_id.split(","))))
        blocks = self._get_blocks(local_ids)

        profile_resources = profile.resources
        branching_price = self._get_blocks_total_price(blocks)
        if profile_resources.money_amount < branching_price:
            raise NotEnoughMoneyException("Not enough money to select this branching")

        with transaction.atomic():
            profile_resources.money_amount -= branching_price
            profile_resources.save()

            profile_branching = ProfileBranchingChoice.objects.create(profile=profile, branching=branching)
            profile_branching.choose_local_id = choose_local_id
            profile_branching.save()

        self._process_callbacks(blocks, profile)
        return branching


class CourseMapSerializer(serializers.ModelSerializer):
    map = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()
    locales = serializers.JSONField(source="locale")

    class Meta:
        model = Course
        fields = ["map", "active", "locales"]

    def get_map(self, obj: Course) -> list[dict]:
        model_to_serializer = {
            Lesson: CourseMapLessonCell,
            Branching: CourseMapBranchingCell,
        }

        profile: Profile = self.context['request'].user.profile.get(course_id=1)
        tree = CourseLessonsTree(obj)

        map_list = tree.get_map_for_profile(profile)

        course_map_images = CourseMapImg.objects.filter(course=obj).all()
        course_map_images_data = CourseMapImgCell(course_map_images, many=True, context=self.context).data
        serialized_map_list = [None] * (tree.get_max_depth() + len(course_map_images))

        for course_map, course_map_data in zip(course_map_images, course_map_images_data):
            if course_map.order <= len(serialized_map_list) and not serialized_map_list[course_map.order]:
                serialized_map_list[course_map.order] = course_map_data

        j = 0
        for obj in map_list:
            while j < len(serialized_map_list) and serialized_map_list[j] is not None:
                j += 1
            # FIXME: Почему-то иногда j выходит за пределы массива
            try:
                serialized_map_list[j] = model_to_serializer[obj.__class__](obj).data
            except IndexError:
                serialized_map_list.append(model_to_serializer[obj.__class__](obj).data)

        return serialized_map_list

    def get_active(self, obj: Course) -> int:
        profile: Profile = self.context['request'].user.profile.get(course_id=1)
        tree = CourseLessonsTree(obj)
        active_block_index = tree.get_active(profile)
        return active_block_index


class CourseNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all(),
    )
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course"
    )
    mail_type = serializers.ChoiceField(
        choices=EmailTypes.choices,
        default=EmailTypes.CONTENT
    )

    class Meta:
        model = Review
        fields = ["text", "course_id", "user", "mail_type"]


class QuestionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all()
    )
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course"
    )

    class Meta:
        model = Question
        fields = ["text", "course_id", "user"]


class LessonFinishSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="local_id")
    next_id = serializers.SerializerMethodField()
    next_type = serializers.SerializerMethodField()
    salary_amount = serializers.SerializerMethodField()

    emotion = EmotionDataSerializer(write_only=True)
    duration = serializers.IntegerField(write_only=True)

    @lru_cache
    def get_next_obj(self, lesson: Lesson):
        course_map = CourseLessonsTree(lesson.course)
        profile = self.context["profile"]
        map_list = course_map.get_map_for_profile(profile)

        for i, block in enumerate(map_list):
            if i + 1 < len(map_list) and block.local_id == lesson.local_id:
                return map_list[i + 1]

    def get_salary_amount(self, lesson: Lesson) -> int:
        salary_amount = 0

        if not lesson.profile_affect:
            next_obj = self.get_next_obj(lesson)

            if isinstance(next_obj, Branching) and next_obj.type != 2:
                salary_amount = get_salary_by_position(self.context["profile"].university_position)

            return salary_amount

        if "amount" not in lesson.profile_affect.content:
            return salary_amount

        salary_amount = lesson.profile_affect.content["amount"]

        if not isinstance(salary_amount, int):
            salary_amount = get_salary_by_position(self.context["profile"].university_position)

        return salary_amount

    def get_next_type(self, lesson: Lesson) -> int:
        next_obj = self.get_next_obj(lesson)

        if isinstance(next_obj, Lesson):
            return BlockType.lesson.value

        return BlockType.branching.value

    def get_next_id(self, lesson: Lesson) -> str:
        next_obj = self.get_next_obj(lesson)

        if next_obj:
            return next_obj.local_id

        return ""

    def validate(self, validated_data):
        validated_data.pop("emotion")
        validated_data.pop("duration")

        return validated_data

    class Meta:
        model = Lesson
        fields = ["id", "next_id", "next_type", "salary_amount", "emotion", "duration"]


class ProfileCourseFinishedSerializer(serializers.ModelSerializer):
    isu = serializers.CharField(source="profile.isu", read_only=True)
    username = serializers.CharField(source="profile.username", read_only=True)
    finished_at = serializers.SerializerMethodField(source="finished_at")

    def get_finished_at(self, instance: ProfileCourseDone) -> str:
        return instance.finished_at.strftime("%d.%m.%Y")

    class Meta:
        model = ProfileCourseDone
        fields = ["isu", "username", "finished_at"]


class ProfileLessonSerializer(serializers.ModelSerializer):
    local_id = serializers.CharField()

    name = serializers.CharField()
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    timeCost = serializers.IntegerField(source='time_cost')
    moneyCost = serializers.IntegerField(source='money_cost')
    energyCost = serializers.IntegerField(source='energy_cost')
    has_bonuses = serializers.BooleanField(default=False)
    bonuses = serializers.JSONField()

    next = serializers.CharField(allow_blank=True)
    unit_count = serializers.SerializerMethodField()

    done = serializers.SerializerMethodField()

    def get_unit_count(self, lesson: Lesson) -> int:
        return lesson.unit_set.count()

    def get_bonuses(self, lesson: Lesson) -> dict:
        if self.context.get("finished", False):
            return {"energy": 0, "money": 0}

        profile = self.context["request"].user.profile.get()

        if not profile.scientific_director_id:
            return {"energy": 0, "money": 0}

        scientific_director_id = profile.scientific_director.uid[1:]

        return lesson.bonuses[scientific_director_id]

    def get_done(self, lesson: Lesson) -> bool:

        profile = self.context['request'].user.profile.get()
        lesson_done = ProfileLessonDone.objects.filter(profile=profile, lesson=lesson).first()
        if lesson_done:
            return True
        return False

    class Meta:

        model = Lesson
        fields = [
            'id',
            'local_id',
            'course',
            'quest',
            'name',
            'timeCost',
            'moneyCost',
            'energyCost',
            'bonuses',
            'next',
            'has_bonuses',
            'x',
            'y',
            'unit_count',
            'done'
        ]


class ProfileBranchingSerializer(serializers.ModelSerializer):
    local_id = serializers.CharField()
    selected = serializers.SerializerMethodField()

    # TODO: добавить два типа бранчей

    def get_selected(self, branching: Branching) -> bool:
        profile = self.context['request'].user.profile.get()

        if branching.type in (2, 3):
            branching_choice = ProfileBranchingChoice.objects.filter(profile=profile, branching=branching).first()
            if branching_choice:
                return branching_choice.choose_local_id

            return False

        if branching.content['parameter'] == 2:

            return branching.content['next'][profile.gender]
        if branching.content['parameter'] == 1:
            return branching.content['next'][profile.laboratory]


    class Meta:
        ordering = ['id']
        model = Branching
        fields = ['id', 'local_id', 'course', 'quest', 'x', 'y', 'type', 'content', 'selected']


class ProfileQuestSerializer(serializers.ModelSerializer):
    local_id = serializers.CharField()

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    lessons = ProfileLessonSerializer(many=True)
    branchings = ProfileBranchingSerializer(required=False, many=True)

    description = serializers.CharField()
    entry = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    next = serializers.CharField(allow_blank=True)

    class Meta:
        model = Quest
        fields = [
            'id',
            'local_id',
            'name',
            'course',
            'lessons',
            'branchings',
            'description',
            'entry',
            'next',
            'x',
            'y',
        ]


class NewCourseMapSerializer(serializers.ModelSerializer):
    lessons = ProfileLessonSerializer(required=False, many=True)
    quests = ProfileQuestSerializer(required=False, many=True)
    branchings = ProfileBranchingSerializer(required=False, many=True)

    name = serializers.CharField()
    description = serializers.CharField()
    entry = serializers.CharField(required=False, allow_blank=True)
    locale = serializers.JSONField(required=False)

    class Meta:
        model = Course
        fields = ['id', 'lessons', 'quests', 'branchings', 'name', 'description', 'entry', 'locale', 'is_editable']


class SavedProfileLessonChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileLessonChunk
        ordering = ['id']
        fields = ['unit_id', 'type', 'content']


class SavedProfileLessonSerializer(serializers.ModelSerializer):
    chunk = serializers.SerializerMethodField()

    class Meta:
        model = ProfileLesson
        fields = ['id', 'location', 'npc', 'lesson_name', 'lesson_number', 'quest_number', 'locales', 'chunk']

    def get_chunk(self, obj):
        sorted_chunks = obj.chunk.order_by('id')
        serializer = SavedProfileLessonChunkSerializer(sorted_chunks, many=True)

        return serializer.data
    
class CourselistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
     #   fields  = "__all__"
        exclude =[ "locale"]


class CourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model =Course
        fields = "__all__"
                

    


