from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin

from accounts import models


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password'),
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


admin.site.register(models.UserRole)
admin.site.register(models.Profile)
admin.site.register(models.ScientificDirector)
admin.site.register(models.ProfileAvatarHead)
admin.site.register(models.ProfileAvatarHair)
admin.site.register(models.ProfileAvatarFace)
admin.site.register(models.ProfileAvatarBrows)
admin.site.register(models.ProfileAvatarClothes)
