from django.http import HttpResponseForbidden, HttpResponseNotFound
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from djangoapp.authentication import JWTAuthentication
from djangoapp.decorators import teacher_required, teacher_or_admin_required
from djangoapp.models.course import Course, CourseStateEnum
from djangoapp.models.group import Group
from djangoapp.models.user import User
from djangoapp.models.user import UserRoleEnum
from djangoapp.serializers.group_serializer import GroupSerializer


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('Successful retrieval of group list', GroupSerializer(many=True)),
        403: openapi.Response('Forbidden')
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getGroups(request):
    if request.user.role == UserRoleEnum.TEACHER:
        groups = Group.objects.filter(teacher=request.user)
    elif request.user.role == UserRoleEnum.STUDENT:
        groups = Group.objects.filter(students=request.user)
    elif request.user.role == UserRoleEnum.ADMIN:
        groups = Group.objects.all()
    else:
        return HttpResponseForbidden({'error': 'You do not have permission to perform this action.'})
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('Successful retrieval of group data', GroupSerializer()),
        404: openapi.Response('Not Found')
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getGroup(request, pk):
    group = Group.objects.get(pk=pk)

    if group.teacher == request.user or request.user in group.students:
        return Response(groupData(group))
    else:
        return HttpResponseNotFound({'error': 'You do not have permission to perform this action.'})


@swagger_auto_schema(
    method='post',
    request_body=GroupSerializer,
    responses={
        201: openapi.Response('Group created successfully', GroupSerializer),
        422: openapi.Response('Validation error')
    }
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@teacher_required
def createGroup(request):
    request.data['teacher_id'] = request.user.id
    serializer = GroupSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@swagger_auto_schema(
    method='put',
    request_body=GroupSerializer,
    responses={
        200: openapi.Response('Group updated successfully', GroupSerializer),
        403: openapi.Response('Forbidden'),
        422: openapi.Response('Validation error')
    }
)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@teacher_or_admin_required
def updateGroup(request, pk):
    group = Group.objects.get(id=pk)
    if request.user != group.teacher and not request.user.is_admin():
        return HttpResponseForbidden({'error': 'You cannot change this group'})

    serializer = GroupSerializer(group, data=request.data)

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
            'student_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))
        }
    ),
    responses={
        200: openapi.Response('Students added successfully', GroupSerializer),
        403: openapi.Response('Forbidden'),
        404: openapi.Response('Students not found')
    }
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@teacher_required
def addStudents(request, pk):
    group = Group.objects.get(id=pk)
    if request.user != group.teacher:
        return HttpResponseForbidden({'error': 'You cannot change this group'})

    students_to_add = User.objects.filter(role=UserRoleEnum.STUDENT, id__in=request.data['student_ids'])
    if students_to_add:
        group.students.add(*students_to_add)
        return Response(groupData(group))
    else:
        return HttpResponseNotFound({'error': 'Students not found'})


@swagger_auto_schema(
    method='delete',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'student_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))
        }
    ),
    responses={
        200: openapi.Response('Students deleted successfully', GroupSerializer),
        403: openapi.Response('Forbidden'),
        404: openapi.Response('Students not found')
    }
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@teacher_required
def deleteStudents(request, pk):
    group = Group.objects.get(id=pk)
    if request.user != group.teacher and not request.user.is_admin():
        return HttpResponseForbidden({'error': 'You cannot change this group'})

    students_to_delete = User.objects.filter(role=UserRoleEnum.STUDENT, id__in=request.data['student_ids'])
    if students_to_delete:
        group.students.remove(*students_to_delete)
        return Response(groupData(group))
    else:
        return HttpResponseNotFound({'error': 'Students not found'})


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'courses': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_OBJECT, properties={
                    'course_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'passage_time': openapi.Schema(type=openapi.TYPE_STRING)
                })
            )
        }
    ),
    responses={
        200: openapi.Response('Courses added successfully', GroupSerializer),
        403: openapi.Response('Forbidden')
    }
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@teacher_required
def addCourses(request, pk):
    group = Group.objects.get(id=pk)
    not_founded_courses = []

    if request.user != group.teacher:
        return HttpResponseForbidden({'error': 'You cannot change this group'})

    for course_data in request.data['courses']:
        try:
            course = Course.objects.get(id=course_data['course_id'], state=CourseStateEnum.AVAILABLE)
            group.set_course(course, course_data['passage_time'])
        except Course.DoesNotExist:
            not_founded_courses.append(course_data['course_id'])

    return Response({'course': groupData(group), 'not_founded_courses': not_founded_courses}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'course_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))
        }
    ),
    responses={
        200: openapi.Response('Courses deleted successfully', GroupSerializer),
        403: openapi.Response('Forbidden')
    }
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@teacher_required
def deleteCourses(request, pk):
    group = Group.objects.get(id=pk)
    not_founded_courses = []

    if request.user != group.teacher:
        return HttpResponseForbidden({'error': 'You cannot change this group'})

    for course_id in request.data['course_ids']:
        try:
            course = Course.objects.get(id=course_id)
            group.delete_course(course)
        except Course.DoesNotExist:
            not_founded_courses.append(course_id)

    return Response({'course': groupData(group), 'not_founded_courses': not_founded_courses}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='delete',
    responses={
        204: openapi.Response('Group deleted successfully'),
        403: openapi.Response('Forbidden')
    }
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@teacher_or_admin_required
def deleteGroup(request, pk):
    group = Group.objects.get(id=pk)

    if request.user != group.teacher and not request.user.is_admin():
        return HttpResponseForbidden({'error': 'You cannot change this group'})

    group.delete()

    return Response('Group successfully deleted!', status=status.HTTP_204_NO_CONTENT)


def groupData(group):
    group_serializer = GroupSerializer(group, many=False)
    student_ids = list(group.students.values_list('id', flat=True))
    course_ids = list(group.group_courses.values_list('course_id', flat=True))

    return group_serializer.data.update({'student_ids': student_ids, 'course_ids': course_ids})
