from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from users.authentication import BearerTokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from backend.models import Warehouse
from .serializers import WarehouseSerializer
from django.db import IntegrityError
from django.shortcuts import get_object_or_404


# Create warehouse API:
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def createWarehouse(request):
    serializer = WarehouseSerializer(data=request.data)
    if serializer.is_valid():
        try:
            warehouse = serializer.save()
            return Response({'detail': "Warehouse created successfully."}, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            return Response({'detail': "A warehouse with that name already exists."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        error_message = next(iter(serializer.errors.values()))[0]
        return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)



# Update warehouse API:
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def updateWarehouse(request, id):
    warehouse = get_object_or_404(Warehouse, id=id)
    serializer = WarehouseSerializer(warehouse, data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response({'detail': "Warehouse updated successfully."}, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({'detail': "A warehouse with that name already exists."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        error_message = next(iter(serializer.errors.values()))[0]
        return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)



# List warehouses API: 
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def listWarehouses(request):
    warehouses = Warehouse.objects.all()
    serializer = WarehouseSerializer(warehouses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



# Delete warehouse API:
@api_view(['DELETE'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def deleteWarehouse(request, id):
    warehouse = get_object_or_404(Warehouse, id=id)
    warehouse.delete()
    return Response({'detail': "Warehouse deleted successfully."}, status=status.HTTP_204_NO_CONTENT)