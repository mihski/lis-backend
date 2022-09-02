from rest_framework import serializers

from accounts.models import User
from lessons.structures.tasks import TaskBlock
from student_tasks.models import StudentTaskAnswer


class StudentTaskAnswerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    is_correct = serializers.ReadOnlyField()

    class Meta:
        model = StudentTaskAnswer
        fields = "__all__"

    def _get_task(self, task_unit):
        task_models = {t_model.type.value: t_model for t_model in TaskBlock.get_all_subclasses()}
        task_model = task_models[task_unit.type]
        task_instance = task_model.objects.filter(id=task_unit.content['id']).only().first()

        return task_instance

    def _check_task(self, task_unit, answer):
        task_instance = self._get_task(task_unit)
        return task_instance.check_answer(answer)

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.is_correct = self._check_task(instance.task, validated_data['answer'])
        instance.save()

        return instance
