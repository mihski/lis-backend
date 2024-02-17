from django.contrib import admin
from .models import Assignment, StudentAssignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)


@admin.register(StudentAssignment)
class StudentAssignmentAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'full_name', 'reviewed', 'score', 'accepted')
    list_filter = ('assignment', 'accepted', 'reviewed')
    search_fields = ('profile__user__last_name', 'profile__user__first_name', 'profile__user__middle_name')
    date_hierarchy = 'completed_date'
    ordering = ('accepted', '-completed_date')
    actions = ['accept_student_assignment', 'reject_student_assignment']

    def full_name(self, obj):
        try:
            return obj.profile.user.get_full_name()
        except Exception:
            return

    full_name.short_description = 'Профиль'

    def accept_student_assignment(self, request, queryset):
        queryset.update(accepted=True)

    accept_student_assignment.short_description = 'Принять выбранные студенческие задания'

    def reject_student_assignment(self, request, queryset):
        queryset.update(accepted=False)

    reject_student_assignment.short_description = 'Отклонить выбранные студенческие задания'
