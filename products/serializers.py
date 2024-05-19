from rest_framework import serializers
from backend.models import Product, Supplier, Category


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name','photo']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name','description']


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'supplier', 'size', 'price', 'barcode', 'photo']


class CustomProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    supplier = SupplierSerializer()

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
    supplier = SupplierSerializer()
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'supplier', 'price', 'photo']

