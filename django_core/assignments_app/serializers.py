from rest_framework import serializers

from .models import Assignment, StudentAssignment


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'


class StudentAssignmentSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        attrs['profile'] = self.context['request'].user.profile.first()
        return attrs

    class Meta:
        model = StudentAssignment
        exclude = ('id', 'profile')
        read_only_fields = ('reviewe', 'reviewed', 'accepted', 'completed_date', 'score')
