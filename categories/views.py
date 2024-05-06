from rest_framework.decorators import api_view, permission_classes, authentication_classes
from users.authentication import BearerTokenAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from backend.models import Category
from .serializers import CategorySerializer, CategoryNameSerializer


# List Categories API:
@api_view(['GET'])
@permission_classes([AllowAny])
def listCategories(request):
    categories = Category.objects.all()
    serializer = CategoryNameSerializer(categories, many=True)
    return Response(serializer.data)


# Category Info API:
@api_view(['GET'])
@permission_classes([AllowAny])
def categoryInfo(request, id):
    try:
        category = Category.objects.get(pk=id)
    except Category.DoesNotExist:
        return Response({"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CategorySerializer(category)
    return Response(serializer.data)


# Create Category API:
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def createCategory(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Category created successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update Category API:
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def updateCategory(request, id):
    try:
        category = Category.objects.get(pk=id)
    except Category.DoesNotExist:
        return Response({"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CategorySerializer(category, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Category updated successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete Category API:
@api_view(['DELETE'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def deleteCategory(request, id):
    try:
        category = Category.objects.get(pk=id)
    except Category.DoesNotExist:
        return Response({"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    category.delete()
    return Response({"detail": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


