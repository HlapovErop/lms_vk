from django.contrib.auth.hashers import check_password
from django.http import HttpResponseForbidden
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from djangoapp.authentication import JWTAuthentication
from djangoapp.decorators import admin_required
from djangoapp.models.group import Group
from djangoapp.models.user import User
from djangoapp.models.user import UserRoleEnum
from djangoapp.serializers.user_serializer import UserSerializer
from djangoapp.utils.decoders import generate_jwt_token


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=status.HTTP_400_BAD_REQUEST)
 
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'Invalid username'},
                        status=status.HTTP_401_UNAUTHORIZED)

    if not check_password(password, user.password):
        return Response({'error': 'Invalid password'},
                        status=status.HTTP_401_UNAUTHORIZED)

    token, date = generate_jwt_token(user.id)

    return Response({'token': token, 'end_time': date}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getUsers(request):
    if request.user.is_admin():
        users = User.objects.all()
    elif request.user.role == UserRoleEnum.TEACHER:
        users = set()
        teacher_groups = Group.objects.filter(teacher=request.user)
        for group in teacher_groups:
            users.update(group.students.all())
        users = list(users)
    else:
        users = User.objects.filter(role__in=request.user)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getUser(request, pk):
    users = User.objects.get(id=pk)
    serializer = UserSerializer(users, many=False)
    return Response(serializer.data)


@api_view(['POST'])
def createUser(request):
    if request.data['role'] == UserRoleEnum.ADMIN and not request.user.is_admin():
        return HttpResponseForbidden({'error': 'you cannot set admin role'})

    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
def updateUser(request, pk):
    user = User.objects.get(id=pk)
    if request.user.id != user.id and not request.user.is_admin():
        return HttpResponseForbidden({'error': 'You cannot change another user'})

    if request.data['role'] == UserRoleEnum.ADMIN and not request.user.is_admin():
        return HttpResponseForbidden({'error': 'you cannot set admin role'})

    serializer = UserSerializer(instance=user, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@admin_required
def deleteUser(request, pk):
    user = User.objects.get(id=pk)
    user.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
