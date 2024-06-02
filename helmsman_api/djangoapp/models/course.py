from django.db import models
from django.utils import timezone
from djangoapp.models.user import User
from django.contrib.postgres.fields import ArrayField


class CourseStateEnum:
    DRAFT = 1
    AVAILABLE = 2
    ARCHIVED = 3


class CourseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class Course(models.Model):
    methodologist = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.CharField(null=True, max_length=50)
    state = models.PositiveSmallIntegerField(choices=[
        (CourseStateEnum.DRAFT, 'Draft'),
        (CourseStateEnum.AVAILABLE, 'Available'),
        (CourseStateEnum.ARCHIVED, 'Archived'),
    ])
    categories = ArrayField(models.TextField(), blank=True, default=list)
    default_passage_time = models.IntegerField(null=True)
    description = models.TextField(null=True)
    lesson_ids = ArrayField(models.TextField(), blank=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = CourseManager()

    class Meta:
        db_table = 'courses'

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

