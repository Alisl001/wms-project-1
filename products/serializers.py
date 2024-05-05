from rest_framework import serializers
from backend.models import Product, Supplier, Category


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


class ProductSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer()
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'supplier', 'size', 'price', 'barcode', 'photo']


class ProductListSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer()
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'barcode', 'category', 'supplier', 'price', 'photo']


class ProductSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'barcode', 'category', 'supplier', 'price']