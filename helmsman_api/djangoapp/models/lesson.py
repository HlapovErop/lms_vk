from django.db import models
from django.utils import timezone
from djangoapp.models.test import Test
from djangoapp.models.course import Course
from django.contrib.postgres.fields import ArrayField


class LessonTypeEnum:
    LECTURE = 1
    TEST = 2
    FINAL_TEST = 3

class LessonManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class Lesson(models.Model):
    test = models.ForeignKey(Test, null=True, on_delete=models.SET_NULL)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(null=True, max_length=250)
    limit = models.PositiveIntegerField(null=True)
    content = models.TextField(null=True)
    type = models.PositiveSmallIntegerField(choices=[
        (LessonTypeEnum.LECTURE, 'Lecture'),
        (LessonTypeEnum.TEST, 'Test'),
        (LessonTypeEnum.FINAL_TEST, 'Final test')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = LessonManager()

    class Meta:
        db_table = 'lessons'

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def is_active(self):
        return self.deleted_at is None

