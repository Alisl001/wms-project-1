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
        fields = '__all__'

class ShipmentSerializer(serializers.ModelSerializer):
    details = ShipmentDetailSerializer(many=True, source='shipmentdetail_set')

    class Meta:
        model = Shipment
        fields = '__all__'

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        shipment = Shipment.objects.create(**validated_data)
        for detail_data in details_data:
            ShipmentDetail.objects.create(shipment=shipment, **detail_data)
        return shipment



