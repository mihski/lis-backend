from django.contrib import admin

from student_tasks.models import StudentTaskAnswer


@admin.register(StudentTaskAnswer)
class StudentTaskAnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "task", "answer", "is_correct")
    list_filter = ("is_correct", "profile", "task")
    search_fields = ("profile__username", "task__local_id")
