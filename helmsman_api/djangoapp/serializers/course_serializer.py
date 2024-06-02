from rest_framework import serializers
from djangoapp.serializers.lesson_serializer import LessonSerializer
from djangoapp.models.course import Course

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
