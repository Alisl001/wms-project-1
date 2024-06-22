from rest_framework import serializers
from backend.models import Inventory, Location, Product, StockMovement, CycleCount, ReplenishmentRequest


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    location = LocationSerializer()
    class Meta:
        model = Inventory
        fields = '__all__'

class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = '__all__'


class CycleCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CycleCount
        fields = '__all__'

class ReplenishmentRequestSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    location = LocationSerializer()
    class Meta:
        model = ReplenishmentRequest
        fields = '__all__'