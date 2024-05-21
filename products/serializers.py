from rest_framework import serializers
from backend.models import Product, Supplier, Category


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all())

    class Meta:
        model = Product
        fields = '__all__'


class CustomProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    supplier = SupplierSerializer()

    class Meta:
        model = Product
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer()
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = '__all__'


class ProductSearchSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer()
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = '__all__'

