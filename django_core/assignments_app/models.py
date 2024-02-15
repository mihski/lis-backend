from django.db import models


class Assignment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    max_score = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'


class StudentAssignment(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    answer = models.TextField()
    completed_date = models.DateTimeField(null=True, blank=True, auto_now=True)
    profile = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE,
        related_name="assignments"
    )
    score = models.IntegerField(null=True, blank=True)
    reviewe = models.TextField(null=True, blank=True)
    reviewed = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.profile} - {self.assignment}'

    class Meta:
        unique_together = ('assignment', 'profile')
        verbose_name = 'Student assignment'
        verbose_name_plural = 'Student assignments'