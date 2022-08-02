from django.db import models
from lessons.models import Lesson


class LessonBlock(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class TextBlock(LessonBlock):
    message = models.CharField(max_length=127)
    location = models.IntegerField()

    class Meta:
        abstract = True


class URLBlock(LessonBlock):
    title = models.CharField(max_length=127)
    url = models.CharField(max_length=127)
    location = models.IntegerField()

    class Meta:
        abstract = True


class ReplicaBlock(TextBlock):
    """ A0 """
    emotion = models.IntegerField()


class ReplicaNPCBlock(ReplicaBlock):
    npc = models.IntegerField()


class TheoryBlock(TextBlock):
    pass


class ImportantBlock(TextBlock):
    pass


class QuoteBlock(TextBlock):
    pass


class ImageBlock(URLBlock):
    pass


class GalleryBlock(LessonBlock):
    location = models.IntegerField()
    images = models.JSONField()


class EmailBlock(TextBlock):
    npc = models.IntegerField()
    subject = models.TextField()
    f_from = models.TextField()
    to = models.TextField()


class BrowserBlock(TextBlock):
    url = models.CharField(max_length=1027)


class TableBlock(URLBlock):
    pass


class DocBlock(TextBlock):
    title = models.TextField()


class VideoBlock(URLBlock):
    pass
