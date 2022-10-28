from django.contrib import admin

from lessons import models


@admin.register(models.Lesson)
class LessonAdmin(admin.ModelAdmin):
    model = models.Lesson
    list_display = (
        "id", "local_id", "name", "quest", "time_cost", "money_cost", "energy_cost"
    )
    list_filter = ("local_id",)
    search_fields = ("local_id",)


@admin.register(models.Unit)
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


@admin.register(models.Branching)
class BranchingAdmin(admin.ModelAdmin):
    list_display = ("id","local_id", "course", "quest", "type", "content")
    list_filter = ("course", "quest", "type")
    search_fields = ("local_id", "quest__name", "course__name", "type")


@admin.register(models.ProfileBranchingChoice)
class SelectBranchingAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "branching", "choose_local_id")
    list_filter = ("profile", "branching")
    search_fields = ("profile__username", "quest__name", "course__name", "type")


@admin.register(models.Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ("id", "local_id", "course", "name", "entry", "next")
    list_filter = ("local_id", "course")
    search_fields = ("local_id", "course__name")


admin.site.register(models.Course)
admin.site.register(models.CourseMapImg)
admin.site.register(models.LessonBlock)
admin.site.register(models.NPC)
admin.site.register(models.Location)
admin.site.register(models.ProfileLessonDone)
admin.site.register(models.UnitAffect)
