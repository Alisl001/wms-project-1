from dataclasses import field
from itertools import product
from pyexpat import model
from rest_framework import serializers
from backend.models import Favorite, Product

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'product']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None


class MyFavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Favorite
        fields = ['product']


