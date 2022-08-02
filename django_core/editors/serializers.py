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


class TextBlockSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['message', 'location']


class UrlBlockSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['title', 'url', 'location']


class ReplicaBlockSerializer(TextBlockSerializer):
    class Meta:
        model = ReplicaBlock
        fields = ['emotions'] + TextBlockSerializer.Meta.fields


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
            return False

        for image in images:
            if len(image) != 2 or any(field not in image for field in ['title', 'url']):
                raise ValidationError(f'You should specify both title and url: {image}')

        return True


class EmailBlockSerializer(TextBlockSerializer):
    class Meta:
        model = EmailBlock
        fields = ['npc', 'subject', 'from', 'to'] + TextBlockSerializer.Meta.fields

    def get_from(self, obj: EmailBlock):
        return obj.from_


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
