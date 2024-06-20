from celery import shared_task
from .models import Report
from .views import generate_sales_report, generate_inventory_report, generate_activity_report

@shared_task
def generate_reports():
    data = generate_sales_report(None)
    report = Report(report_type='sales', data=data)
    report.save()
