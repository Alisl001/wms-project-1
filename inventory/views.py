from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from backend.models import Inventory, StockMovement, Product, Location, Activity, CycleCount, StockAdjustment, ReplenishmentRequest
from .serializers import InventorySerializer, ReplenishmentRequestSerializer, CycleCountSerializer, StockMovementSerializer
from users.authentication import BearerTokenAuthentication
from users.permissions import IsStaffUser


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


# Transfer Product API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
def transferProduct(request):
    product_barcode = request.data.get('product_barcode')
    from_location_barcode = request.data.get('from_location_barcode')
    to_location_barcode = request.data.get('to_location_barcode')
    quantity = request.data.get('quantity')

    if not product_barcode or not from_location_barcode or not to_location_barcode or not quantity:
        return Response({"detail": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        quantity = int(quantity)
        if quantity <= 0:
            return Response({"detail": "Quantity must be a positive integer"}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({"detail": "Quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

    product = get_object_or_404(Product, barcode=product_barcode)
    from_location = get_object_or_404(Location, barcode=from_location_barcode)
    to_location = get_object_or_404(Location, barcode=to_location_barcode)
    staff = request.user

    if from_location == to_location:
        return Response({"detail": "From location and to location cannot be the same"}, status=status.HTTP_400_BAD_REQUEST)

    inventory_from = get_object_or_404(Inventory, product=product, location=from_location)
    if inventory_from.quantity < quantity:
        return Response({"detail": "Insufficient quantity in the source location"}, status=status.HTTP_400_BAD_REQUEST)

    inventory_to, created = Inventory.objects.get_or_create(product=product, location=to_location, defaults={'quantity': 0})

    # Update quantities
    inventory_from.quantity -= quantity
    inventory_to.quantity += quantity

    # Save updated inventory
    inventory_from.save()
    inventory_to.save()

    # Create stock movement record
    stock_movement = StockMovement(
        product=product,
        from_location=from_location,
        to_location=to_location,
        quantity=quantity,
        movement_type='transfer'
    )
    stock_movement.save()

    # Create activity record
    activity_description = f"Transferred {quantity} of {product.name} from {from_location.name} to {to_location.name}"
    activity = Activity(
        staff=staff,
        description=activity_description,
        activity_type='transfer'
    )
    activity.save()

    # Delete the inventory record if the quantity is zero
    if inventory_from.quantity == 0:
        inventory_from.delete()

    return Response({"detail": "Product transferred successfully"}, status=status.HTTP_200_OK)


# Cycle count API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
def cycleCount(request):
    product_barcode = request.data.get('product_barcode')
    location_barcode = request.data.get('location_barcode')
    counted_quantity = request.data.get('counted_quantity')

    if not product_barcode or not location_barcode or not counted_quantity:
        return Response({"detail": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        counted_quantity = int(counted_quantity)
        if counted_quantity < 0:
            return Response({"detail": "Counted quantity must be a non-negative integer"}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({"detail": "Counted quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

    product = get_object_or_404(Product, barcode=product_barcode)
    location = get_object_or_404(Location, barcode=location_barcode)
    staff = request.user

    inventory = get_object_or_404(Inventory, product=product, location=location)

    # Create cycle count record
    cycle_count = CycleCount(
        product=product,
        location=location,
        counted_quantity=counted_quantity
    )
    cycle_count.save()

    # Create activity record
    activity_description = f"Cycle count for {product.name} at {location.name} - Counted Quantity: {counted_quantity}"
    activity = Activity(
        staff=staff,
        description=activity_description,
        activity_type='cycle_count'
    )
    activity.save()

    # Check for discrepancies and create stock adjustment if needed
    if inventory.quantity != counted_quantity:
        adjustment_type = 'increase' if counted_quantity > inventory.quantity else 'decrease'
        adjustment_quantity = abs(counted_quantity - inventory.quantity)

        stock_adjustment = StockAdjustment(
            product=product,
            location=location,
            quantity=adjustment_quantity,
            adjustment_type=adjustment_type,
            reason=f"Cycle count discrepancy: {counted_quantity} counted vs {inventory.quantity} recorded"
        )
        stock_adjustment.save()

        # Update the inventory quantity to the counted quantity
        inventory.quantity = counted_quantity
        inventory.save()

    return Response({"detail": "Cycle count recorded successfully"}, status=status.HTTP_200_OK)


# Create Replenishment Request API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
def createReplenishmentRequest(request):
    product_barcode = request.data.get('product_barcode')
    location_barcode = request.data.get('location_barcode')
    quantity = request.data.get('quantity')
    reason = request.data.get('reason', '')

    if not product_barcode or not location_barcode or not quantity:
        return Response({"detail": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        quantity = int(quantity)
        if quantity <= 0:
            return Response({"detail": "Quantity must be a positive integer"}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({"detail": "Quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

    product = get_object_or_404(Product, barcode=product_barcode)
    location = get_object_or_404(Location, barcode=location_barcode)

    replenishment_request = ReplenishmentRequest(
        product=product,
        location=location,
        quantity=quantity,
        reason=reason
    )
    replenishment_request.save()

    return Response({"detail": "Replenishment request created successfully"}, status=status.HTTP_201_CREATED)


# List Replenishment Requests API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def listReplenishmentRequests(request):
    requests = ReplenishmentRequest.objects.all()
    serializer = ReplenishmentRequestSerializer(requests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Approve Replenishment Request API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def approveReplenishmentRequest(request, request_id):
    replenishment_request = get_object_or_404(ReplenishmentRequest, id=request_id)

    if replenishment_request.status != 'pending':
        return Response({"detail": "Request is not pending"}, status=status.HTTP_400_BAD_REQUEST)

    replenishment_request.status = 'approved'
    replenishment_request.save()

    return Response({"detail": "Replenishment request approved"}, status=status.HTTP_200_OK)


# Reject Replenishment Request API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def rejectReplenishmentRequest(request, request_id):
    replenishment_request = get_object_or_404(ReplenishmentRequest, id=request_id)

    if replenishment_request.status != 'pending':
        return Response({"detail": "Request is not pending"}, status=status.HTTP_400_BAD_REQUEST)

    replenishment_request.status = 'rejected'
    replenishment_request.save()

    return Response({"detail": "Replenishment request rejected"}, status=status.HTTP_200_OK)



