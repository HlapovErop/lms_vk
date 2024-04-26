from django.db import models
from .user import User


class Notification(models.Model):
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_received')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_sent')
    message = models.CharField(null=True, max_length=300)
    theme = models.URLField(null=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
