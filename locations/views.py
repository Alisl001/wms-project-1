from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from backend.models import Location
from .serializers import LocationSerializer
from users.authentication import BearerTokenAuthentication

# List Locations API
@api_view(['GET'])
@permission_classes([AllowAny])
def listLocations(request):
    locations = Location.objects.all()
    serializer = LocationSerializer(locations, many=True)
    return Response(serializer.data)


# Location Info API
@api_view(['GET'])
@permission_classes([AllowAny])
def locationInfo(request, id):
    try:
        location = Location.objects.get(pk=id)
    except Location.DoesNotExist:
        return Response({"detail": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = LocationSerializer(location)
    return Response(serializer.data)


# Create Location API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def createLocation(request):
    serializer = LocationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Location created successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update Location API
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def updateLocation(request, id):
    try:
        location = Location.objects.get(pk=id)
    except Location.DoesNotExist:
        return Response({"detail": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = LocationSerializer(location, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Location updated successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete Location API
@api_view(['DELETE'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def deleteLocation(request, id):
    try:
        location = Location.objects.get(pk=id)
    except Location.DoesNotExist:
        return Response({"detail": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

    location.delete()
    return Response({"detail": "Location deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

