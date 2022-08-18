import django_filters.rest_framework as filters

from editors.models import EditorSession


class CharListFilter(filters.Filter):
    def filter(self, qs, value):
        if value is not None:
            local_ids = [v for v in value.split(',')]
            return qs.filter(**{'{0}__{1}'.format(self.field_name, self.lookup_expr): local_ids})

        return qs


class EditorSessionFilter(filters.FilterSet):
    course = filters.NumberFilter(field_name='course__id', lookup_expr='exact')
    local_ids = CharListFilter(field_name='local_id', lookup_expr='in')

    class Meta:
        model = EditorSession
        fields = ['course', 'local_ids']
