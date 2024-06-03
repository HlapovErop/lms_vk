from django.http import HttpResponseForbidden, HttpResponseNotFound
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from djangoapp.authentication import JWTAuthentication
from djangoapp.decorators import teacher_required, teacher_or_admin_required
from djangoapp.models.course import Course, CourseStateEnum
from djangoapp.models.group import Group
from djangoapp.models.user import User
from djangoapp.models.user import UserRoleEnum
from djangoapp.serializers.group_serializer import GroupSerializer


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



@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getGroup(request, pk):
    group = Group.objects.get(pk=pk)

    if group.teacher == request.user or request.user in group.students:
        return Response(groupData(group))
    else:
        return HttpResponseNotFound({'error': 'You do not have permission to perform this action.'})


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


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@teacher_required
def addStudents(request, pk):
    group = Group.objects.get(id=pk)
    if request.user != group.teacher:
        return HttpResponseForbidden({'error': 'You cannot change this group'})

    students_to_add = User.objects.filter(role=UserRoleEnum.STUDENT, id=request.data['student_ids'])
    if students_to_add:
        group.students.add(*students_to_add)
        return Response(groupData(group))
    else:
        return HttpResponseNotFound({'error': 'Students not found'})


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@teacher_required
def deleteStudents(request, pk):
    group = Group.objects.get(id=pk)
    if request.user != group.teacher and not request.user.is_admin():
        return HttpResponseForbidden({'error': 'You cannot change this group'})

    students_to_add = User.objects.filter(role=UserRoleEnum.STUDENT, id=request.data['student_ids'])
    if students_to_add:
        group.students.remove(*students_to_add)
        return Response(groupData(group))
    else:
        return HttpResponseNotFound({'error': 'Students not found'})

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

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@teacher_or_admin_required
def deleteGroup(request, pk):
    group = Group.objects.get(id=pk)

    if request.user != group.teacher and not request.user.is_admin():
        return HttpResponseForbidden({'error': 'You cannot change this group'})

    group.delete()

    return Response('User successfully deleted!', status=status.HTTP_204_NO_CONTENT)

def groupData(group):
    group_serializer = GroupSerializer(group, many=False)
    student_ids = list(group.students.values_list('id', flat=True))
    course_ids = list(group.group_courses.values_list('course_id', flat=True))

    return group_serializer.data.update({'student_ids': student_ids, 'course_ids': course_ids})
