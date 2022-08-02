from enum import Enum
from typing import List, Dict

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


class TextBlockSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['message', 'location']


class UrlBlockSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['title', 'url', 'location']

    def validate_url(self, url: str) -> str:
        if not url.startswith('http'):
            raise ValidationError('url should starts with http')

        return url


class ReplicaBlockSerializer(TextBlockSerializer):
    class Meta:
        model = ReplicaBlock
        fields = ['emotion'] + TextBlockSerializer.Meta.fields


class ReplicaNPCBlockSerializer(ReplicaBlockSerializer):
    class Meta:
        model = ReplicaNPCBlock
        fields = ['npc'] + ReplicaBlockSerializer.Meta.fields


class TheoryBlockSerializer(TextBlockSerializer):
    class Meta:
        model = TheoryBlock
        fields = TextBlockSerializer.Meta.fields


class ImportantBlockSerializer(TextBlockSerializer):
    class Meta:
        model = ImportantBlock
        fields = TextBlockSerializer.Meta.fields


class QuoteBlockSerializer(TextBlockSerializer):
    class Meta:
        model = QuoteBlock
        fields = TextBlockSerializer.Meta.fields


class ImageBlockSerializer(UrlBlockSerializer):
    class Meta:
        model = ImageBlock
        fields = UrlBlockSerializer.Meta.fields


class GalleryBlockSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = EmailBlock
        fields = ['npc', 'subject', 'from', 'to'] + TextBlockSerializer.Meta.fields

    def get_from(self, obj: EmailBlock):
        return obj.f_from


class BrowserBlockSerializer(TextBlockSerializer):
    class Meta:
        model = BrowserBlock
        fields = ['url'] + TextBlockSerializer.Meta.fields


class TableBlockSerializer(UrlBlockSerializer):
    class Meta:
        model = TableBlock
        fields = UrlBlockSerializer.Meta.fields


class DocBlockSerializer(TextBlockSerializer):
    class Meta:
        model = DocBlock
        fields = ['title'] + TextBlockSerializer.Meta.fields


class VideoBlockSerializer(UrlBlockSerializer):
    class Meta:
        model = VideoBlock
        fields = UrlBlockSerializer.Meta.fields


class UnitSerializer(serializers.ModelSerializer):
    LESSON_BLOCK_SERIALIZERS = {
        LessonBlockType.replica: ReplicaBlockSerializer,
        LessonBlockType.replicaNPC: ReplicaNPCBlockSerializer,
        LessonBlockType.theory: TheoryBlockSerializer,
        LessonBlockType.important: ImportantBlockSerializer,
        LessonBlockType.quote: QuoteBlockSerializer,
        LessonBlockType.image: ImageBlockSerializer,
        LessonBlockType.gallery: GalleryBlockSerializer,
        LessonBlockType.email: EmailBlockSerializer,
        LessonBlockType.browser: BrowserBlockSerializer,
        LessonBlockType.table: TableBlockSerializer,
        LessonBlockType.doc: DocBlockSerializer,
        LessonBlockType.video: VideoBlockSerializer,
    }

    type = serializers.IntegerField()
    next = serializers.JSONField()
    content = serializers.JSONField()

    def __init__(self, *args, **kwargs):
        super(UnitSerializer, self).__init__(*args, **kwargs)

    def get_unit_content_serializer(self, type_: int):
        lesson_block_type = LessonBlockType(type_)

        return self.LESSON_BLOCK_SERIALIZERS[lesson_block_type]

    def validate_type(self, type_: int) -> int:
        if not LessonBlockType.has_value(type_):
            raise ValidationError(f'type ({type_}) is not specified')

        lesson_block_type = LessonBlockType(type_)

        if lesson_block_type not in self.LESSON_BLOCK_SERIALIZERS:
            raise ValidationError(f'serializator with type {type_} is not specified')

        return type_

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
