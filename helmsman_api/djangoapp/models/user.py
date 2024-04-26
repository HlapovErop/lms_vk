from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password


class UserRoleEnum:
    ADMIN = 1
    METHODOLOGIST = 2
    TEACHER = 3
    STUDENT = 4


class UserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at=None)


class User(models.Model):
    name = models.CharField(max_length=250)
    username = models.CharField(max_length=250, unique=True)
    email = models.CharField(null=True, max_length=250)
    photo = models.URLField(null=True, max_length=250)
    password = models.CharField(max_length=128)
    role = models.PositiveSmallIntegerField(choices=[
        (UserRoleEnum.ADMIN, 'Admin'),
        (UserRoleEnum.METHODOLOGIST, 'Methodologist'),
        (UserRoleEnum.TEACHER, 'Teacher'),
        (UserRoleEnum.STUDENT, 'Student')
    ])
    temporary_code = models.CharField(null=True, max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

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

    def is_admin(self):
        return self.role == UserRoleEnum.ADMIN

    def __str__(self):
        return self.username
