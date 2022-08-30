from rest_framework import serializers
from student_tasks.models import StudentTaskAnswer


class StudentTaskAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTaskAnswer
        fields = "__all__"

    def update(self, instance, validated_data):
        pass
