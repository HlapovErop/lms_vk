from django.http import HttpResponseForbidden
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from djangoapp.authentication import JWTAuthentication
from djangoapp.models.course import Course, CourseStateEnum
from djangoapp.models.user import User
from djangoapp.utils.question_preparator import QuestionPreparator
from djangoapp.serializers.course_serializer import CourseSerializer
from djangoapp.models.lesson import Lesson
from djangoapp.models.student_lesson import StudentLesson
from djangoapp.serializers.lesson_serializer import LessonSerializer
from djangoapp.serializers.test_serializer import TestSerializer


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getLesson(request, pk):
    student_lesson = StudentLesson.objects.get(id=pk, user=request.user)
    if student_lesson is None:
        return HttpResponseForbidden({'error': 'You cannot get this lesson'})
    lesson = Lesson.objects.get(id=pk)
    lesson_serializer = LessonSerializer(instance=lesson)

    if lesson.test:
        test = lesson.test
        QuestionPreparator.prepare_question(test)
        test_serializer = TestSerializer(instance=test)
    return Response({'status': student_lesson.state, 'lesson': lesson_serializer.data, 'test': test_serializer.data})

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def solve(request, pk):
    course = User.objects.get(id=pk)
    if course.methodologist != request.user:
        return HttpResponseForbidden({'error': 'You cannot change this course'})

    serializer = CourseSerializer(instance=course, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

