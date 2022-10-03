from django.contrib import admin

from lessons import models


class UnitAdmin(admin.ModelAdmin):
    model = models.Unit
    list_display = (
        'id', 'local_id', 'type'
    )
    search_fields = ('local_id', 'id')
admin.site.register(models.Course)
admin.site.register(models.Lesson)
admin.site.register(models.LessonBlock)
admin.site.register(models.Unit, UnitAdmin)
admin.site.register(models.NPC)
admin.site.register(models.Location)
