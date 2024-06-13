from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from djangoapp.models.notification import Notification
from djangoapp.serializers.notification_serializer import NotificationSerializer
from djangoapp.authentication import JWTAuthentication

from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(
    method='post',
    request_body=NotificationSerializer,
    responses={
        201: openapi.Response('Notification created successfully', NotificationSerializer),
        422: openapi.Response('Validation error')
    }
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def createNotification(request: HttpRequest) -> HttpResponse:
    request.data['from_user'] = request.user.id
    serializer = NotificationSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@swagger_auto_schema(
    method='get',
    responses={
        200: openapi.Response('Successful retrieval of notifications', NotificationSerializer(many=True)),
        403: openapi.Response('Forbidden')
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def getNotifications(request: HttpRequest) -> HttpResponse:
    notifications = Notification.objects.filter(to_user=request.user)
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@swagger_auto_schema(
    method='delete',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'notification_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER))
        }
    ),
    responses={
        204: openapi.Response('Notifications read and deleted successfully'),
        400: openapi.Response('Bad Request'),
        403: openapi.Response('Forbidden')
    }
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
def readNotifications(request: HttpRequest) -> HttpResponse:
    notification_ids = request.data.get('notification_ids', [])
    if not notification_ids:
        return Response({'error': 'No notification IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

    notifications = Notification.objects.filter(id__in=notification_ids, to_user=request.user)
    if not notifications:
        return HttpResponseForbidden({'error': 'You cannot read these notifications'})

    deleted_count, _ = notifications.delete()
    return Response(f'{deleted_count} notification read successfully and deleted!', status=status.HTTP_204_NO_CONTENT)
