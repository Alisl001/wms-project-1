from rest_framework import serializers
from backend.models import ShipmentDetail, Inventory, Location, Product

class ShipmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentDetail
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
