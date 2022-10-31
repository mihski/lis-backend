from django.contrib import admin

from lessons import models


@admin.register(models.Lesson)
class LessonAdmin(admin.ModelAdmin):
    model = models.Lesson
    list_display = (
        "id", "local_id", "name", "quest", "time_cost", "money_cost", "energy_cost"
    )
    list_filter = ("time_cost", "money_cost", "energy_cost")
    search_fields = (
        "local_id",
        "name",
        "quest__name",
        "quest__local_id",
        "course__name"
    )


@admin.register(models.Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("id", "local_id", "type")
    list_filter = ("type",)
    search_fields = ("local_id",)


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "text", "created_at")
    list_filter = ("user", "created_at")
    search_fields = ("user__username",)
    ordering = ("-created_at",)
    readonly_fields = ("id", "user", "created_at")


@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "text", "created_at")
    list_filter = ("user", "created_at")
    search_fields = ("user__username",)
    ordering = ("-created_at",)
    readonly_fields = ("id", "user", "created_at")


@admin.register(models.Branching)
class BranchingAdmin(admin.ModelAdmin):
    list_display = ("id","local_id", "course", "quest", "type", "content")
    list_filter = ("course", "quest", "type")
    search_fields = (
        "local_id",
        "quest__name",
        "quest__local_id"
        "course__name",
        "type"
    )


@admin.register(models.ProfileBranchingChoice)
class SelectBranchingAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "branching", "choose_local_id")
    list_filter = ("profile", "branching")
    search_fields = (
        "profile__username",
        "branching__quest__name",
        "branching__quest__local_id",
        "branching__course__name",
        "branching__local_id",
        "branching__type"
    )


@admin.register(models.Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ("id", "local_id", "course", "name", "entry", "next")
    list_filter = ("local_id", "course")
    search_fields = ("local_id", "course__name")


@admin.register(models.NPC)
class NPCAdmin(admin.ModelAdmin):
    list_display = ("id", "uid", "ru_name", "gender", "age", "is_scientific_director")
    list_filter = ("gender", "age", "is_scientific_director")
    search_fields = ("ru_name", "en_name", "uid")


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "uid", "ru_name")
    list_filter = ("uid",)
    search_fields = ("uid", "ru_name", "eu_name")


@admin.register(models.ProfileLessonDone)
class ProfileLessonsDoneAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "lesson")
    list_filter = ("profile", "lesson")
    search_fields = (
        "profile__username",
        "lesson__name",
        "lesson__local_id"
    )


@admin.register(models.UnitAffect)
class UnitAffectAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "content")
    list_filter = ("code",)


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_editable", "entry")
    list_filter = ("name", "is_editable")
    search_fields = ("name",)


@admin.register(models.CourseMapImg)
class CourseMapImgAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "order")
    list_filter = ("course",)
    search_fields = ("course__name",)


class LessonInline(admin.TabularInline):
    model = models.Lesson


@admin.register(models.LessonBlock)
class LessonBlockAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ("id", "entry")
    search_fields = ("id", "entry")
