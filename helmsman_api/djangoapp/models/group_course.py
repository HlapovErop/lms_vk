from django.db import models


class GroupCourse(models.Model):

    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='group_courses')
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='group_courses')

    passage_time = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = 'groups_courses'