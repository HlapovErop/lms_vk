from django.db import models


class TestType(models.Model):
    template = models.JSONField(blank=True, default=dict)
    format = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'test_types'
