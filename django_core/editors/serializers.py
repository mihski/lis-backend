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
    VideoBlock
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
from lessons.models import Lesson, Unit, LessonBlock


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


def _check_missed_fields(data: Iterable[Dict], required_fields: set):
    for element in data:
        missed_fields = required_fields.difference(set(element.keys()))

        if missed_fields:
            raise ValidationError(f'{element} missed {missed_fields} fields')


class BaseLisBlockSerializer(serializers.ModelSerializer):
    """ Requires block_type property for lessons blocks in order to deserialize block object """
    block_type: LessonBlockType = None

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
        fields = ['message', 'location']


class UrlBlockSerializer(BaseLisBlockSerializer):
    class Meta:
        fields = ['title', 'url', 'location']

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
        model = RadiosBlock
        fields = ['lists', 'correct'] + TaskBlockSerializer.Meta.fields


class UnitSerializer(serializers.ModelSerializer):
    LESSON_BLOCK_SERIALIZERS: Dict[LessonBlockType, BaseLisBlockSerializer] = dict()

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
        content_serializer(data=data['content']).is_valid(raise_exception=True)

        return data

    def create(self, validated_data):
        return Unit(**validated_data)

    class Meta:
        model = Unit
        fields = '__all__'


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
        blocks = UnitSerializer(
            data=validated_data.pop('blocks'),
            many=True
        )
        blocks.is_valid()
        blocks = blocks.save()

        Unit.objects.bulk_create(blocks)

        validated_data['entry'] = blocks[validated_data['entry']].id
        instance = super(LessonContentSerializer, self).create(validated_data)

        for block in blocks:
            block.lesson_block = instance

        Unit.objects.bulk_update(blocks, fields=['lesson_block'])

        return instance

    class Meta:
        model = LessonBlock
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    timeCost = serializers.IntegerField(source='time_cost')
    moneyCost = serializers.IntegerField(source='money_cost')
    energyCost = serializers.IntegerField(source='energy_cost')
    bonuses = serializers.JSONField()
    content = LessonContentSerializer(required=False)

    def create(self, validated_data):
        content = LessonContentSerializer(
            data=validated_data.pop('content')
        )
        content.is_valid()
        content = content.save()

        instance = super(LessonSerializer, self).create(validated_data)
        instance.content = content
        instance.save()

        return instance

    class Meta:
        model = Lesson
        fields = [
            'name',
            'timeCost',
            'moneyCost',
            'energyCost',
            'bonuses',
            'content',
        ]
