from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from users.authentication import BearerTokenAuthentication
from backend.models import Activity
from .serializers import ActivitySerializer
from django.shortcuts import render


# List All Activities API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def listActivities(request):
    activities = Activity.objects.order_by('-timestamp')
    serializer = ActivitySerializer(activities, many=True)
    return Response(serializer.data)


# Homepage API
@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
      return Response("Welcome to SAD WMS!")
