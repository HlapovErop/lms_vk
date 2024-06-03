from django.http import HttpResponseForbidden, HttpResponseNotFound
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from djangoapp.authentication import JWTAuthentication
from djangoapp.decorators import methodologist_required, student_required
from djangoapp.models.course import Course, CourseStateEnum
from djangoapp.models.student_course import StudentCourse, CompletingStateEnum
from djangoapp.models.user import User
from djangoapp.models.user import UserRoleEnum
from djangoapp.serializers.course_serializer import CourseSerializer

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getCourses(request):
    courses = Course.objects.filter(state=CourseStateEnum.AVAILABLE)
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getCourse(request, pk):
    course = Course.objects.filter(id=pk)

    if course.methodologist != request.user and course.state == CourseStateEnum.DRAFT:
        return HttpResponseNotFound()

    serializer = CourseSerializer(course, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
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
@authentication_classes([JWTAuthentication])
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


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@methodologist_required
def deleteCourse(request, pk):
    course = Course.objects.get(id=pk)
    if course.methodologist != request.user:
        return HttpResponseForbidden({'error': 'You cannot change this course'})

    course.delete()

    return Response('Course successfully deleted!', status=status.HTTP_204_NO_CONTENT)
