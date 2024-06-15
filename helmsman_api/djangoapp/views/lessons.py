from django.http import HttpResponseForbidden, HttpResponseNotFound
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from djangoapp.decorators import student_required
from djangoapp.authentication import JWTAuthentication
from djangoapp.models.course import Course, CourseStateEnum
from djangoapp.models.user import User
from djangoapp.utils.question_preparator import QuestionPreparator
from djangoapp.serializers.course_serializer import CourseSerializer
from djangoapp.models.lesson import Lesson, LessonTypeEnum
from djangoapp.models.student_lesson import StudentLesson, CompletingStateEnum
from djangoapp.serializers.lesson_serializer import LessonSimpleSerializer
from djangoapp.serializers.test_serializer import TestSerializer
from djangoapp.utils.comparator import compare_json


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getLesson(request, pk):
    try:
        lesson = Lesson.objects.get(id=pk)
        student_lesson = StudentLesson.objects.get(lesson=lesson, student=request.user)
    except StudentLesson.DoesNotExist:
        return HttpResponseForbidden("{'error': 'You cannot get this lesson'}")
    except Lesson.DoesNotExist:
        return HttpResponseNotFound("{'error': 'Lesson not found'}")
    lesson_serializer = LessonSimpleSerializer(instance=lesson)
    response_json = {'state': student_lesson.state, 'lesson': lesson_serializer.data}
    if lesson.test:
        test = lesson.test
        QuestionPreparator.prepare_question(test)
        test_serializer = TestSerializer(instance=test)
        response_json['test'] = test_serializer.data
    return Response(response_json)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@student_required
def solve(request, pk):
    try:
        lesson = Lesson.objects.get(id=pk)
        student_lesson = StudentLesson.objects.get(lesson=lesson, student=request.user, state=CompletingStateEnum.ON_WAY)
    except StudentLesson.DoesNotExist:
        return HttpResponseForbidden("{'error': 'You cannot solve this lesson'}")
    except Lesson.DoesNotExist:
        return HttpResponseNotFound("{'error': 'Lesson not found'}")

    student_lesson.attempt += 1

    if lesson.type == LessonTypeEnum.LECTURE:
        student_lesson.state = CompletingStateEnum.FINISHED
        open_next_lesson(lesson, request.user)
    else:
        if compare_json(lesson.test.template_data, request.data['template_data']):
            open_next_lesson(lesson, request.user)
            student_lesson.state = CompletingStateEnum.FINISHED
        else:
            student_lesson.last_answer = request.data['template_data']
            if student_lesson.attempt == lesson.limit:
                student_lesson.state = CompletingStateEnum.FAILED
    student_lesson.save()

    return Response({'state': student_lesson.state, 'lesson': LessonSimpleSerializer(instance=lesson).data},
                    status=status.HTTP_200_OK)


def open_next_lesson(lesson, user):
    course = lesson.course
    lesson_index = course.lesson_ids.index(lesson.id)
    if lesson_index + 1 < len(course.lesson_ids):
        next_lesson = Lesson.objects.get(id=course.lesson_ids[lesson_index + 1])
        StudentLesson.objects.get_or_create(
            student=user,
            lesson=next_lesson,
            state=CompletingStateEnum.ON_WAY,
            attempt=0
        )
