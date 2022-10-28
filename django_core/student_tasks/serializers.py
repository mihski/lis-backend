from rest_framework import serializers

from lessons.structures.tasks import TaskBlock
from accounts.models import Profile
from lessons.models import Unit
from student_tasks.models import StudentTaskAnswer


class StudentTaskAnswerSerializer(serializers.ModelSerializer):
    is_correct = serializers.ReadOnlyField()
    details = serializers.SerializerMethodField()

    class Meta:
        model = StudentTaskAnswer
        fields = ["id", "answer", "is_correct", "details"]

    def _get_task(self, task_unit: Unit) -> TaskBlock:
        task_models = {t_model.type.value: t_model for t_model in TaskBlock.get_all_subclasses()}
        task_model = task_models[task_unit.type]
        task_instance = task_model.objects.filter(id=task_unit.content['id']).only().first()

        return task_instance

    def _get_profile(self, task_unit: Unit) -> Profile:
        # TODO: add course field for profile
        profile: Profile = self.context['request'].user.profile.get()
        return profile

    def get_details(self, obj: StudentTaskAnswer) -> dict:
        task_instance = self._get_task(obj.task)
        return task_instance.get_details(obj.answer)

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        task_block = self._get_task(instance.task)
        profile = self._get_profile(instance.task)

        is_correct = task_block.check_answer(validated_data['answer'])

        instance.profile = profile
        instance.is_correct = is_correct
        instance.save()

        return instance
