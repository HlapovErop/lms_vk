from django.db import models
from djangoapp.models.test_type import TestType


class Test(models.Model):
    type = models.ForeignKey(TestType, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    template_data = models.JSONField(blank=True, default=dict)
    error_comment = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tests'