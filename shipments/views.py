from itertools import product
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from backend.models import Shipment, ShipmentDetail, Product, Inventory, Activity
from .serializers import ShipmentSerializer, ShipmentDetailSerializer, ListShipmentSerializer
from users.authentication import BearerTokenAuthentication
from users.permissions import IsStaffUser
from datetime import datetime
from django.db.models import Case, When, IntegerField
from django.db import models


# Create Shipment API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def createShipment(request):
    data = request.data
    details = data.pop('details', [])
    data['status'] = 'pending'
    data.pop('receive_date', None)

    # Creating the shipment first
    shipment_serializer = ShipmentSerializer(data=data)
    
    if shipment_serializer.is_valid():
        shipment = shipment_serializer.save()
        
        products_seen = set()
        
        # Creating ShipmentDetail entries manually
        for detail in details:
            product_id = detail['product']
            if product_id in products_seen:
                continue  # Skip duplicate product entries
            
            product = Product.objects.get(id=product_id)
            product.price = detail['price_at_shipment'] * 1.05
            product.save()
            
            ShipmentDetail.objects.create(
                shipment=shipment,
                product=product,
                price_at_shipment=detail['price_at_shipment'],
                quantity=detail['quantity'],
                status='pending'
            )
            products_seen.add(product_id)
        
        return Response({"detail": "Shipment created successfully."}, status=status.HTTP_201_CREATED)
    
    return Response(shipment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# List All Shipments API
@api_view(['GET'])
@permission_classes([AllowAny])
def listShipments(request):
    shipments = Shipment.objects.all().order_by(
        Case(When(status='pending', then=0),
            When(status='received', then=1),
            When(status='put_away', then=2),
            default=3,
            output_field=models.IntegerField()
        )
    )
    serializer = ListShipmentSerializer(shipments, many=True)
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
        shipment = Shipment.objects.get(id=id)
    except Shipment.DoesNotExist:
        return Response({"detail": "Shipment not found."}, status=status.HTTP_404_NOT_FOUND)
    
    data = request.data
    details = data.pop('details', [])
    data['status'] = 'pending'
    data.pop('receive_date', None)

    shipment_serializer = ShipmentSerializer(shipment, data=data, partial=True)
    
    if shipment_serializer.is_valid():
        shipment = shipment_serializer.save()
        
        existing_details = {detail.id: detail for detail in ShipmentDetail.objects.filter(shipment=shipment)}
        products_seen = set()
        
        for detail in details:
            product_id = detail['product']
            product = Product.objects.get(id=product_id)
            product.price = detail['price_at_shipment'] * 1.05
            product.save()

            if 'id' in detail and detail['id'] in existing_details:
                shipment_detail = existing_details.pop(detail['id'])
                shipment_detail.product = product
                shipment_detail.price_at_shipment = detail['price_at_shipment']
                shipment_detail.quantity = detail['quantity']
                shipment_detail.status = 'pending'
                shipment_detail.save()
            else:
                ShipmentDetail.objects.create(
                    shipment=shipment,
                    product=product,
                    price_at_shipment=detail['price_at_shipment'],
                    quantity=detail['quantity'],
                    status='pending'
                )
            
            products_seen.add(product_id)
        
        for shipment_detail in existing_details.values():
            shipment_detail.delete()
        
        return Response({"detail": "Shipment updated successfully."}, status=status.HTTP_200_OK)
    
    return Response(shipment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    user = request.user
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

    # Record activity
    Activity.objects.create(
        staff=user,
        description=f"received product {shipment_detail.product} from shipment {shipment_id}",
        activity_type='receive')

    return Response({"detail": "Product received successfully."}, status=status.HTTP_200_OK)


# Shipment details and all its product API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
def shipmentDetails(request, shipment_id):
    try:
        shipment_details = ShipmentDetail.objects.filter(shipment_id=shipment_id)
        serializer = ShipmentDetailSerializer(shipment_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ShipmentDetail.DoesNotExist:
        return Response({"detail": "Shipment details not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


