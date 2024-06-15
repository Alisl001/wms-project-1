from itertools import product
from rest_framework import serializers
from backend.models import ShipmentDetail, Inventory, Location, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class ShipmentDetailSerializer(serializers.ModelSerializer):
    product=ProductSerializer()
    class Meta:
        model = ShipmentDetail
        fields = '__all__'
