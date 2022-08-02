from django.db import models


class TextBlock(models.Model):
    message = models.CharField(max_length=127)
    location = models.IntegerField()

    class Meta:
        abstract = True


class URLBlock(models.Model):
    title = models.CharField(max_length=127)
    url = models.CharField()
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


class GalleryBlock(models.Model):
    location = models.IntegerField()
    images = models.JSONField()


class EmailBlock(TextBlock):
    npc = models.IntegerField()
    subject = models.TextField()
    from_ = models.TextField()
    to = models.TextField()


class BrowserBlock(TextBlock):
    url = models.CharField(max_length=1027)


class TableBlock(URLBlock):
    pass


class DocBlock(TextBlock):
    title = models.TextField()



class VideoBlock(URLBlock):
    pass
