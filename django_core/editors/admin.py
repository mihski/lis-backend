from django.contrib import admin
from editors import models


class EditorSessionAdmin(admin.ModelAdmin):
    list_filter = ('is_closed', )
    readonly_fields = ('created_at', 'local_id', 'get_content', 'user', 'course')

    def get_content(self, obj):
        return obj.get_content()

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(models.EditorSession, EditorSessionAdmin)
