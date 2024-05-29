from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from backend.models import Inventory
from .serializers import InventorySerializer
from users.authentication import BearerTokenAuthentication


# List Inventory API
@api_view(['GET'])
@permission_classes([AllowAny])
def listInventory(request):
    inventory = Inventory.objects.all()
    serializer = InventorySerializer(inventory, many=True)
    return Response(serializer.data)


# Inventory Info API
@api_view(['GET'])
@permission_classes([AllowAny])
def inventoryInfo(request, id):
    try:
        inventory = Inventory.objects.get(pk=id)
    except Inventory.DoesNotExist:
        return Response({"detail": "Inventory item not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = InventorySerializer(inventory)
    return Response(serializer.data)


# Create Inventory API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def createInventory(request):
    serializer = InventorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Inventory item created successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update Inventory API
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def updateInventory(request, id):
    try:
        inventory = Inventory.objects.get(pk=id)
    except Inventory.DoesNotExist:
        return Response({"detail": "Inventory item not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = InventorySerializer(inventory, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Inventory item updated successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete Inventory API
@api_view(['DELETE'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def deleteInventory(request, id):
    try:
        inventory = Inventory.objects.get(pk=id)
    except Inventory.DoesNotExist:
        return Response({"detail": "Inventory item not found"}, status=status.HTTP_404_NOT_FOUND)

    inventory.delete()
    return Response({"detail": "Inventory item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


