from django.contrib import admin
from .models import Assignment, StudentAssignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')


@admin.register(StudentAssignment)
class StudentAssignmentAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'profile', 'reviewed', 'score', 'accepted')
    list_filter = ('assignment', 'accepted', 'reviewed')
    search_fields = ('assignment', 'profile')
    date_hierarchy = 'completed_date'
    ordering = ('accepted', '-completed_date')
    actions = ['accept_student_assignment', 'reject_student_assignment']

    def accept_student_assignment(self, request, queryset):
        queryset.update(accepted=True)

    accept_student_assignment.short_description = 'Accept selected student assignments'

    def reject_student_assignment(self, request, queryset):
        queryset.update(accepted=False)

    reject_student_assignment.short_description = 'Reject selected student assignments'
