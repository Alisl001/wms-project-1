from rest_framework import serializers
from backend.models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class CategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
