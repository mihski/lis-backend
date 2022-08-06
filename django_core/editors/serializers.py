import logging

from enum import Enum
from typing import List, Dict, Iterable

from rest_framework import serializers
from rest_framework.validators import ValidationError

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
from lessons.models import Lesson, Unit, LessonBlock, Quest, Course, Branching
from editors.models import Block


logger = logging.Logger(__file__)


class LessonBlockType(Enum):
    replica = 100
    replicaNPC = 101

    theory = 202
    important = 203
    quote = 204
    image = 205
    gallery = 206
    email = 207
    browser = 208
    table = 209
    doc = 210
    messenger = 211
    video = 212

    radios = 301
    checkboxes = 302
    selects = 303
    input = 304
    number = 305
    radiosTable = 306
    imageAnchors = 307
    sort = 308
    comparison = 309

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class BlockType(Enum):
    lesson = 1
    quest = 2
    unit = 3
    branching = 4


def _check_missed_fields(data: Iterable[Dict], required_fields: set):
    for element in data:
        missed_fields = required_fields.difference(set(element.keys()))

        if missed_fields:
            raise ValidationError(f'{element} missed {missed_fields} fields')


class BaseLisBlockSerializer(serializers.ModelSerializer):
    """ Requires block_type property for lessons blocks in order to deserialize block object """
    block_type: LessonBlockType = None

    class Meta:
        model = None

    @staticmethod
    def get_all_subclasses() -> List['BaseLisBlockSerializer']:
        subclasses = set()
        work = [BaseLisBlockSerializer]

        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)

        return list(subclasses)


class TextBlockSerializer(BaseLisBlockSerializer):
    class Meta:
        fields = ['id', 'message', 'location']


class UrlBlockSerializer(BaseLisBlockSerializer):
    class Meta:
        fields = ['id', 'title', 'url', 'location']

    def validate_url(self, url: str) -> str:
        if not url.startswith('http'):
            raise ValidationError('url should starts with http')

        return url


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
        fields = ['location', 'images']

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
        fields = ['npc', 'subject', 'from', 'to'] + TextBlockSerializer.Meta.fields

    def get_from(self, obj: EmailBlock):
        return obj.f_from


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
    block_type = LessonBlockType.doc

    class Meta:
        model = DocBlock
        fields = ['title'] + TextBlockSerializer.Meta.fields


class VideoBlockSerializer(UrlBlockSerializer):
    block_type = LessonBlockType.video

    class Meta:
        model = VideoBlock
        fields = UrlBlockSerializer.Meta.fields


class TaskBlockSerializer(BaseLisBlockSerializer):
    ifCorrect = serializers.CharField(source='if_correct')
    ifIncorrect = serializers.CharField(source='if_incorrect')

    class Meta:
        fields = ['id', 'title', 'description', 'ifCorrect', 'ifIncorrect']


class RadiosBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.radios

    variants = serializers.JSONField()
    correct = serializers.IntegerField(write_only=True)

    def validate_variants(self, variants: List[Dict[int, str]]) -> List[Dict[int, str]]:
        _check_missed_fields(variants, {'id', 'variant', 'ifCorrect', 'ifIncorrect'})

        return variants

    class Meta:
        model = RadiosBlock
        fields = ['variants', 'correct'] + TaskBlockSerializer.Meta.fields


class CheckboxesBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.checkboxes

    variants = serializers.JSONField()
    correct = serializers.JSONField(write_only=True)

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
    correct = serializers.JSONField(write_only=True)

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

    correct = serializers.JSONField(write_only=True)

    def validate_correct(self, correct: Dict[str, List[str]]):
        _check_missed_fields([correct], {'ru', 'en'})

    class Meta:
        model = InputBlock
        fields = ['correct'] + TaskBlockSerializer.Meta.fields


class NumberBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.number

    tolerance = serializers.IntegerField(write_only=True)
    correct = serializers.IntegerField(write_only=True)

    class Meta:
        model = NumberBlock
        fields = ['tolerance', 'correct'] + TaskBlockSerializer.Meta.fields


class RadiosTableBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.radiosTable

    columns = serializers.JSONField()
    rows = serializers.JSONField()
    isRadio = serializers.BooleanField(source='is_radio', read_only=True)
    correct = serializers.JSONField(write_only=True)

    def validate_columns(self, columns: List[Dict[str, str]]):
        _check_missed_fields(columns, {'name', 'id'})

    def validate_rows(self, rows: Dict[str, str]):
        _check_missed_fields([rows], {'name', 'id', 'ifCorrect', 'ifIncorrect'})

    class Meta:
        model = RadiosTableBlock
        fields = ['columns', 'rows', 'isRadio', 'correct'] + TaskBlockSerializer.Meta.fields


class ImageAnchorsBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.imageAnchors

    anchors = serializers.JSONField()
    options = serializers.JSONField()
    imgUrl = serializers.CharField(source='img_url')
    correct = serializers.JSONField(write_only=True)

    def validate_anchors(self, anchors: List[Dict[str, str]]):
        _check_missed_fields(anchors, {'name', 'id', 'x', 'y'})

    def validate_options(self, options: List[Dict[str, str]]):
        _check_missed_fields(options, {'value', 'id'})

    class Meta:
        model = ImageAnchorsBlock
        fields = ['anchors', 'options', 'imgUrl', 'correct'] + TaskBlockSerializer.Meta.fields


class SortBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.radios

    options = serializers.JSONField()
    correct = serializers.JSONField(write_only=True)

    def validate_options(self, options: List[Dict[int, str]]) -> List[Dict[int, str]]:
        _check_missed_fields(options, {'value', 'id'})
        return options

    class Meta:
        model = SortBlock
        fields = ['options', 'correct'] + TaskBlockSerializer.Meta.fields


class ComparisonBlockSerializer(TaskBlockSerializer):
    block_type = LessonBlockType.radios

    lists = serializers.JSONField()
    correct = serializers.JSONField(write_only=True)

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

        # FIXME: rewrite with less queires
        for instance, validated_data in zip(instances, validated_datas):
            obj_serializer = UnitSerializer(instance, data=validated_data)
            obj_serializer.is_valid()
            ret.append(obj_serializer.save())

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
    def create(self, validated_data):
        block_data = {
            'x': validated_data.pop('x', None),
            'y': validated_data.pop('y', None)
        }
        instance = super(LisEditorModelSerializer, self).create(validated_data)
        instance.save()

        self.create_block(instance, block_data)

        return instance

    def update(self, instance, validated_data):
        block_data = {
            'x': validated_data.pop('x', None),
            'y': validated_data.pop('y', None)
        }

        instance = super(LisEditorModelSerializer, self).update(instance, validated_data)
        instance.save()

        self.update_block(instance, block_data)

        return instance


class UnitSerializer(LisEditorModelSerializer):
    LESSON_BLOCK_SERIALIZERS: Dict[LessonBlockType, BaseLisBlockSerializer] = dict()

    x = serializers.FloatField(write_only=True, required=False)
    y = serializers.FloatField(write_only=True, required=False)

    id = serializers.IntegerField(required=False)
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
        content.is_valid()
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
        instance.next = validated_data.get('next', instance.type)

        if instance.type == validated_data['type']:
            content_obj = content_serializer.Meta.model.objects.filter(
                id=validated_data['content']['id']
            ).only().first()
            obj = content_serializer(content_obj, data=validated_data['content'], partial=True)
            obj.is_valid()
            obj.save()

            validated_data['content'] = obj.data

        instance.type = validated_data.get('type', instance.type)
        instance.content = validated_data['content']
        instance.save()

        return instance

    class Meta:
        model = Unit
        fields = ['id', 'lesson', 'type', 'next', 'content', 'x', 'y']

        list_serializer_class = UnitListSerializer


class LessonContentSerializer(serializers.ModelSerializer):
    blocks = UnitSerializer(many=True)
    entry = serializers.IntegerField()
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
            list(instance.blocks.all()),
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
        serialized_blocks = UnitSerializer(
            list(instance.blocks.all()),
            data=validated_data.pop('blocks'),
            many=True
        )
        serialized_blocks.is_valid()
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


class LessonSerializer(LisEditorModelSerializer):
    x = serializers.FloatField(write_only=True, required=False)
    y = serializers.FloatField(write_only=True, required=False)

    name = serializers.CharField()
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    timeCost = serializers.IntegerField(source='time_cost')
    moneyCost = serializers.IntegerField(source='money_cost')
    energyCost = serializers.IntegerField(source='energy_cost')
    bonuses = serializers.JSONField()
    content = LessonContentSerializer(required=False)

    def create(self, validated_data):
        lesson_block_content = validated_data.pop('content', None)
        instance = super(LessonSerializer, self).create(validated_data)

        lesson_block = LessonBlock()

        if lesson_block_content:
            serialized_lesson_block = LessonContentSerializer(
                data=lesson_block_content
            )
            serialized_lesson_block.is_valid()
            lesson_block = serialized_lesson_block.save()

        lesson_block.save()
        instance.content = lesson_block

        instance.save()

        return instance

    def update(self, instance, validated_data):
        serialized_content = LessonContentSerializer(
            instance.content,
            data=validated_data.pop('content')
        )
        serialized_content.is_valid()

        instance.content = serialized_content.save()
        instance.save()

        instance = super().update(instance, validated_data)
        instance.save()

        return instance

    class Meta:
        model = Lesson
        fields = [
            'id',
            'course',
            'name',
            'timeCost',
            'moneyCost',
            'energyCost',
            'bonuses',
            'content',
            'x',
            'y',
        ]


class QuestSerializer(LisEditorModelSerializer):
    x = serializers.FloatField(write_only=True, required=False)
    y = serializers.FloatField(write_only=True, required=False)

    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    lesson_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Lesson.objects.all(),
        source='lessons',
        write_only=True,
    )
    lessons = LessonSerializer(many=True, read_only=True)
    description = serializers.CharField()
    entry = serializers.IntegerField()
    next = serializers.IntegerField()

    def validate_lessons(self, lessons):
        return lessons

    class Meta:
        model = Quest
        fields = [
            'id',
            'course',
            'lesson_ids',
            'lessons',
            'description',
            'entry',
            'next',
            'x',
            'y'
        ]
        depth = 0


class BranchingSerializer(LisEditorModelSerializer):
    class Meta:
        model = Branching
        fields = ['id', 'type', 'content']


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
        body_serializer = self._get_body_serializer(obj.type)
        body_model = body_serializer.Meta.model
        body_obj = body_model.objects.filter(id=obj.body_id).only()
        return body_serializer(body_obj).data

    class Meta:
        model = Block
        fields = ['id', 'x', 'y', 'type', 'body']


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    quests = QuestSerializer(many=True, read_only=True)
    branchings = BranchingSerializer(many=True)
    entry = serializers.IntegerField()
    locale = serializers.JSONField()

    class Meta:
        model = Course
        fields = ['id', 'lessons', 'quests', 'branchings', 'entry', 'locale']
