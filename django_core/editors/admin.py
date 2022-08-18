from django.contrib import admin
from editors import models


class EditorSessionAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'local_id', 'get_content', 'user', 'course')

    def get_content(self, obj):
        return obj.get_content()


admin.site.register(models.EditorSession, EditorSessionAdmin)
