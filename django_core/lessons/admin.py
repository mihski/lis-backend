from django.contrib import admin

from lessons import models


admin.site.register(models.Course)
admin.site.register(models.Quest)
admin.site.register(models.Lesson)
admin.site.register(models.LessonBlock)
admin.site.register(models.Unit)
admin.site.register(models.Branching)
