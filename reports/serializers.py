import json
from rest_framework import serializers
from backend.models import Report, Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('id', 'report_type', 'generated_at', 'data')
        read_only_fields = ['id']



