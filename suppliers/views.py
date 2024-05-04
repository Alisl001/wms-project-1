from rest_framework.decorators import api_view, permission_classes, authentication_classes
from users.authentication import BearerTokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from backend.models import Supplier
from .serializers import SupplierSerializer
from rest_framework.parsers import MultiPartParser


# List Suppliers API:
@api_view(['GET'])
@permission_classes([AllowAny])
def listSuppliers(request):

    suppliers = Supplier.objects.all()
    serializer = SupplierSerializer(suppliers, many=True, fields=('id', 'name', 'photo'))
    return Response(serializer.data)


# Supplier Info API:
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def supplierInfo(request, id):

    try:
        supplier = Supplier.objects.get(pk=id)
    except Supplier.DoesNotExist:
        return Response({"detail": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = SupplierSerializer(supplier)
    return Response(serializer.data)


# Create Supplier API:
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def createSupplier(request):

    serializer = SupplierSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update Supplier API:
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def updateSupplier(request, id):

    try:
        supplier = Supplier.objects.get(pk=id)
    except Supplier.DoesNotExist:
        return Response({"detail": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = SupplierSerializer(supplier, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete Supplier API:
@api_view(['DELETE'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def deleteSupplier(request, id):

    try:
        supplier = Supplier.objects.get(pk=id)
    except Supplier.DoesNotExist:
        return Response({"detail": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)

    supplier.delete()
    return Response({"detail": "Supplier deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Upload Supplier photo API:
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def uploadSupplierPhoto(request, id):

    try:
        supplier = Supplier.objects.get(pk=id)
    except Supplier.DoesNotExist:
        return Response({"detail": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if a photo is included in the request
    if 'photo' not in request.FILES:
        return Response({"detail": "No photo provided in the request"}, status=status.HTTP_400_BAD_REQUEST)

    photo = request.FILES['photo']
    supplier.photo = photo
    supplier.save()

    return Response({"detail": "Photo uploaded successfully"}, status=status.HTTP_200_OK)


