# TODO Прочитать определённые уведомления
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from models.notification import Notification
from serializers.notification_serializer import NotificationSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
def createNotification(request: HttpRequest) -> HttpResponse:
	request.data['from_user'] = request.user.id
	serializer = NotificationSerializer(data=request.data)

	if serializer.is_valid():
		serializer.save()
		return Response(serializer.data,
						status=status.HTTP_201_CREATED)
	else:
		return Response(serializer.errors,
						status=status.HTTP_422_UNPROCESSABLE_ENTITY)
	
@api_view(['GET'])
def getNotifications(request: HttpRequest) -> HttpResponse:
	notifications = Notification.objects.filter(
		to_user=request.user
	)
	serializer = NotificationSerializer(notifications, many=True)
	return serializer.data

@api_view(['DELETE'])
def readNotifications(request: HttpRequest) -> HttpResponse:
	notification_ids = request.data.get('notification_ids', [])
	if not notification_ids:
		return Response({'error': 'No notification IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
	
	notifications = Notification.objects.filter(id__in=notification_ids,
															to_user=request.user)
	if not notifications:
		return HttpResponseForbidden({'error': 'You cannot read these notifications'})
	
	deleted_count, _ = notifications.delete()
	return Response(f'{deleted_count} notification read successfully and deleted!',
					  status=status.HTTP_204_NO_CONTENT)