from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from backend.models import Shipment, ShipmentDetail, Product, Inventory
from .serializers import ShipmentSerializer, ShipmentDetailSerializer
from users.authentication import BearerTokenAuthentication
from users.permissions import IsStaffUser
from datetime import datetime


# Create Shipment API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def createShipment(request):
    data = request.data
    details = data.pop('details')
    data['status'] = 'pending'
    data.pop('receive_date', None)
    serializer = ShipmentSerializer(data=data)
    if serializer.is_valid():
        shipment = serializer.save()
        for detail in details:
            product = Product.objects.get(id=detail['product'])
            product.price = detail['price_at_shipment'] * 1.05
            product.save()
            ShipmentDetail.objects.create(
                shipment=shipment,
                product=product,
                price_at_shipment=detail['price_at_shipment'],
                quantity=detail['quantity'],
                status='pending'
            )
        return Response({"detail": "Shipment created successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# List All Shipments API
@api_view(['GET'])
@permission_classes([AllowAny])
def listShipments(request):
    shipments = Shipment.objects.all().order_by('-status')
    serializer = ShipmentSerializer(shipments, many=True)
    return Response(serializer.data)


# Shipment Details API
@api_view(['GET'])
@permission_classes([AllowAny])
def shipmentInfo(request, id):
    try:
        shipment = Shipment.objects.get(pk=id)
    except Shipment.DoesNotExist:
        return Response({"detail": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ShipmentSerializer(shipment)
    return Response(serializer.data)


# Update Shipment API
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def updateShipment(request, id):
    try:
        shipment = Shipment.objects.get(pk=id)
    except Shipment.DoesNotExist:
        return Response({"detail": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ShipmentSerializer(shipment, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Shipment updated successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete Shipment API
@api_view(['DELETE'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def deleteShipment(request, id):
    try:
        shipment = Shipment.objects.get(pk=id)
    except Shipment.DoesNotExist:
        return Response({"detail": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)

    shipment.delete()
    return Response({"detail": "Shipment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Receive Product API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
def receiveProduct(request, shipment_id, barcode):
    try:
        shipment = Shipment.objects.get(pk=shipment_id)
    except Shipment.DoesNotExist:
        return Response({"detail": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        shipment_detail = ShipmentDetail.objects.get(shipment=shipment, product__barcode=barcode)
    except ShipmentDetail.DoesNotExist:
        return Response({"detail": "Product not found in this shipment"}, status=status.HTTP_404_NOT_FOUND)

    if shipment_detail.status != 'pending':
        return Response({"detail": "Product already received"}, status=status.HTTP_400_BAD_REQUEST)

    shipment_detail.status = 'received'
    shipment_detail.save()

    # Add product to inventory at docking area (location ID 1)
    Inventory.objects.create(
        product=shipment_detail.product,
        location_id=1,
        quantity=shipment_detail.quantity,
        status='available'
    )

    # Check if all products in the shipment are received
    if not ShipmentDetail.objects.filter(shipment=shipment, status='pending').exists():
        shipment.status = 'received'
        shipment.receive_date = datetime.now().date()
        shipment.save()

    return Response({"detail": "Product received successfully."}, status=status.HTTP_200_OK)


# Shipment details and all its product API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
def shipmentDetails(request, shipment_id):
    try:
        shipment = Shipment.objects.get(pk=shipment_id)
    except Shipment.DoesNotExist:
        return Response({"detail": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ShipmentSerializer(shipment)
    return Response(serializer.data, status=status.HTTP_200_OK)


