from django.db import models


class Block(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()
    type = models.IntegerField()
    body = models.JSONField()
