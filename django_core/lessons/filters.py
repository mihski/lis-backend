import django_filters.rest_framework as filters
from django.db.models import QuerySet

from lessons.models import Lesson


class LessonBlockFilter(filters.FilterSet):
    from_unit_id = filters.CharFilter(method="get_units_from_id")

    def get_units_from_id(self, queryset: QuerySet, *args, **kwargs):
        pass

    class Meta:
        model = Lesson
        fields = ['from_unit_id']
