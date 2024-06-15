from rest_framework import serializers
from backend.models import Shipment, ShipmentDetail, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ShipmentDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = ShipmentDetail
        fields = ['id', 'shipment', 'product', 'price_at_shipment', 'quantity', 'status']

class ShipmentSerializer(serializers.ModelSerializer):
    details = ShipmentDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = ['supplier', 'arrival_date', 'receive_date', 'status', 'details']
        extra_kwargs = {
            'receive_date': {'required': False},
            'status': {'required': False, 'default': 'pending'}
        }
