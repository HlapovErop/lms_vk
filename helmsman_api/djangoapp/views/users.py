from django.contrib.auth.hashers import check_password
from django.http import HttpResponseForbidden
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from djangoapp.authentication import JWTAuthentication
from djangoapp.decorators import admin_required
from djangoapp.models.group import Group
from djangoapp.models.user import User
from djangoapp.models.user import UserRoleEnum
from djangoapp.serializers.user_serializer import UserSerializer, SimpleUserSerializer
from djangoapp.utils.decoders import generate_jwt_token


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='User username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
        }
    ),
    responses={
        200: openapi.Response('Successful login', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='JWT token'),
                'end_time': openapi.Schema(type=openapi.TYPE_STRING, description='Token expiry time'),
            }
        )),
        400: openapi.Response('Bad Request'),
        401: openapi.Response('Unauthorized')
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'Invalid username'}, status=status.HTTP_401_UNAUTHORIZED)

    if not check_password(password, user.password):
        return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

    token, date = generate_jwt_token(user.id)

    return Response({'token': token, 'end_time': date}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('Successful retrieval of user list', SimpleUserSerializer(many=True)),
        403: openapi.Response('Forbidden')
    }
)
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
        users = User.objects.filter(role__in=request.user.role)

    if request.user.is_admin():
        serializer = UserSerializer(users, many=True)
    else:
        serializer = SimpleUserSerializer(users, many=True)

    return Response(serializer.data)


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('Successful retrieval of user data', UserSerializer()),
        403: openapi.Response('Forbidden'),
        404: openapi.Response('Not Found')
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getUser(request, pk):
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user.is_admin():
        serializer = UserSerializer(user)
    else:
        serializer = SimpleUserSerializer(user)

    return Response(serializer.data)



@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('Successful retrieval of user data', UserSerializer()),
        403: openapi.Response('Forbidden'),
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getProfile(request):
    serializer = SimpleUserSerializer(request.user)

    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    request_body=UserSerializer,
    responses={
        201: openapi.Response('User created successfully', UserSerializer),
        422: openapi.Response('Validation error')
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def createUser(request):
    if request.data.get('role') == UserRoleEnum.ADMIN and not request.user.is_admin():
        return HttpResponseForbidden({'error': 'You cannot set admin role'})

    serializer = SimpleUserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@swagger_auto_schema(
    method='put',
    request_body=UserSerializer,
    responses={
        200: openapi.Response('User updated successfully', UserSerializer),
        403: openapi.Response('Forbidden'),
        422: openapi.Response('Validation error')
    }
)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
def updateUser(request, pk):
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user.id != user.id and not request.user.is_admin():
        return HttpResponseForbidden({'error': 'You cannot change another user'})

    if request.data.get('role') == UserRoleEnum.ADMIN and not request.user.is_admin():
        return HttpResponseForbidden({'error': 'You cannot set admin role'})

    serializer = SimpleUserSerializer(instance=user, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@swagger_auto_schema(
    method='delete',
    responses={
        204: openapi.Response('User deleted successfully'),
        403: openapi.Response('Forbidden'),
        404: openapi.Response('Not Found')
    }
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@admin_required
def deleteUser(request, pk):
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
