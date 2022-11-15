from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin

from accounts import models


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password'),
        }),
    )
    list_display = ('email', 'username', 'is_superuser')
    list_filter = ('is_superuser', )
    search_fields = ('email', 'username')
    ordering = ('email', )


@admin.register(models.Statistics)
class StatisticsAdmin(ImportExportModelAdmin):
    list_display = ("id", "profile", "quests_done", "lessons_done", "total_time_spend")
    list_filter = ("quests_done", "lessons_done", "total_time_spend")
    search_fields = ("profile__user__username",)
    ordering = list_filter


@admin.register(models.UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_filter = ("name",)


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "isu",
        "user",
        "course",
        "gender",
        "university_position",
        "ultimate_activated",
        "scientific_director",
        "laboratory"
    )
    list_filter = (
        "gender",
        "university_position",
        "ultimate_activated",
        "scientific_director",
        "laboratory"
    )
    search_fields = ("username", "user__username", "isu")


@admin.register(models.ScientificDirector)
class ScientificDirectorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    list_filter = ("name",)
    search_fields = ("name",)

admin.site.register(models.ProfileAvatarHead)
admin.site.register(models.ProfileAvatarHair)
admin.site.register(models.ProfileAvatarFace)
admin.site.register(models.ProfileAvatarBrows)
admin.site.register(models.ProfileAvatarClothes)
