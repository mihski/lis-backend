from django.db import models


class LessonBlock(models.Model):
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
    sender = models.TextField()
    to = models.TextField()


class BrowserBlock(TextBlock):
    url = models.CharField(max_length=1027)


class TableBlock(URLBlock):
    pass


class DocBlock(TextBlock):
    title = models.TextField()


class VideoBlock(URLBlock):
    pass


class MessengerStartBlock(LessonBlock):
    pass


class MessengerEndBlock(LessonBlock):
    pass


class DownloadingBlock(LessonBlock):
    title = models.CharField(max_length=120)
    url = models.CharField(max_length=2047)
    location = models.IntegerField()


class ButtonBlock(LessonBlock):
    """ A16 """
    value = models.CharField(max_length=255)


class DayCounterBlock(LessonBlock):
    location = models.IntegerField()
    value = models.IntegerField()
