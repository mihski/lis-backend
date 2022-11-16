import logging

from typing import List, Dict, Iterable

from rest_framework import serializers
from rest_framework.validators import ValidationError
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from lessons.structures.lectures import (
    ReplicaBlock,
    ReplicaNPCBlock,
    TheoryBlock,
    ImportantBlock,
    QuoteBlock,
    ImageBlock,
    GalleryBlock,
    EmailBlock,
    BrowserBlock,
    TableBlock,
    DocBlock,
    VideoBlock,
    MessengerStartBlock,
    MessengerEndBlock,
    DownloadingBlock,
    ButtonBlock,
    DayCounterBlock
)
from lessons.structures.tasks import (
    RadiosBlock,
    CheckboxesBlock,
    SelectsBlock,
    InputBlock,
    NumberBlock,
    RadiosTableBlock,
    ImageAnchorsBlock,
    SortBlock,
    ComparisonBlock,
)
from lessons.models import (
    Lesson,
    Unit,
    LessonBlock,
    Quest,
    Course,
    Branching,
)
from lessons.structures import LessonBlockType, BlockType
from editors.models import Block, EditorSession
from helpers.mixins import ChildAccessMixin


logger = logging.Logger(__file__)


def _check_missed_fields(data: Iterable[Dict], required_fields: set):
    for element in data:
        if not isinstance(element, dict):
            continue

        missed_fields = required_fields.difference(set(element.keys()))

        if missed_fields:
            raise ValidationError(f'{element} missed {missed_fields} fields')


class BaseLisBlockSerializer(serializers.ModelSerializer, ChildAccessMixin):
    """ Requires block_type property for lessons blocks in order to deserialize block object """
    block_type: LessonBlockType = None

    class Meta:
        model = None


class TextBlockSerializer(BaseLisBlockSerializer):
    class Meta:
        fields = ['id', 'message', 'location']


class UrlBlockSerializer(BaseLisBlockSerializer):
    class Meta:
        fields = ['id', 'title', 'url', 'location']


class ReplicaBlockSerializer(TextBlockSerializer):
    block_type = LessonBlockType.replica

    class Meta:
        model = ReplicaBlock
        fields = ['emotion'] + TextBlockSerializer.Meta.fields


class ReplicaNPCBlockSerializer(ReplicaBlockSerializer):
    block_type = LessonBlockType.replicaNPC

    class Meta:
        model = ReplicaNPCBlock
        fields = ['npc'] + ReplicaBlockSerializer.Meta.fields


class TheoryBlockSerializer(TextBlockSerializer):
    block_type = LessonBlockType.theory

    class Meta:
        model = TheoryBlock
        fields = TextBlockSerializer.Meta.fields


class ImportantBlockSerializer(TextBlockSerializer):
    block_type = LessonBlockType.important

    class Meta:
        model = ImportantBlock
        fields = TextBlockSerializer.Meta.fields


class QuoteBlockSerializer(TextBlockSerializer):
    block_type = LessonBlockType.quote

    class Meta:
        model = QuoteBlock
        fields = TextBlockSerializer.Meta.fields


class ImageBlockSerializer(UrlBlockSerializer):
    block_type = LessonBlockType.image

    class Meta:
        model = ImageBlock
        fields = UrlBlockSerializer.Meta.fields


class GalleryBlockSerializer(BaseLisBlockSerializer):
    block_type = LessonBlockType.gallery

    class Meta:
        model = GalleryBlock
        fields = ['id', 'location', 'images']

    def validate_images(self, images: List[Dict[str, str]]):
        """ Check that images field has specified parameters """
        if not isinstance(images, list):
            raise ValidationError('images should be a list')

        for image in images:
            if len(image) != 2 or any(field not in image for field in ['title', 'url']):
                raise ValidationError(f'You should specify both title and url: {image}')

        return images


class EmailBlockSerializer(TextBlockSerializer):
    block_type = LessonBlockType.email

    class Meta:
        model = EmailBlock
        fields = ['npc', 'subject', 'sender', 'to'] + TextBlockSerializer.Meta.fields


class BrowserBlockSerializer(TextBlockSerializer):
    block_type = LessonBlockType.browser

    class Meta:
        model = BrowserBlock
        fields = ['url'] + TextBlockSerializer.Meta.fields


class TableBlockSerializer(UrlBlockSerializer):
    block_type = LessonBlockType.table

    class Meta:
        model = TableBlock
        fields = UrlBlockSerializer.Meta.fields


class DocBlockSerializer(TextBlockSerializer):
    block_type = LessonBlockType.a10_doc

    class Meta:
        model = DocBlock
        fields = ['title'] + TextBlockSerializer.Meta.fields


class MessengerStartBlockSerializer(BaseLisBlockSerializer):
    block_type = LessonBlockType.a12_1_messenger_start

    class Meta:
        model = MessengerStartBlock
        fields = ['id']


class MessengerEndBlockSerializer(BaseLisBlockSerializer):
    block_type = LessonBlockType.a12_2_messenger_end

    class Meta:
        model = MessengerEndBlock
        fields = ['id']


class DownloadingBlockSerializer(BaseLisBlockSerializer):
    block_type = LessonBlockType.a13_downloading

    class Meta:
        model = DownloadingBlock
        fields = ['id', 'title', 'url', 'location']


class ButtonBlockSerializer(BaseLisBlockSerializer):
    block_type = LessonBlockType.a16_button

    class Meta:
        model = ButtonBlock
        fields = ['id', 'value']


class VideoBlockSerializer(UrlBlockSerializer):
    block_type = LessonBlockType.a15_video

    class Meta:
        model = VideoBlock
        fields = UrlBlockSerializer.Meta.fields


class DayCounterBlockSerializer(BaseLisBlockSerializer):
    block_type = LessonBlockType.a17_days

    class Meta:
        model = DayCounterBlock
        fields = ['id', 'location', 'value']


class TaskBlockSerializer(BaseLisBlockSerializer):
    description = serializers.CharField(allow_blank=True)
    ifCorrect = serializers.CharField(source='if_correct')
    ifIncorrect = serializers.CharField(source='if_incorrect')

    class Meta:
        fields = ['id', 'title', 'description', 'ifCorrect', 'ifIncorrect']


class RadiosBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.radios

    variants = serializers.JSONField()
    correct = serializers.CharField(allow_blank=True)

    def validate_variants(self, variants: List[Dict[int, str]]) -> List[Dict[int, str]]:
        _check_missed_fields(variants, {'id', 'variant', 'ifCorrect', 'ifIncorrect'})
        return variants

    class Meta:
        model = RadiosBlock
        fields = ['variants', 'correct'] + TaskBlockSerializer.Meta.fields


class CheckboxesBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.checkboxes

    variants = serializers.JSONField()
    correct = serializers.JSONField()

    def validate_variants(self, variants: List[Dict[int, str]]) -> List[Dict[int, str]]:
        _check_missed_fields(variants, {'id', 'variant', 'ifCorrect', 'ifIncorrect'})

        return variants

    class Meta:
        model = CheckboxesBlock
        fields = ['variants', 'correct'] + TaskBlockSerializer.Meta.fields


class SelectsBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.selects

    body = serializers.CharField()
    selects = serializers.JSONField()
    correct = serializers.JSONField()

    def validate_selects(self, selects: Dict[int, List[Dict[str, str]]]):
        if not isinstance(selects, dict):
            return ValidationError('selects is suppose to be a json')

        all_selects = [s for row in selects.values() for s in row]
        _check_missed_fields(all_selects, {'id', 'value'})

        return selects

    class Meta:
        model = SelectsBlock
        fields = ['body', 'selects', 'correct'] + TaskBlockSerializer.Meta.fields


class InputBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.input

    correct = serializers.JSONField()

    def validate_correct(self, correct: Dict[str, List[str]]):
        _check_missed_fields([correct], {'ru', 'en'})
        return correct

    class Meta:
        model = InputBlock
        fields = ['correct'] + TaskBlockSerializer.Meta.fields


class NumberBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.number

    class Meta:
        model = NumberBlock
        fields = ['tolerance', 'correct'] + TaskBlockSerializer.Meta.fields


class RadiosTableBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.radiosTable

    columns = serializers.JSONField()
    rows = serializers.JSONField()
    isRadio = serializers.BooleanField(source='is_radio', read_only=True)
    correct = serializers.JSONField()

    def validate_columns(self, columns: List[Dict[str, str]]):
        _check_missed_fields(columns, {'name', 'id'})
        return columns

    def validate_rows(self, rows: Dict[str, str]):
        _check_missed_fields([rows], {'name', 'id', 'ifCorrect', 'ifIncorrect'})
        return rows

    def validate(self, data):
        data['is_radio'] = True
        return data

    class Meta:
        model = RadiosTableBlock
        fields = ['columns', 'rows', 'isRadio', 'correct'] + TaskBlockSerializer.Meta.fields


class ImageAnchorsBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.imageAnchors

    anchors = serializers.JSONField()
    options = serializers.JSONField()
    imgUrl = serializers.CharField(source='img_url')
    correct = serializers.JSONField()

    def validate_anchors(self, anchors: List[Dict[str, str]]):
        _check_missed_fields(anchors, {'name', 'id', 'x', 'y'})
        return anchors

    def validate_options(self, options: List[Dict[str, str]]):
        _check_missed_fields(options, {'value', 'id'})
        return options

    class Meta:
        model = ImageAnchorsBlock
        fields = ['anchors', 'options', 'imgUrl', 'correct'] + TaskBlockSerializer.Meta.fields


class SortBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.sort

    options = serializers.JSONField()
    correct = serializers.JSONField()

    def validate_options(self, options: List[Dict[int, str]]) -> List[Dict[int, str]]:
        _check_missed_fields(options, {'value', 'id'})
        return options

    class Meta:
        model = SortBlock
        fields = ['options', 'correct'] + TaskBlockSerializer.Meta.fields


class ComparisonBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.comparison

    lists = serializers.JSONField()
    correct = serializers.JSONField()

    def validate_lists(self, lists: List[List[Dict[str, str]]]):
        for row in lists:
            _check_missed_fields(row, {'name', 'id'})

        return lists

    class Meta:
        model = ComparisonBlock
        fields = ['lists', 'correct'] + TaskBlockSerializer.Meta.fields


class UnitListSerializer(serializers.ListSerializer):
    def update(self, instances: List[Unit], validated_datas):
        ret = []
        local2instance = {
            instance.local_id: instance
            for instance in instances
        }
        local2data = {
            data['local_id']: data
            for data in validated_datas
        }

        # FIXME: rewrite with less queires
        for local_id in local2data.keys():
            # TODO: почему то приходят десериализованные данные
            instance = local2instance.get(local_id, None)
            validated_data = local2data[local_id]
            validated_data['lesson'] = validated_data['lesson'].id

            obj_serializer = UnitSerializer(data=validated_data)

            if instance:
                obj_serializer = UnitSerializer(instance, data=validated_data)

            obj_serializer.is_valid()
            obj_serializer.save()
            ret.append(obj_serializer.save())

        lids_to_delete = set(local2instance.keys()) - set(local2data.keys())
        # TODO: как то сохранять или создавать новые версии (ревизии)
        Unit.objects.filter(local_id__in=lids_to_delete).delete()

        return ret


class EditorBlockMixin:
    """ Provide create editor block interface """
    CLASS_TO_TYPE_MAPPING = {
        Lesson: BlockType.lesson,
        Branching: BlockType.branching,
        Unit: BlockType.unit,
        Quest: BlockType.quest,
    }

    def block_provided(self, validated_data):
        return validated_data.get('x') and validated_data.get('y')

    def check_exist_block(self, instance):
        block = Block.objects.filter(id=instance.block_id).first()

        return block

    def create_block(self, instance, validated_data):
        if not self.block_provided(validated_data):
            return

        block = self.check_exist_block(instance)
        x, y = validated_data['x'], validated_data['y']

        if block:
            logger.warning("Tried to create duplication block. Updating exists one.")
            return self.update_block(instance, x, y, block=block)

        body_type = self.CLASS_TO_TYPE_MAPPING[instance.__class__].value
        block = Block.objects.create(x=x, y=y, type=body_type, body_id=instance.id)
        instance.block_id = block.id
        instance.save()

        return block

    def update_block(self, instance, validated_data, block=None):
        if not self.block_provided(validated_data):
            return

        x, y = validated_data['x'], validated_data['y']

        if not block:
            block = self.check_exist_block(instance)

        if not block:
            logger.error(f"There is no block for {instance.__class__}: {instance.id}. Creating...")
            return self.create_block(instance, validated_data)

        block.x = x
        block.y = y
        instance.block_id = block.id

        block.save()
        instance.save()

        return block


class LisEditorModelSerializer(serializers.ModelSerializer, EditorBlockMixin):
    """ Отнаследованные сериализаторы будут создавать блок """
    def create(self, validated_data):
        # block_data = {
        #     'x': validated_data.pop('x', None),
        #     'y': validated_data.pop('y', None)
        # }
        instance = super(LisEditorModelSerializer, self).create(validated_data)
        instance.save()

        # self.create_block(instance, block_data)

        return instance

    def update(self, instance, validated_data):
        # block_data = {
        #     'x': validated_data.pop('x', None),
        #     'y': validated_data.pop('y', None)
        # }

        instance = super(LisEditorModelSerializer, self).update(instance, validated_data)
        instance.save()

        # self.update_block(instance, block_data)

        return instance


class UnitSerializer(LisEditorModelSerializer):
    LESSON_BLOCK_SERIALIZERS: Dict[LessonBlockType, BaseLisBlockSerializer] = dict()

    id = serializers.IntegerField(required=False)
    local_id = serializers.CharField()
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())
    type = serializers.IntegerField()
    next = serializers.JSONField()
    content = serializers.JSONField()

    def __init__(self, *args, **kwargs):
        super(UnitSerializer, self).__init__(*args, **kwargs)

        for subclass in BaseLisBlockSerializer.get_all_subclasses():
            if subclass.block_type:
                self.LESSON_BLOCK_SERIALIZERS[subclass.block_type] = subclass

    def get_unit_content_serializer(self, lesson_type: int):
        lesson_block_type = LessonBlockType(lesson_type)

        return self.LESSON_BLOCK_SERIALIZERS[lesson_block_type]

    def validate_type(self, lesson_type: int) -> int:
        if not LessonBlockType.has_value(lesson_type):
            raise ValidationError(f'type ({lesson_type}) is not specified')

        lesson_block_type = LessonBlockType(lesson_type)

        if lesson_block_type not in self.LESSON_BLOCK_SERIALIZERS:
            raise ValidationError(f'serializer with type {lesson_type} is not specified')

        return lesson_type

    def validate(self, data):
        content_serializer = self.get_unit_content_serializer(data['type'])
        content_serializer(data=data['content']).is_valid()
        # TODO: if len(next) > 1 check blocks are replicas
        return data

    def create(self, validated_data):
        # creating content
        content_serializer = self.get_unit_content_serializer(validated_data['type'])
        content = content_serializer(data=validated_data['content'])
        content.is_valid(raise_exception=True)
        content = content.save()

        # creating unit
        instance: Unit = super().create(validated_data)
        instance.content = content_serializer(content).data

        # binding lesson block
        instance.lesson_block = instance.lesson.content

        instance.save()

        return instance

    def update(self, instance, validated_data):
        content_serializer = self.get_unit_content_serializer(validated_data['type'])
        instance.next = validated_data.get('next', instance.next)

        if instance.type == validated_data['type'] and instance.content:
            content_obj = content_serializer.Meta.model.objects.filter(
                id=instance.content['id']
            ).only().first()
            obj = content_serializer(content_obj, data=validated_data['content'], partial=True)
            obj.is_valid()
            obj.save()

            validated_data['content'] = obj.data

        instance.type = validated_data.get('type', instance.type)
        instance.content = validated_data.get('content', instance.content)
        instance.x = validated_data.get('x', instance.x)
        instance.y = validated_data.get('y', instance.x)
        instance.save()

        return instance

    class Meta:
        model = Unit
        fields = ['id', 'local_id', 'lesson', 'type', 'next', 'content', 'x', 'y']

        list_serializer_class = UnitListSerializer


class LessonContentSerializer(serializers.ModelSerializer):
    blocks = UnitSerializer(many=True)
    entry = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    locale = serializers.JSONField()
    markup = serializers.JSONField()

    def validate_markup(self, markup: Dict[str, List[int]]):
        if not any(field in markup for field in ['ru', 'en']):
            raise ValidationError('There should be both ru and en')

        difference_ru = set(markup['ru']).difference(markup['en'])
        difference_en = set(markup['en']).difference(markup['ru'])

        if difference_ru or difference_en:
            raise ValidationError(
                f'There is no equal ru and en blocks. ru: {difference_ru}. en: {difference_en}'
            )

        return markup

    def create(self, validated_data):
        blocks_data = validated_data.pop('blocks')
        instance = super(LessonContentSerializer, self).create(validated_data)

        serialized_blocks = UnitSerializer(
            data=blocks_data,
            many=True
        )
        serialized_blocks.is_valid()
        blocks = serialized_blocks.save()

        for block in blocks:
            block.lesson_block = instance

        Unit.objects.bulk_update(blocks, fields=['lesson_block'])
        instance.save()

        return instance

    def update(self, instance, validated_data):
        # если нам передали блоки, то обновляем
        if 'blocks' in validated_data:
            for block in validated_data['blocks']:
                block['lesson'] = block['lesson'].id

            serialized_blocks = UnitSerializer(
                list(instance.blocks.all()),
                data=validated_data.pop('blocks'),
                many=True
            )
            serialized_blocks.is_valid(raise_exception=True)
            serialized_blocks.save()

        instance = super().update(instance, validated_data)
        instance.save()

        return instance

    class Meta:
        model = LessonBlock
        fields = [
            'id',
            'lesson',
            'blocks',
            'entry',
            'locale',
            'markup'
        ]


class LessonListSerializer(serializers.ListSerializer):
    def update(self, instances: List[Lesson], validated_datas):
        ret = []
        local2instance = {
            instance.local_id: instance
            for instance in instances
        }
        local2data = {
            data['local_id']: data
            for data in validated_datas
        }

        for local_id in local2data.keys():
            instance = local2instance.get(local_id, None)
            validated_data = local2data[local_id]

            LessonSerializer.reverse_validated_data(validated_data)
            obj_serializer = LessonSerializer(data=validated_data)

            if instance:
                obj_serializer = LessonSerializer(instance, data=validated_data)

            obj_serializer.is_valid(raise_exception=True)
            obj_serializer.save()
            ret.append(obj_serializer.save())

        lids_to_delete = set(local2instance.keys()) - set(local2data.keys())
        # TODO: как то сохранять или создавать новые версии (ревизии)
        Lesson.objects.filter(local_id__in=lids_to_delete).delete()

        return ret


class LessonSerializer(LisEditorModelSerializer):
    local_id = serializers.CharField()

    name = serializers.CharField()
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    timeCost = serializers.IntegerField(source='time_cost')
    moneyCost = serializers.IntegerField(source='money_cost')
    energyCost = serializers.IntegerField(source='energy_cost')
    has_bonuses = serializers.BooleanField(default=False)
    bonuses = serializers.JSONField()
    content = LessonContentSerializer(required=False)
    next = serializers.CharField(allow_blank=True)
    unit_count = serializers.SerializerMethodField()

    def get_unit_count(self, lesson: Lesson) -> int:
        return lesson.unit_set.count()

    @staticmethod
    def reverse_validated_data(lessons):
        if not isinstance(lessons, list):
            lessons = [lessons]

        for lesson in lessons:
            lesson['course'] = lesson['course'].id
            lesson['timeCost'] = lesson.pop('time_cost')
            lesson['energyCost'] = lesson.pop('energy_cost')
            lesson['moneyCost'] = lesson.pop('money_cost')

            if 'content' in lesson:
                lesson['content']['lesson'] = lesson['content']['lesson'].id

    def create(self, validated_data):
        lesson_block_content = validated_data.pop('content', None)
        lesson_block = LessonBlock()

        # если нам передали content, то сериализуем его,
        # если нет, то привязываем дефолтный блок к уроку
        if lesson_block_content:
            lesson_block_content['lesson'] = lesson_block_content['lesson'].id
            serialized_lesson_block = LessonContentSerializer(
                data=lesson_block_content
            )
            serialized_lesson_block.is_valid()
            lesson_block = serialized_lesson_block.save()

        lesson_block.save()

        validated_data['content'] = lesson_block
        instance = super(LessonSerializer, self).create(validated_data)
        instance.save()

        return instance

    def update(self, instance, validated_data):
        if 'content' in validated_data:
            if not isinstance(validated_data['content']['lesson'], int):
                validated_data['content']['lesson'] = validated_data['content']['lesson'].id

            for block in validated_data['content']['blocks']:
                block['lesson'] = block['lesson'].id

            serialized_content = LessonContentSerializer(
                instance.content,
                data=validated_data.pop('content')
            )
            serialized_content.is_valid(raise_exception=True)
            instance.content = serialized_content.save()

        instance = super().update(instance, validated_data)
        instance.save()

        return instance

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
            'content',
            'next',
            'has_bonuses',
            'x',
            'y',
            'unit_count',
        ]

        list_serializer_class = LessonListSerializer


class QuestListSerializer(serializers.ListSerializer):
    def update(self, instances: List[Quest], validated_datas):
        ret = []

        local2instance = {
            instance.local_id: instance
            for instance in instances
        }
        local2data = {
            data['local_id']: data
            for data in validated_datas
        }

        for local_id in local2data.keys():
            instance = local2instance.get(local_id, None)
            validated_data = local2data[local_id]

            QuestSerializer.reverse_validated_data(validated_data)

            obj_serializer = QuestSerializer(instance, data=validated_data)
            obj_serializer.is_valid(raise_exception=True)
            ret.append(obj_serializer.save())

        lids_to_delete = set(local2instance.keys()) - set(local2data.keys())
        # TODO: как то сохранять или создавать новые версии (ревизии)
        Quest.objects.filter(local_id__in=lids_to_delete).delete()

        return ret


class BranchingListSerializer(serializers.ListSerializer):
    def update(self, instances: List[Branching], validated_datas):
        ret = []

        local2instance = {
            instance.local_id: instance
            for instance in instances
        }
        local2data = {
            data['local_id']: data
            for data in validated_datas
        }

        for local_id in local2data.keys():
            instance = local2instance.get(local_id, None)
            validated_data = local2data[local_id]

            obj_serializer = BranchingSerializer(instance, data=validated_data)
            obj_serializer.is_valid()
            ret.append(obj_serializer.save())

        lids_to_delete = set(local2instance.keys()) - set(local2data.keys())
        # TODO: как то сохранять или создавать новые версии (ревизии)
        Branching.objects.filter(local_id__in=lids_to_delete).delete()

        return ret


class BranchingSerializer(LisEditorModelSerializer):
    local_id = serializers.CharField()

    # TODO: добавить два типа бранчей
    class Meta:
        model = Branching
        fields = ['id', 'local_id', 'course', 'quest', 'x', 'y', 'type', 'content']

        list_serializer_class = BranchingListSerializer


class QuestSerializer(LisEditorModelSerializer):
    local_id = serializers.CharField()

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    lessons = LessonSerializer(many=True)
    branchings = BranchingSerializer(required=False, many=True)

    description = serializers.CharField()
    entry = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    next = serializers.CharField(allow_blank=True)

    @staticmethod
    def reverse_validated_data(quests):
        if not isinstance(quests, list):
            quests = [quests]

        for quest in quests:
            quest['course'] = quest['course'].id

            if 'lessons' in quest:
                LessonSerializer.reverse_validated_data(quest['lessons'])

    def _update_lessons(self, instance, actual_lessons, lessons_data):
        for lesson in lessons_data:
            LessonSerializer.reverse_validated_data(lesson)
            # in order to skip content updating
            lesson.pop('content', None)

        lessons_serializer = LessonSerializer(actual_lessons, data=lessons_data, many=True)
        lessons_serializer.is_valid(raise_exception=True)
        lessons = lessons_serializer.save()

        for lesson in lessons:
            lesson.quest = instance

        Lesson.objects.bulk_update(lessons, fields=['quest'])

        return lessons

    def _update_branchings(self, instance, actual_branchings, branchings_data):
        branching_serializer = BranchingSerializer(actual_branchings, data=branchings_data, many=True)
        branching_serializer.is_valid()
        branchings = branching_serializer.save()

        for branch in branchings:
            branch.quest = instance
            branch.course = instance.course

        Branching.objects.bulk_update(branchings, fields=['course', 'quest'])

        return branchings

    def create(self, validated_data):
        lessons_data = validated_data.pop('lessons', [])
        branchings_data = validated_data.pop('branchings', [])

        instance = super().create(validated_data)

        self._update_lessons(instance, [], lessons_data)
        self._update_branchings(instance, [], branchings_data)

        return instance

    def update(self, instance, validated_data):
        lessons_data = validated_data.pop('lessons', [])
        branchings_data = validated_data.pop('branchings', [])

        instance = super().update(instance, validated_data)

        self._update_lessons(instance, instance.lessons.all(), lessons_data)
        self._update_branchings(instance, instance.branchings.all(), branchings_data)

        return instance

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

        list_serializer_class = QuestListSerializer


class BlockSerializer(serializers.ModelSerializer):
    BLOCK_TYPE_TO_SERIALIZER = {
        BlockType.lesson: LessonSerializer,
        BlockType.unit: UnitSerializer,
        BlockType.branching: BranchingSerializer,
        BlockType.quest: QuestSerializer
    }

    x = serializers.FloatField()
    y = serializers.FloatField()
    type = serializers.IntegerField()
    body = serializers.JSONField(read_only=True)

    def _get_body_serializer(self, block_type: int):
        type = BlockType(block_type)
        return self.BLOCK_TYPE_TO_SERIALIZER[type]

    def get_body(self, obj: Block):
        # TODO: проверить скорость, если нужно, оптимизировать
        # получаем нужную модель данных из поля type, сериализуем body_id элемент
        body_serializer = self._get_body_serializer(obj.type)
        body_model = body_serializer.Meta.model
        body_obj = body_model.objects.filter(id=obj.body_id).only()
        return body_serializer(body_obj).data

    class Meta:
        model = Block
        fields = ['id', 'x', 'y', 'type', 'body']


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(required=False, many=True)
    quests = QuestSerializer(required=False, many=True)
    branchings = BranchingSerializer(required=False, many=True)

    name = serializers.CharField()
    description = serializers.CharField()
    entry = serializers.CharField(required=False, allow_blank=True)
    locale = serializers.JSONField(required=False)

    class Meta:
        model = Course
        fields = ['id', 'lessons', 'quests', 'branchings', 'name', 'description', 'entry', 'locale', 'is_editable']

    def to_representation(self, instance):
        """ Filter lessons and branchings inside quests """
        representation = super().to_representation(instance)

        representation['lessons'] = [x for x in representation['lessons'] if x['quest'] is None]
        representation['branchings'] = [x for x in representation['branchings'] if x['quest'] is None]

        if not self.context["request"].GET.get("full", "false") == "true":
            [x.pop("content") for x in representation['lessons'] if x['quest'] is None]
            [x.pop("content") for quest in representation['quests'] for x in quest["lessons"]]

        return representation

    def validate(self, data):
        super().validate(data)
        
        lessons = data.get('lessons', [])
        quests = data.get('quests', [])
        branchings = data.get('branchings', [])

        local_ids = {
            lesson['local_id']
            for lesson in lessons
        } | {
            quest['local_id']
            for quest in quests
        } | {
            branch['local_id']
            for branch in branchings
        }

        if len(local_ids) != len(lessons) + len(quests) + len(branchings):
            raise ValidationError(f"lesson ids through course should be unique: {local_ids}")

        return data

    def _update_courses_entities(
        self,
        course,
        list_serializer,
        actual_instances,
        new_instances_data
    ):
        obj_serialized = list_serializer(actual_instances, data=new_instances_data, many=True)
        obj_serialized.is_valid(raise_exception=True)
        objs = obj_serialized.save()

        for obj in objs:
            obj.course = course

        list_serializer.Meta.model.objects.bulk_update(objs, fields=['course'])

    def create(self, validated_data):
        validated_data.pop('lessons', [])
        validated_data.pop('quests', [])
        validated_data.pop('branchings', [])

        instance = super().create(validated_data)

        return instance

    def update(self, instance, validated_data):
        lessons_data = validated_data.pop('lessons', [])
        quests_data = validated_data.pop('quests', [])
        branchings_data = validated_data.pop('branchings', [])

        instance = super().update(instance, validated_data)

        LessonSerializer.reverse_validated_data(lessons_data)
        QuestSerializer.reverse_validated_data(quests_data)

        self._update_courses_entities(
            instance,
            LessonSerializer,
            instance.lessons.filter(quest__isnull=True).all(),
            lessons_data,
        )
        self._update_courses_entities(
            instance,
            QuestSerializer,
            instance.quests.all(),
            quests_data,
        )
        self._update_courses_entities(
            instance,
            BranchingSerializer,
            instance.branchings.filter(quest__isnull=True).all(),
            branchings_data,
        )

        instance.refresh_from_db()

        return instance


class EditorSessionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    local_id = serializers.CharField(default='')
    is_closed = serializers.ReadOnlyField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = User.objects.get(id=representation['user']).username
        return representation

    class Meta:
        model = EditorSession
        fields = ["user", "course", "local_id", "is_closed"]
