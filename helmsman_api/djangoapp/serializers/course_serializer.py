from rest_framework import serializers
from djangoapp.models.course import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class SimpleCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ['created_at', 'updated_at', 'deleted_at']
