from rest_framework import serializers
from backend.models import Order, OrderDetail, Product
from django.contrib.auth.models import User

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = OrderDetail
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    products = serializers.ListField(child=serializers.DictField(), write_only=True)
    customer = UserSerializer()
    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        total_price = 0

        # Calculate total price and set price_at_sale from the product's current price
        for product_data in products_data:
            product = Product.objects.get(id=product_data['product'])
            total_price += product.price * product_data['quantity']

        order = Order.objects.create(total_price=total_price, **validated_data)

        for product_data in products_data:
            product = Product.objects.get(id=product_data['product'])
            OrderDetail.objects.create(
                order=order,
                product=product,
                quantity=product_data['quantity'],
                price_at_sale=product.price,
                status='pending'
            )
        return order


