from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

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
    list_display = ('email', 'is_superuser')
    list_filter = ('is_superuser', )
    search_fields = ('email', )
    ordering = ('email', )


admin.site.register(models.UserRole)
admin.site.register(models.Profile)
admin.site.register(models.ScientificDirector)
