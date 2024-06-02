from rest_framework import serializers
from backend.models import Inventory, Location, Product


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

