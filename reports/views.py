import json
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from users.authentication import BearerTokenAuthentication
from backend.models import Report, Warehouse, Activity, Inventory, Order, OrderDetail, Shipment, ShipmentDetail, StockAdjustment, StockMovement, ReplenishmentRequest, Location, CycleCount
from .serializers import ReportSerializer
import pandas as pd
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Case, When, IntegerField
from django.db import models


# List Reports API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def listReports(request):
    reports = Report.objects.all().order_by('-generated_at')
    serializer = ReportSerializer(reports, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Report Detail API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def getReportById(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
    except Report.DoesNotExist:
        return Response({"detail": "Report not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReportSerializer(report)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Generate Report API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def generateReport(request):
    report_type = request.data.get('report_type')
    warehouse_id = request.data.get('warehouse_id')

    if not report_type:
        return Response({"detail": "Report type is required"}, status=status.HTTP_400_BAD_REQUEST)

    warehouse = None
    if warehouse_id:
        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)
        except Warehouse.DoesNotExist:
            return Response({"detail": "Warehouse not found"}, status=status.HTTP_404_NOT_FOUND)

    # Generate report data based on type
    if report_type == 'sales':
        data = generate_sales_report(warehouse)
    elif report_type == 'inventory':
        data = generate_inventory_report(warehouse)
    elif report_type == 'activity':
        data = generate_activity_report(warehouse)
    else:
        return Response({"detail": "Invalid report type"}, status=status.HTTP_400_BAD_REQUEST)

    # Serialize the data to JSON string before saving
    data_json = json.dumps(data)

    # Check if a similar report already exists
    similar_reports = Report.objects.filter(
        report_type=report_type,
        warehouse=warehouse,
        generated_at__year=datetime.now().year,
        generated_at__month=datetime.now().month,
        generated_at__day=datetime.now().day,
    )

    if similar_reports.exists():
        # If a similar report exists, retrieve the first instance
        report = similar_reports.first()
    else:
        # If no similar report exists, create a new Report instance
        report = Report(
            report_type=report_type,
            generated_at=datetime.now(),
            data=data_json,
            warehouse=warehouse
        )
        report.save()

    # Serialize the Report instance using ReportSerializer
    serializer = ReportSerializer(report)

    # Return the serialized data including the 'id'
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# Sales Report Function
def generate_sales_report(warehouse=None):
    # Extract shipment and order details
    if warehouse:
        shipment_details = ShipmentDetail.objects.filter(shipment__warehouse=warehouse).values(
            'product__name', 'product__category__name', 'quantity', 'price_at_shipment', 'shipment__receive_date')
        order_details = OrderDetail.objects.filter(order__warehouse=warehouse).values(
            'product__name', 'product__category__name', 'quantity', 'price_at_sale', 'order__created_at')
    else:
        shipment_details = ShipmentDetail.objects.all().values(
            'product__name', 'product__category__name', 'quantity', 'price_at_shipment', 'shipment__receive_date')
        order_details = OrderDetail.objects.all().values(
            'product__name', 'product__category__name', 'quantity', 'price_at_sale', 'order__created_at')

    # Convert to DataFrame for analysis
    shipments_df = pd.DataFrame(list(shipment_details))
    orders_df = pd.DataFrame(list(order_details))

    # Data cleaning and formatting
    shipments_df['shipment__receive_date'] = pd.to_datetime(shipments_df['shipment__receive_date'])
    orders_df['order__created_at'] = pd.to_datetime(orders_df['order__created_at'])

    # Calculate total sales and total revenue
    total_sales = int(orders_df['quantity'].sum())
    total_revenue = float((orders_df['quantity'] * orders_df['price_at_sale']).sum())

    # Calculate total cost from shipments
    total_cost = float((shipments_df['quantity'] * shipments_df['price_at_shipment']).sum())

    # Calculate net revenue (profit)
    net_revenue = float(total_revenue - total_cost)

    # Analysis: top selling products
    top_selling_products = orders_df.groupby('product__name')['quantity'].sum().nlargest(5).to_dict()

    # Analysis: sales by month
    orders_df['month'] = orders_df['order__created_at'].dt.to_period('M')
    sales_by_month = orders_df.groupby('month')['quantity'].sum().to_dict()

    # Analysis: revenue by month
    revenue_by_month = orders_df.groupby('month').apply(lambda x: float((x['quantity'] * x['price_at_sale']).sum())).to_dict()

    # Analysis: incoming shipments by month
    shipments_df['month'] = shipments_df['shipment__receive_date'].dt.to_period('M')
    incoming_shipments_by_month = shipments_df.groupby('month')['quantity'].sum().to_dict()

    # Analysis: sales performance by product category
    sales_by_category = orders_df.groupby('product__category__name')['quantity'].sum().to_dict()

    # Generate insights
    data = {
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'net_revenue': net_revenue,
        'top_selling_products': top_selling_products,
        'sales_by_month': {str(key): value for key, value in sales_by_month.items()},
        'revenue_by_month': {str(key): value for key, value in revenue_by_month.items()},
        'incoming_shipments_by_month': {str(key): value for key, value in incoming_shipments_by_month.items()},
        'sales_by_category': sales_by_category,
    }

    # Convert data to JSON serializable format
    json_data = serialize_to_json(data)

    # Create and save the report
    report = Report(
        report_type='sales',
        generated_at=datetime.now(),
        data=json_data,
        warehouse=warehouse
    )
    report.save()

    return json_data


# Inventory Reports Function

def generate_inventory_report(warehouse=None):
    try:
        # Extract inventory details
        if warehouse:
            inventory_details = Inventory.objects.filter(location__warehouse=warehouse).values(
                'product__name', 'product__category__name', 'quantity', 'expiry_date', 'status', 'location__name')
            stock_movements = StockMovement.objects.filter(from_location__warehouse=warehouse).values(
                'product__name', 'from_location__name', 'to_location__name', 'quantity', 'movement_type', 'timestamp')
            stock_adjustments = StockAdjustment.objects.filter(location__warehouse=warehouse).values(
                'product__name', 'location__name', 'quantity', 'adjustment_type', 'timestamp')
            cycle_counts = CycleCount.objects.filter(location__warehouse=warehouse).values(
                'product__name', 'location__name', 'counted_quantity', 'timestamp')
            replenishment_requests = ReplenishmentRequest.objects.filter(location__warehouse=warehouse).values(
                'product__name', 'location__name', 'quantity', 'status', 'timestamp')
        else:
            inventory_details = Inventory.objects.all().values(
                'product__name', 'product__category__name', 'quantity', 'expiry_date', 'status', 'location__name')
            stock_movements = StockMovement.objects.all().values(
                'product__name', 'from_location__name', 'to_location__name', 'quantity', 'movement_type', 'timestamp')
            stock_adjustments = StockAdjustment.objects.all().values(
                'product__name', 'location__name', 'quantity', 'adjustment_type', 'timestamp')
            cycle_counts = CycleCount.objects.all().values(
                'product__name', 'location__name', 'counted_quantity', 'timestamp')
            replenishment_requests = ReplenishmentRequest.objects.all().values(
                'product__name', 'location__name', 'quantity', 'status', 'timestamp')

        # Convert to DataFrame for analysis
        inventory_df = pd.DataFrame(list(inventory_details))
        stock_movements_df = pd.DataFrame(list(stock_movements))
        stock_adjustments_df = pd.DataFrame(list(stock_adjustments))
        cycle_counts_df = pd.DataFrame(list(cycle_counts))
        replenishment_requests_df = pd.DataFrame(list(replenishment_requests))

        # Data cleaning and formatting
        inventory_df['expiry_date'] = pd.to_datetime(inventory_df['expiry_date'], errors='coerce')

        # Check for empty DataFrames and column existence
        if not inventory_df.empty and 'product__name' in inventory_df.columns:
            total_stock_by_product = inventory_df.groupby('product__name')['quantity'].sum().to_dict()
            stock_status = inventory_df.groupby('status')['quantity'].sum().to_dict()
        else:
            total_stock_by_product = {}
            stock_status = {}

        if not stock_movements_df.empty and 'timestamp' in stock_movements_df.columns:
            stock_movements_df['timestamp'] = pd.to_datetime(stock_movements_df['timestamp'], errors='coerce')
            stock_movements_summary = stock_movements_df.groupby('movement_type')['quantity'].sum().to_dict()
        else:
            stock_movements_summary = {}

        if not stock_adjustments_df.empty and 'timestamp' in stock_adjustments_df.columns:
            stock_adjustments_df['timestamp'] = pd.to_datetime(stock_adjustments_df['timestamp'], errors='coerce')
            stock_adjustments_summary = stock_adjustments_df.groupby('adjustment_type')['quantity'].sum().to_dict()
        else:
            stock_adjustments_summary = {}

        if not cycle_counts_df.empty and 'timestamp' in cycle_counts_df.columns:
            cycle_counts_df['timestamp'] = pd.to_datetime(cycle_counts_df['timestamp'], errors='coerce')
            cycle_counts_summary = cycle_counts_df.groupby(['product__name', 'location__name'])['counted_quantity'].sum().to_dict()
        else:
            cycle_counts_summary = {}

        if not replenishment_requests_df.empty and 'timestamp' in replenishment_requests_df.columns:
            replenishment_requests_df['timestamp'] = pd.to_datetime(replenishment_requests_df['timestamp'], errors='coerce')
            replenishment_requests_summary = replenishment_requests_df.groupby('status')['quantity'].sum().to_dict()
        else:
            replenishment_requests_summary = {}

        # Generate insights
        data = {
            'total_stock_by_product': total_stock_by_product,
            'stock_status': stock_status,
            'stock_movements_summary': stock_movements_summary,
            'stock_adjustments_summary': stock_adjustments_summary,
            'cycle_counts_summary': cycle_counts_summary,
            'replenishment_requests_summary': replenishment_requests_summary,
        }

        # Convert data to JSON serializable format
        json_data = serialize_to_json(data)

        # Create and save the report
        report = Report(
            report_type='inventory',
            generated_at=datetime.now(),
            data=json_data,
            warehouse=warehouse
        )
        report.save()

        return json_data

    except KeyError as e:
        # Handle KeyError specifically for missing columns
        error_message = f"KeyError: {str(e)}"
        # Log the error or handle it accordingly (e.g., raise a custom exception, return an error response)

        # For demonstration, re-raise the exception
        raise e


# Activity Reports Function
def generate_activity_report(warehouse=None):
    try:
        # Get the current date and the start of the month
        today = datetime.today()
        start_of_month = today.replace(day=1)
        start_of_previous_month = (start_of_month - timedelta(days=1)).replace(day=1)

        # Filter activities based on warehouse if provided
        if warehouse:
            activities = Activity.objects.filter(staff__profile__warehouse=warehouse).values(
                'timestamp', 'activity_type', 'staff_id'
            )
        else:
            activities = Activity.objects.all().values(
                'timestamp', 'activity_type', 'staff_id'
            )

        # Convert to DataFrame for analysis
        activities_df = pd.DataFrame(list(activities))

        # Check if 'timestamp' column is present
        if 'timestamp' not in activities_df.columns:
            raise KeyError("'timestamp' column not found in activities_df")

        # Convert timestamps to datetime
        activities_df['timestamp'] = pd.to_datetime(activities_df['timestamp'], errors='coerce')

        # Filter activities for daily and monthly reports
        daily_activities_df = activities_df[activities_df['timestamp'].dt.date == today.date()]
        monthly_activities_df = activities_df[activities_df['timestamp'].dt.date >= start_of_month.date()]
        previous_month_activities_df = activities_df[
            (activities_df['timestamp'].dt.date >= start_of_previous_month.date()) &
            (activities_df['timestamp'].dt.date < start_of_month.date())
        ]

        # Check for empty DataFrames
        if daily_activities_df.empty:
            daily_summary = {}
            daily_staff_activity = {}
            most_active_staff_daily = None
        else:
            daily_summary = daily_activities_df.groupby('activity_type').size().to_dict()
            daily_staff_activity = daily_activities_df.groupby('staff_id').size().to_dict()
            most_active_staff_daily = daily_activities_df['staff_id'].value_counts().idxmax()

        if monthly_activities_df.empty:
            monthly_summary = {}
            monthly_staff_activity = {}
            most_active_staff_monthly = None
            monthly_activity_count = 0
        else:
            monthly_summary = monthly_activities_df.groupby('activity_type').size().to_dict()
            monthly_staff_activity = monthly_activities_df.groupby('staff_id').size().to_dict()
            most_active_staff_monthly = monthly_activities_df['staff_id'].value_counts().idxmax()
            monthly_activity_count = monthly_activities_df.shape[0]

        if previous_month_activities_df.empty:
            activity_growth = None  # Handle the case where there's no previous month data
        else:
            previous_month_activity_count = previous_month_activities_df.shape[0]
            if previous_month_activity_count == 0:
                activity_growth = None  # Handle the case where previous_month_activity_count is 0
            else:
                activity_growth = (monthly_activity_count - previous_month_activity_count) / previous_month_activity_count * 100

        # Generate insights
        data = {
            'daily_summary': daily_summary,
            'monthly_summary': monthly_summary,
            'daily_staff_activity': daily_staff_activity,
            'monthly_staff_activity': monthly_staff_activity,
            'most_active_staff_daily': most_active_staff_daily,
            'most_active_staff_monthly': most_active_staff_monthly,
            'activity_growth': activity_growth,
        }

        # Convert data to JSON serializable format
        json_data = serialize_to_json(data)

        # Create and save the report
        report = Report(
            report_type='activity',
            generated_at=datetime.now(),
            data=json_data,
            warehouse=warehouse
        )
        report.save()

        return json_data

    except KeyError as e:
        # Handle KeyError specifically for missing columns
        error_message = f"KeyError: {str(e)}"
        # Log the error or handle it accordingly (e.g., raise a custom exception, return an error response)

        # For demonstration, re-raise the exception
        raise e


def serialize_to_json(data):
    """Serialize data to JSON serializable format."""
    serialized_data = {}
    for key, value in data.items():
        if isinstance(value, pd.Series):
            value = value.to_dict()
        elif isinstance(value, pd.DataFrame):
            value = value.to_dict(orient='records')
        elif isinstance(value, dict):
            value = serialize_to_json(value)  # Recursively handle nested dictionaries
        elif isinstance(value, (int, float)):
            value = value  # Already JSON serializable
        else:
            value = str(value)  # Fallback to string representation for other types
        serialized_data[key] = value
    return serialized_data
