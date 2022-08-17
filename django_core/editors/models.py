from django.db import models
from django.conf import settings
from lessons.models import Course, Lesson, Quest


class Block(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()
    type = models.IntegerField()
    body_id = models.IntegerField()


class EditorSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    local_id = models.CharField(max_length=255, null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now=True)

    def get_content(self):
        if not self.local_id:
            return

        lesson = Lesson.objects.filter(local_id=self.local_id).first()

        if lesson:
            return lesson

        return Quest.objects.get(local_id=self.local_id)

    def __str__(self):
        prefix = '' if not self.local_id else '- ' + str(self.get_content())

        return f"EditorSession[{self.id}] {self.user} - {self.course} {prefix}"

    class Meta:
        unique_together = ['course', 'local_id']
