from django.contrib import admin

from lessons import models


admin.site.register(models.Question)
admin.site.register(models.QuestionType)
