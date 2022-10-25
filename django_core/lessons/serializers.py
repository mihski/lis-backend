from functools import lru_cache

from rest_framework import serializers, validators
from django.contrib.auth import get_user_model

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
    EmailTypes
)
from lessons.structures import BlockType, BranchingType, BranchingViewType, LessonBlockType
from lessons.structures.tasks import TaskBlock
from lessons.utils import process_affect
from helpers.course_tree import CourseLessonsTree

User = get_user_model()


class NPCSerializer(serializers.ModelSerializer):
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

        return unit.content

    class Meta:
        model = Unit
        fields = ["id", "type", "content"]


class LessonDetailSerializer(serializers.ModelSerializer):
    # TODO: переделать
    lesson_name = serializers.CharField(source="name")
    lesson_number = serializers.IntegerField(default=0)
    quest_number = serializers.IntegerField(default=0)
    tasks = serializers.IntegerField(default=0)

    class Meta:
        model = Lesson
        fields = ["lesson_name", "lesson_number", "quest_number", "tasks"]


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
        return sum([l.money_cost for l in quest.lessons.all()])

    def get_lessons(self, obj: Course) -> dict:
        quest_tree = CourseLessonsTree(obj)

        profile = Profile.objects.get(user=self.context['request'].user)
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
        return self._get_absolute_url(map_cell.image.url)

    class Meta:
        model = CourseMapImg
        fields = ["type", "image", "image_disabled"]


class BranchingDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="local_id")
    choices = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

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
        fields = ["id", "choices", "type"]


class BranchingSelectSerializer(serializers.ModelSerializer):
    choose_local_id = serializers.CharField(write_only=True)

    class Meta:
        model = Branching
        fields = ["choose_local_id"]

    @lru_cache
    def _get_blocks(self, local_ids: str) -> list[Lesson | Quest]:
        blocks = [
            *Lesson.objects.filter(quest__isnull=True, local_id__in=local_ids.split(",")),
            *Quest.objects.filter(local_id__in=local_ids.split(",")),
        ]
        return blocks

    def validate_choose_local_id(self, choose_local_id: str) -> str:
        local_ids = ",".join(list(map(lambda x: x.strip(), choose_local_id.split(","))))
        blocks = self._get_blocks(local_ids)
        blocks_local_ids = [b.local_id for b in blocks]

        unexist_local_ids = set(local_ids.split(",")) - set(blocks_local_ids)

        if unexist_local_ids:
            raise validators.ValidationError(f"There is no block on course with local_id: {unexist_local_ids}")

        return local_ids

    def validate(self, validated_data: dict) -> dict:
        profile = Profile.objects.get(user=self.context["request"].user)
        blocks = self._get_blocks(validated_data['choose_local_id'])

        if self.instance.type == BranchingType.one_from_n.value:
            if len(blocks) != 1:
                raise validators.ValidationError("There is no one lessons")

        elif self.instance.type == BranchingType.six_from_n.value:
            block_counts = sum([
                len(CourseLessonsTree(block).get_map_for_profile(profile))
                if isinstance(block, Quest)
                else 1
                for block in blocks
            ])

            if block_counts != 6:
                raise validators.ValidationError("There is no exact six lessons")

        return validated_data

    def _process_callbacks(self, choose_local_id: str, profile: Profile) -> None:
        lessons = Lesson.objects.filter(local_id__in=choose_local_id.split(","))
        for lesson in lessons:
            process_affect(lesson.profile_affect, profile)

    def update(self, branching, validated_data):
        profile = Profile.objects.get(user=self.context["request"].user)
        choice_branching, created = ProfileBranchingChoice.objects.get_or_create(profile=profile, branching=branching)
        choice_branching.choose_local_id = validated_data["choose_local_id"]
        choice_branching.save()

        self._process_callbacks(choice_branching.choose_local_id, profile)

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

        profile = Profile.objects.get(user=self.context['request'].user)
        tree = CourseLessonsTree(obj)

        map_list = tree.get_map_for_profile(profile)

        course_map_images = CourseMapImg.objects.filter(course=obj).all()

        serialized_map_list = [None] * (tree.get_max_depth() + len(course_map_images))

        for course_map in course_map_images:
            serialized_map_list[course_map.order] = CourseMapImgCell(
                course_map,
                context=self.context
            ).data

        j = 0
        for obj in map_list:
            while j < len(serialized_map_list) and serialized_map_list[j] is not None:
                j += 1

            serialized_map_list[j] = model_to_serializer[obj.__class__](obj).data

        return serialized_map_list

    def get_active(self, obj: Course) -> int:
        profile = Profile.objects.get(user=self.context['request'].user)
        tree = CourseLessonsTree(obj)
        return tree.get_active(profile)


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

    def get_next_id(self, lesson: Lesson):
        course_map = CourseLessonsTree(lesson.course)
        profile = self.context["profile"]
        map_list = course_map.get_map_for_profile(profile)

        for i, block in enumerate(map_list):
            if i + 1 < len(map_list) and block.local_id == lesson.local_id:
                return map_list[i + 1].local_id

        return ""

    class Meta:
        model = Lesson
        fields = ["id", "next_id"]
