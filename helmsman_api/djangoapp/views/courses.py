from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from djangoapp.decorators import methodologist_required, student_required
from djangoapp.models.course import Course, CourseStateEnum
from djangoapp.models.student_course import StudentCourse, CompletingStateEnum
from djangoapp.models.user import User
from djangoapp.models.user import UserRoleEnum
from djangoapp.serializers.course_serializer import CourseSerializer
from djangoapp.serializers.lesson_serializer import LessonSerializer
from djangoapp.models.lesson import LessonTypeEnum, Lesson
from djangoapp.models.test_type import TestType
from djangoapp.serializers.lesson_serializer import LessonSerializer


@api_view(['POST'])
@student_required
def syllabus(request, pk):
    course = Course.objects.filter(id=pk)
    student_course, created = StudentCourse.objects.get_or_create(
        student=request.user,
        course=course
    )
    if created:
        student_course.state = CompletingStateEnum.START
        student_course.save()
        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
def myCourses(request):
    if request.user.ROLE == UserRoleEnum.STUDENT:
        student_courses = StudentCourse.objects.filter(student=request.user)
        courses = [student_course.course for student_course in student_courses]
    elif request.user.ROLE == UserRoleEnum.METHODOLOGIST:
        courses = Course.objects.filter(methodologist=request.user)
    else:
        return HttpResponseForbidden({'error': 'You don\'t have permission to perform this action'})

    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def getCourses(request):
    courses = Course.objects.filter(state=CourseStateEnum.AVAILABLE)
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getCourse(request, pk):
    try:
        course = Course.objects.get(id=pk)
    except Course.DoesNotExist:
        return HttpResponseNotFound()

    if course.methodologist != request.user and course.state == CourseStateEnum.DRAFT:
        return HttpResponseNotFound()

    lessons = Lesson.objects.filter(course=course)
    course_serializer = CourseSerializer(course)
    lessons_serializer = LessonSerializer(lessons, many=True)
    course_data = course_serializer.data
    course_data['lessons'] = lessons_serializer.data

    return Response(course_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@methodologist_required
def createCourse(request):
    request.data['methodologist_id'] = request.user.id
    serializer = CourseSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(['PUT'])
@methodologist_required
def updateCourse(request, pk):
    course = User.objects.get(id=pk)
    if course.methodologist != request.user:
        return HttpResponseForbidden({'error': 'You cannot change this course'})

    serializer = CourseSerializer(instance=course, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(['POST'])
@methodologist_required
def addLesson(request, pk):
    course = Course.objects.filter(id=pk)
    course_lessons = course.lesson_ids
    lesson_data = request.data['lesson']
    lesson_index = 0

    if lesson_data['type'] != LessonTypeEnum.FINAL_TEST:
        lesson_index = request.data.get('lesson_index')
        if not lesson_index:
            return HttpResponseBadRequest({'error': 'lesson_index is missing'})

        if not isinstance(lesson_index, int):
            return HttpResponseBadRequest({'error': 'lesson_index must be an integer'})

        if len(course_lessons) < lesson_index:
            return HttpResponseBadRequest({'error': 'You cannot add lesson to this lesson_index'})

    if lesson_data['type'] == LessonTypeEnum.LECTURE:
        lesson_serializer = LessonSerializer(data=lesson_data)
        if lesson_serializer.is_valid():
            lesson_instance = lesson_serializer.save()
            lesson_id = lesson_instance.id
            course.lesson_ids.insert(lesson_index, lesson_id)
            course.save()
    elif lesson_data.type == LessonTypeEnum.TEST:
        test_type = TestType(request.data.get('test_type'))
        test_data = request.data['test']
        test_type = request.data['test_type']


@api_view(['DELETE'])
@methodologist_required
def deleteCourse(request, pk):
    course = Course.objects.get(id=pk)
    if course.methodologist != request.user:
        return HttpResponseForbidden({'error': 'You cannot change this course'})

    course.delete()

    return Response('Course successfully deleted!', status=status.HTTP_204_NO_CONTENT)
