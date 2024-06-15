from django.db import models
from .user import User
from .lesson import Lesson


class CompletingStateEnum:
    ON_WAY = 1
    FINISHED = 2
    FAILED = 3


class StudentLesson(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.PositiveSmallIntegerField(choices=[
        (CompletingStateEnum.ON_WAY, 'On way'),
        (CompletingStateEnum.FINISHED, 'Finished'),
        (CompletingStateEnum.FAILED, 'Failed')
    ])
    attempt = models.PositiveSmallIntegerField()
    last_answer = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'students_lessons'
