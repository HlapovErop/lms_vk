from django.db import models
from .user import User
from .course import Course


class CompletingStateEnum:
    START = 1
    ON_WAY = 2
    FINISHED = 3
    FAILED = 4


class StudentCourse(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.PositiveSmallIntegerField(choices=[
        (CompletingStateEnum.START, 'Start'),
        (CompletingStateEnum.ON_WAY, 'On way'),
        (CompletingStateEnum.FINISHED, 'Finished'),
        (CompletingStateEnum.FAILED, 'Failed')
    ])
    begin_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'students_courses'
