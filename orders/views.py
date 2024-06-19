from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth.models import User
from backend.models import Order, OrderDetail, Product, Notification, Inventory, Location, StockAdjustment, StockMovement, BarcodeScanning, Activity, DeliveryRecord, Wallet, TransactionLog
from users.permissions import IsStaffUser
from .serializers import OrderSerializer, OrderDetailSerializer
from users.authentication import BearerTokenAuthentication
from django.db.models import Case, When, Value, IntegerField, F, Sum
from datetime import datetime


def send_notification_to_admin(message):
    admin = User.objects.get(pk=1)
    Notification.objects.create(
        user=admin,
        message=message,
        status='unread'
    )


# Create Order API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def createOrder(request):
    data = request.data.copy()
    data['customer'] = request.user.id

    # Calculate the total price
    try:
        products_data = data.get('products', [])
        total_price = sum(Product.objects.get(id=item['product']).price * item['quantity'] for item in products_data)
    except Product.DoesNotExist:
        return Response({"detail": "One or more products not found"}, status=status.HTTP_400_BAD_REQUEST)
    except KeyError:
        return Response({"detail": "Invalid product data"}, status=status.HTTP_400_BAD_REQUEST)

    # Add the calculated total_price to the data
    data['total_price'] = total_price

    serializer = OrderSerializer(data=data)
    if serializer.is_valid():
        if products_data:
            product_ids = [product['product'] for product in products_data]
            total_quantity_needed = sum(product['quantity'] for product in products_data)
            
            # Calculate the total quantity of products in pending orders
            pending_orders_quantity = OrderDetail.objects.filter(
                order__status='pending',
                product__id__in=product_ids
            ).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

            # Check the availability of products in inventory
            for product_data in products_data:
                product = Product.objects.get(id=product_data['product'])
                product_quantity_in_inventory = Inventory.objects.filter(product=product).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
                if product_quantity_in_inventory - pending_orders_quantity - product_data['quantity'] < 0:
                    return Response({"detail": f"Not enough quantity available for product {product.name}"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                wallet = Wallet.objects.get(customer=request.user)
            except Wallet.DoesNotExist:
                return Response({"detail": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check if the user's wallet balance is sufficient
            if wallet.balance < total_price:
                return Response({"detail": "Insufficient funds in the wallet"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order without products data
        validated_data = serializer.validated_data
        validated_data.pop('products', None)  # Remove products from validated_data if it's already there
        order = Order.objects.create(**validated_data)

        # Add products to the order
        for product_data in products_data:
            product = Product.objects.get(id=product_data['product'])
            OrderDetail.objects.create(
                order=order,
                product=product,
                quantity=product_data['quantity'],
                price_at_sale=product.price,
                status='pending'
            )

        # Deduct the total order amount from the wallet balance and save the wallet
        wallet.balance -= total_price
        wallet.save()

        # Create a transaction log entry for the deduction
        TransactionLog.objects.create(
            customer=request.user,
            amount=total_price,
            transaction_type='purchase',
            description='Deducted funds for order'
        )

        send_notification_to_admin(f"New order created: Order ID {order.id}")
        return Response({"detail": "Order created successfully"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update Order API
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def updateOrder(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['customer'] = order.customer.id  # Keep the original customer

    serializer = OrderSerializer(order, data=data, partial=True)
    if serializer.is_valid():
        products_data = data.get('products', [])

        # Calculate new total price and check product availability
        total_price = 0
        try:
            for product_data in products_data:
                product = Product.objects.get(id=product_data['product'])
                total_price += product.price * product_data['quantity']

                # Check product availability in inventory
                product_quantity_in_inventory = Inventory.objects.filter(product=product).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
                pending_orders_quantity = OrderDetail.objects.filter(order__status='pending', product=product).exclude(order=order).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

                if product_quantity_in_inventory - pending_orders_quantity - product_data['quantity'] < 0:
                    return Response({"detail": f"Not enough quantity available for product {product.name}"}, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({"detail": "One or more products not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Remove existing order details
        OrderDetail.objects.filter(order=order).delete()

        # Update order total price
        order.total_price = total_price
        order.save()

        try:
            wallet = Wallet.objects.get(customer=request.user)
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)

        # Calculate the difference in total price for updating the wallet balance
        difference = total_price - order.total_price

        # Update the wallet balance
        wallet.balance -= difference
        wallet.save()

        # Create a transaction log entry for the difference
        TransactionLog.objects.create(
            customer=request.user,
            amount=difference,
            transaction_type='purchase' if difference < 0 else 'refund',
            description='Updated funds for order'
        )

        # Create new order details
        for product_data in products_data:
            product = Product.objects.get(id=product_data['product'])
            OrderDetail.objects.create(
                order=order,
                product=product,
                quantity=product_data['quantity'],
                price_at_sale=product.price,
                status='pending'
            )
        
        send_notification_to_admin(f"Order updated: Order ID {order.id}")
        return Response({"detail": "Order updated successfully"}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Cancel Order API
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def cancelOrder(request, order_id):
    try:
        order = Order.objects.get(id=order_id, customer=request.user)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Refund the deducted amount back to the user's wallet balance
    try:
        wallet = Wallet.objects.get(customer=request.user)
    except Wallet.DoesNotExist:
        return Response({"detail": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)
    
    wallet.balance += order.total_price
    wallet.save()

    # Create a transaction log entry for the refund
    TransactionLog.objects.create(
        customer=request.user,
        amount=order.total_price,
        transaction_type='refund',
        description='Refunded funds for canceled order'
    )

    # Update the order status to 'cancelled'
    order.status = 'cancelled'
    order.save()

    send_notification_to_admin(f"Order cancelled: Order ID {order.id}")
    return Response({"detail": "Order cancelled successfully"}, status=status.HTTP_200_OK)


# View Order Status API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def viewOrderStatus(request, order_id):
    try:
        order = Order.objects.get(id=order_id, customer=request.user)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Get Order Details API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def getOrderDetails(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    order_details = OrderDetail.objects.filter(order=order)
    order_data = OrderSerializer(order).data
    order_data['details'] = OrderDetailSerializer(order_details, many=True).data

    return Response(order_data, status=status.HTTP_200_OK)


# View My Orders API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def viewMyOrders(request):
    orders = Order.objects.filter(customer=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# View All Orders API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
def listOrders(request):
    orders = Order.objects.annotate(
        is_pending=Case(
            When(status='pending', then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        ),
        priority_level=Case(
            When(priority='high', then=Value(1)),
            When(priority='low', then=Value(2)),
            default=Value(3),
            output_field=IntegerField()
        )
    ).order_by('-is_pending', 'priority_level', '-created_at')
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


# Prioritize Order API
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def prioritizeOrder(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    
    order.priority = 'high'
    order.save()
    return Response({"detail": "Order prioritized successfully"}, status=status.HTTP_200_OK)


# Update Order Status API
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def updateOrderStatus(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status')
    if new_status not in dict(Order.status_choices):
        return Response({"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    order.status = new_status
    order.save()

    # Send notification to the customer
    message = f"Your order (ID: {order.id}) status has been updated to {new_status}."
    Notification.objects.create(
        user=order.customer,
        message=message,
        status='unread'
    )

    return Response({"detail": "Order status updated successfully"}, status=status.HTTP_200_OK)


# Pick List API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsStaffUser])
def getPickList(request, order_detail_id):
    try:
        order_detail = OrderDetail.objects.get(pk=order_detail_id)
    except OrderDetail.DoesNotExist:
        return Response({"detail": "Order detail not found"}, status=status.HTTP_404_NOT_FOUND)

    product = order_detail.product

    # Get locations where the product is available
    locations = Inventory.objects.filter(
        product=product,
        quantity__gt=0,
        status='available'
    ).annotate(
        capacity_left=F('location__capacity') - F('quantity'),
        barcode=F('location__barcode')
    ).order_by('capacity_left')[:3]

    if not locations.exists():
        return Response({"detail": "No locations found for this product"}, status=status.HTTP_404_NOT_FOUND)

    # Prepare response data
    locations_data = [
        {
            "location_id": location.location.id,
            "location_name": location.location.name,
            "aisle": location.location.aisle,
            "rack": location.location.rack,
            "level": location.location.level,
            "quantity": location.quantity,
            "barcode": location.barcode,
            "capacity_left": location.capacity_left
        }
        for location in locations
    ]

    response_data = {
        "order_detail_id": order_detail.id,
        "product_id": product.id,
        "product_name": product.name,
        "quantity": order_detail.quantity,
        "locations": locations_data
    }

    return Response(response_data, status=status.HTTP_200_OK)


# Pick Product API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsStaffUser])
def pickProduct(request, order_detail_id, location_barcode):
    try:
        order_detail = OrderDetail.objects.get(pk=order_detail_id)
    except OrderDetail.DoesNotExist:
        return Response({"detail": "Order detail not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        location = Location.objects.get(barcode=location_barcode)
    except Location.DoesNotExist:
        return Response({"detail": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

    quantity_to_pick = order_detail.quantity

    try:
        inventory_record = Inventory.objects.get(product=order_detail.product, location=location)
    except Inventory.DoesNotExist:
        return Response({"detail": "Inventory record not found for this product and location"}, status=status.HTTP_404_NOT_FOUND)

    if inventory_record.quantity < quantity_to_pick:
        return Response({"detail": "Not enough quantity in the location to pick"}, status=status.HTTP_400_BAD_REQUEST)

    # Adjust inventory record
    inventory_record.quantity -= quantity_to_pick
    if inventory_record.quantity == 0:
        inventory_record.delete()
    else:
        inventory_record.save()

    # Create stock movement record
    StockMovement.objects.create(
        product=order_detail.product,
        from_location=location,
        to_location=None,  
        quantity=quantity_to_pick,
        movement_type='pick'
    )

    # Create stock adjustment record if needed
    StockAdjustment.objects.create(
        product=order_detail.product,
        location=location,
        quantity=quantity_to_pick,
        adjustment_type='decrease',
        reason='Order picking'
    )

    # Create activity record
    Activity.objects.create(
        staff=request.user,
        description=f"Picked {quantity_to_pick} of {order_detail.product.name} from {location.name}",
        activity_type='pick'
    )

    # Create barcode scanning record
    BarcodeScanning.objects.create(
        scanned_by=request.user,
        scanned_item=order_detail.product,
        location=location,
        action='pick'
    )

    # Update order detail status
    order_detail.status = 'picked'
    order.updated_at_at = datetime.now().date()
    order_detail.save()

    # Check if all order details are picked, then update order status
    order = order_detail.order
    if all(detail.status == 'picked' for detail in order.orderdetail_set.all()):
        order.status = 'picked'
        order.save()

    Notification.objects.create(
        user=order.customer,
        message=f"Your order {order.id} has been picked.",
        status='unread'
    )

    return Response({"detail": "Product picked successfully"}, status=status.HTTP_200_OK)


# Pack Order API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
def packOrder(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if all order details are picked
    if not all(detail.status == 'picked' for detail in order.orderdetail_set.all()):
        return Response({"detail": "Not all order products are picked"}, status=status.HTTP_400_BAD_REQUEST)

    # Update order status to packed
    order.status = 'packed'
    order.updated_at_at = datetime.now().date()
    order.save()

    # Create activity record
    Activity.objects.create(
        staff=request.user,
        description=f"Packed Order ( ID:{order.id} ).",
        activity_type='pack'
    )

    # Send notification to the customer
    Notification.objects.create(
        user=order.customer,
        message=f"Your order {order.id} has been packed.",
        status='unread'
    )

    return Response({"detail": "Order packed successfully"}, status=status.HTTP_200_OK)


# List Packed Orders API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def listPackedOrders(request):
    packed_orders = Order.objects.filter(status='packed')
    serializer = OrderSerializer(packed_orders, many=True)
    return Response(serializer.data)


# Assign Orders To Delivery Man API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsStaffUser])
def assignOrdersToDeliveryMan(request):
    delivery_company = request.data.get('delivery_company')
    delivery_man_name = request.data.get('delivery_man_name')
    delivery_man_phone = request.data.get('delivery_man_phone')
    orders_ids = request.data.get('orders')  # List of order IDs

    if not (delivery_company and delivery_man_name and delivery_man_phone and orders_ids):
        return Response({"detail": "Incomplete data provided"}, status=status.HTTP_400_BAD_REQUEST)

    orders = Order.objects.filter(pk__in=orders_ids)

    # Update order status to delivered
    for order in orders:
        if order.status == 'cancelled':
            return Response({"detail": "Some orders has been cancelled"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'delivered'
        order.delivered_at = datetime.now().date()
        order.save()

        # Send notification to customer
        Notification.objects.create(
            user=order.customer,
            message=f"Your order {order.id} has been delivered.",
            status='unread'
        )

    # Create delivery record
    delivery_record = DeliveryRecord.objects.create(
        delivery_company=delivery_company,
        delivery_man_name=delivery_man_name,
        delivery_man_phone=delivery_man_phone,
    )
    delivery_record.orders.set(orders)

    # Create activity record
    activity_description = f"Orders {', '.join(str(order.id) for order in orders)} delivered by {delivery_man_name} from {delivery_company}"
    Activity.objects.create(
        staff=request.user,
        description=activity_description,
        activity_type='delivery',
    )

    return Response({"detail": "Orders assigned to delivery man successfully"}, status=status.HTTP_200_OK)


