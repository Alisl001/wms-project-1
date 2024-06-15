from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from users.authentication import BearerTokenAuthentication
from users.permissions import IsStaffUser
from backend.models import ShipmentDetail, Location, Inventory, Product, BarcodeScanning, Activity, StockAdjustment, Shipment, StockMovement
from .serializers import ShipmentDetailSerializer, ProductSerializer, InventorySerializer, LocationSerializer
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError, transaction


# Browse Received Products API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
def browseReceivedProducts(request):
    try:
        received_products = ShipmentDetail.objects.filter(status='received')
        
        if not received_products.exists():
            return Response({"detail": "No received products found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ShipmentDetailSerializer(received_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Suggest Locations API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
def suggestLocations(request, shipment_detail_id):
    try:
        shipment_detail = ShipmentDetail.objects.get(id=shipment_detail_id, status='received')
    except ShipmentDetail.DoesNotExist:
        return Response({"detail": "Shipment detail not found or not received"}, status=status.HTTP_404_NOT_FOUND)

    product = shipment_detail.product
    quantity = shipment_detail.quantity
    product_size = product.size
    category_id = product.category.id

    # Define location mappings based on category ID
    location_mappings = {
        1: {'aisle': '1', 'rack__in': ['1', '2']},
        2: {'aisle': '1', 'rack__in': ['3', '4']},
        3: {'aisle': '2', 'rack__in': ['1', '2']},
        4: {'aisle': '2', 'rack__in': ['3', '4']},
        5: {'aisle': '3', 'rack__in': ['1', '2']},
        6: {'aisle': '3', 'rack__in': ['3', '4']},
    }

    # Retrieve locations based on category ID
    if category_id in location_mappings:
        base_locations = Location.objects.filter(**location_mappings[category_id])
    else:
        return Response({"detail": "Category not supported for location suggestion"}, status=status.HTTP_400_BAD_REQUEST)

    # Retrieve all locations matching the category and calculate stock movement frequency
    location_freq = {}
    for location in base_locations:
        from_location_count = StockMovement.objects.filter(from_location=location).count()
        to_location_count = StockMovement.objects.filter(to_location=location).count()
        location_freq[location.id] = from_location_count + to_location_count

    # Sort locations by frequency in descending order
    sorted_locations = sorted(location_freq.items(), key=lambda x: x[1], reverse=True)
    sorted_location_ids = [loc_id for loc_id, freq in sorted_locations]

    # Filter locations based on capacity and proximity to docking area
    suggested_locations = []
    for loc_id in sorted_location_ids:
        location = Location.objects.get(id=loc_id)
        used_capacity = Inventory.objects.filter(location=location).aggregate(total=Sum('quantity'))['total'] or 0
        available_capacity = location.capacity - used_capacity
        if available_capacity >= product_size * quantity:
            suggested_locations.append({
                'location': location,
                'shipment_detail_id': shipment_detail_id
            })
            if len(suggested_locations) == 3:  # Limit to 3 suggested locations
                break

    if not suggested_locations:
        return Response({"detail": "No suitable locations found"}, status=status.HTTP_404_NOT_FOUND)

    # Serialize data for response
    location_serializer = LocationSerializer([loc['location'] for loc in suggested_locations], many=True)
    product_serializer = ProductSerializer(product)

    response_data = {
        'shipment_detail_id': shipment_detail_id,
        'product': product_serializer.data,
        'quantity': quantity,
        'suggested_locations': location_serializer.data
    }

    return Response(response_data, status=status.HTTP_200_OK)


# Put Away Product API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
def putAwayProduct(request):
    shipment_detail_id = request.data.get('shipment_detail_id')
    location_barcode = request.data.get('location_barcode')
    quantity_to_put_away = int(request.data.get('quantity'))
    user = request.user

    try:
        shipment_detail = ShipmentDetail.objects.get(id=shipment_detail_id, status='received')
    except ShipmentDetail.DoesNotExist:
        return Response({"detail": "Shipment detail not found or not received"}, status=status.HTTP_404_NOT_FOUND)

    try:
        location = Location.objects.get(barcode=location_barcode)
    except Location.DoesNotExist:
        return Response({"detail": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

    product = shipment_detail.product
    docking_area_location = Location.objects.get(id=1)

    # Validate quantity
    if quantity_to_put_away > shipment_detail.quantity:
        return Response({"detail": "Quantity to put away exceeds available quantity in shipment detail"}, status=status.HTTP_400_BAD_REQUEST)

    # Update inventory at docking area
    try:
        with transaction.atomic():
            docking_inventories = Inventory.objects.filter(product=product, location=docking_area_location)
            if not docking_inventories.exists():
                return Response({"detail": "No inventory record found in docking area for the product"}, status=status.HTTP_404_NOT_FOUND)

            total_docking_quantity = sum(inventory.quantity for inventory in docking_inventories)
            
            if quantity_to_put_away > total_docking_quantity:
                return Response({"detail": "Quantity to put away exceeds available quantity in docking area"}, status=status.HTTP_400_BAD_REQUEST)

            quantity_remaining = quantity_to_put_away

            for inventory in docking_inventories:
                if quantity_remaining <= inventory.quantity:
                    inventory.quantity -= quantity_remaining
                    inventory.save()
                    quantity_remaining = 0
                    break
                else:
                    quantity_remaining -= inventory.quantity
                    inventory.delete()

            # Record stock adjustment
            StockAdjustment.objects.create(
                product=product,
                location=docking_area_location,
                quantity=quantity_to_put_away,
                adjustment_type='decrease',
                reason='Put away to another location'
            )

            # Create new inventory record at the new location
            new_inventory, created = Inventory.objects.get_or_create(
                product=product,
                location=location,
                defaults={'quantity': quantity_to_put_away}
            )
            if not created:
                new_inventory.quantity += quantity_to_put_away
                new_inventory.save()

            # Remove any inventory records with quantity 0
            Inventory.objects.filter(product=product, quantity=0).delete()

            # Update shipment detail status without altering quantity
            shipment_detail.status = 'put_away'
            shipment_detail.save()

            # Record activity
            Activity.objects.create(
                staff=user,
                description=f"Put away {quantity_to_put_away} of product {product.name} to location {location.name}",
                activity_type='put_away'
            )

            # Record stock movement from docking area to target location
            StockMovement.objects.create(
                product=product,
                from_location=docking_area_location,
                to_location=location,
                quantity=quantity_to_put_away,
                movement_type='put_away'
            )

            # Record barcode scanning
            BarcodeScanning.objects.create(
                scanned_by=user,
                scanned_item=product,
                location=location,
                action='put_away'
            )

            # Check if all products in the shipment are put away
            shipment = shipment_detail.shipment
            if not ShipmentDetail.objects.filter(shipment=shipment, status__in=['pending', 'received']).exists():
                shipment.status = 'put_away'
                shipment.receive_date = timezone.now()
                shipment.save()

            return Response({"detail": "Product put away successfully"}, status=status.HTTP_200_OK)

    except IntegrityError as e:
        return Response({"detail": f"Integrity error occurred while updating docking area inventory: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({"detail": f"Unexpected error occurred while updating docking area inventory: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

