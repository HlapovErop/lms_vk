from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from djangoapp.authentication import JWTAuthentication
from djangoapp.decorators import methodologist_required, student_required
from djangoapp.models.course import Course, CourseStateEnum
from djangoapp.models.student_course import StudentCourse, CompletingStateEnum
from djangoapp.models.user import User
from djangoapp.models.user import UserRoleEnum
from djangoapp.serializers.course_serializer import CourseSerializer, SimpleCourseSerializer
from djangoapp.models.lesson import LessonTypeEnum, Lesson
from djangoapp.models.test_type import TestType
from djangoapp.serializers.lesson_serializer import LessonSerializer
from djangoapp.serializers.test_serializer import TestSerializer


@swagger_auto_schema(
    method='post',
    responses={
        201: openapi.Response('Subscribed to the course'),
        200: openapi.Response('Already subscribed'),
        404: openapi.Response('Course not found')
    }
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@student_required
def syllabus(request, pk):
    try:
        course = Course.objects.get(id=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

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


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('Successful retrieval of user courses', SimpleCourseSerializer(many=True)),
        403: openapi.Response('Forbidden')
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def myCourses(request):
    if request.user.role == UserRoleEnum.STUDENT:
        student_courses = StudentCourse.objects.filter(student=request.user)
        courses = [student_course.course for student_course in student_courses]
    elif request.user.role == UserRoleEnum.METHODOLOGIST:
        courses = Course.objects.filter(methodologist=request.user)
    else:
        return HttpResponseForbidden({'error': 'You don\'t have permission to perform this action'})

    serializer = SimpleCourseSerializer(courses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('Successful retrieval of courses', SimpleCourseSerializer(many=True)),
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getCourses(request):
    courses = Course.objects.filter(state=CourseStateEnum.AVAILABLE)
    serializer = SimpleCourseSerializer(courses, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('Successful retrieval of course', SimpleCourseSerializer()),
        404: openapi.Response('Not Found')
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getCourse(request, pk):
    try:
        course = Course.objects.get(id=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    if course.methodologist != request.user and course.state == CourseStateEnum.DRAFT:
        return HttpResponseNotFound()

    serializer = SimpleCourseSerializer(course)
    lessons = Lesson.objects.filter(course=course)
    return Response({'course': serializer.data, 'lessons': LessonSerializer(lessons, many=True).data}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=SimpleCourseSerializer,
    responses={
        201: openapi.Response('Course created successfully', SimpleCourseSerializer),
        422: openapi.Response('Validation error')
    }
)
@api_view(['POST'])
@methodologist_required
@authentication_classes([JWTAuthentication])
def createCourse(request):
    request.data['methodologist'] = request.user.id
    serializer = SimpleCourseSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@swagger_auto_schema(
    method='put',
    request_body=SimpleCourseSerializer,
    responses={
        200: openapi.Response('Course updated successfully', SimpleCourseSerializer),
        403: openapi.Response('Forbidden'),
        422: openapi.Response('Validation error')
    }
)
@api_view(['PUT'])
@methodologist_required
@authentication_classes([JWTAuthentication])
def updateCourse(request, pk):
    try:
        course = Course.objects.get(id=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    if course.methodologist != request.user:
        return HttpResponseForbidden({'error': 'You cannot change this course'})

    serializer = SimpleCourseSerializer(instance=course, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'lesson': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'type': openapi.Schema(type=openapi.TYPE_STRING, description='Lesson type'),
                    # Добавь сюда другие необходимые поля для урока
                }
            ),
            'lesson_index': openapi.Schema(type=openapi.TYPE_INTEGER, description='Index of the lesson')
        }
    ),
    responses={
        201: openapi.Response('Lesson added successfully', LessonSerializer),
        400: openapi.Response('Bad request'),
        403: openapi.Response('Forbidden')
    }
)
@api_view(['POST'])
@methodologist_required
@authentication_classes([JWTAuthentication])
def addLesson(request, pk):
    print('fchgvj')
    try:
        course = Course.objects.get(id=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    print('fchgvjryftyug')

    course_lessons = course.lesson_ids
    lesson_data = request.data['lesson']
    lesson_index = 0
    lesson_data['course'] = course.id
    print('fchgvjgfhkjkkghjk', lesson_data['type'])

    if lesson_data['type'] != LessonTypeEnum.FINAL_TEST:
        print(request.data['lesson_index'])
        lesson_index = request.data['lesson_index']
        if lesson_index is None:
            return HttpResponseBadRequest({'error': 'lesson_index is missing'})

        if not isinstance(lesson_index, int):
            return HttpResponseBadRequest({'error': 'lesson_index must be an integer'})

        if len(course_lessons) < lesson_index:
            return HttpResponseBadRequest({'error': 'You cannot add lesson to this lesson_index'})
    print('fchgvjdcfjvgjbhkjnlkhgjvjfdh')

    if lesson_data['type'] == LessonTypeEnum.LECTURE:
        lesson_serializer = LessonSerializer(data=lesson_data)
        if lesson_serializer.is_valid():
            lesson_instance = lesson_serializer.save()
            lesson_id = lesson_instance.id
            course.lesson_ids.insert(lesson_index, lesson_id)
            course.save()
    elif lesson_data['type'] == LessonTypeEnum.TEST:
        test_type = TestType.objects.get(format=request.data['test']['type'])
        request.data['test']['type'] = test_type.id
        test_serializer = TestSerializer(data=request.data['test'])
        if test_serializer.is_valid():
            test = test_serializer.save()
            lesson_serializer = LessonSerializer(data=lesson_data)
            if lesson_serializer.is_valid():
                lesson_instance = lesson_serializer.save()
                lesson_id = lesson_instance.id
                test.lesson_id = lesson_id
                lesson_instance.test_id = test.id
                lesson_instance.save()
                test.save()
                course.lesson_ids.insert(lesson_index, lesson_id)
                course.save()
            else:
                print(lesson_serializer.errors)
                print(lesson_data)
                return HttpResponseBadRequest("{'error': 'Bad lesson data'}")
        else:
            print(test_serializer.errors)
            print(test_serializer)
            return HttpResponseBadRequest("{'error': 'Bad test data'}")

    return Response(lesson_serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='delete',
    responses={
        204: openapi.Response('Course deleted successfully'),
        403: openapi.Response('Forbidden'),
        404: openapi.Response('Not Found')
    }
)
@api_view(['DELETE'])
@methodologist_required
@authentication_classes([JWTAuthentication])
def deleteCourse(request, pk):
    try:
        course = Course.objects.get(id=pk)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    if course.methodologist != request.user:
        return HttpResponseForbidden({'error': 'You cannot change this course'})

    course.delete()

    return Response('Course successfully deleted!', status=status.HTTP_204_NO_CONTENT)
