from django.db import models
from django.utils import timezone
from djangoapp.models.user import User
from djangoapp.models.group_course import GroupCourse


class GroupManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class Group(models.Model):
    students = models.ManyToManyField(User, related_name='groups')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(null=True, max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = GroupManager()

    class Meta:
        db_table = 'groups'

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

    def set_course(self, course, passage_time=None):
        group_course, created = GroupCourse.objects.get_or_create(
            group=self,
            course=course
        )
        if created or group_course.passage_time != passage_time:
            group_course.passage_time = passage_time or course.passage_time
            group_course.save()

    def delete_course(self, course):
        try:
            group_course = GroupCourse.objects.get(group=self, course=course)
            group_course.delete()
            return True
        except GroupCourse.DoesNotExist:
            return False
