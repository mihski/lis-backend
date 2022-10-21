from django.contrib import admin

from lessons import models


class LessonAdmin(admin.ModelAdmin):
    model = models.Lesson
    list_display = (
        "id", "local_id", "name", "quest", "time_cost", "money_cost", "energy_cost"
    )
    list_filter = ("local_id",)
    search_fields = ("local_id",)


class UnitAdmin(admin.ModelAdmin):
    model = models.Unit
    list_display = (
        "id", "local_id", "type"
    )
    search_fields = ("local_id", "id")


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "text", "created_at")
    list_filter = ("user", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("id", "user", "created_at")


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "text", "created_at")
    list_filter = ("user", "created_at")
    ordering = ("-created_at",)
    readonly_fields = ("id", "user", "created_at")


admin.site.register(models.Course)
admin.site.register(models.CourseMapImg)
admin.site.register(models.Lesson, LessonAdmin)
admin.site.register(models.LessonBlock)
admin.site.register(models.Unit, UnitAdmin)
admin.site.register(models.NPC)
admin.site.register(models.Location)
admin.site.register(models.ProfileBranchingChoice)
