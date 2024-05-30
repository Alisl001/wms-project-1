from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from backend.models import Product
from .serializers import ProductSerializer, ProductListSerializer, ProductSearchSerializer, CustomProductSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from users.authentication import BearerTokenAuthentication
from rest_framework import viewsets
from django.db.models import Q


# Create Product API:
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def createProduct(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Product created successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update Product API:
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def updateProduct(request, id):
    try:
        product = Product.objects.get(pk=id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Product updated successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete Product API:
@api_view(['DELETE'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def deleteProduct(request, id):
    try:
        product = Product.objects.get(pk=id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    product.delete()
    return Response({"detail": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# Get Product Info API:
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([AllowAny])
def getProductInfo(request, id):
    try:
        product = Product.objects.get(pk=id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CustomProductSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)


# List All Products API:
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([AllowAny])
def listProducts(request):
    products = Product.objects.all()
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# List Products by Category API:
@api_view(['GET'])
@permission_classes([AllowAny])
def listProductsByCategory(request, category_id):
    products = Product.objects.filter(category_id=category_id)
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# List Products by Supplier API:
@api_view(['GET'])
@permission_classes([AllowAny])
def listProductsBySupplier(request, supplier_id):
    products = Product.objects.filter(supplier_id=supplier_id)
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Products Search API:
@api_view(['GET'])
@permission_classes([AllowAny])
def productSearch(request):
    search_query = request.query_params.get('q', '')
    sort_by = request.query_params.get('sort_by', 'name')
    filter_by_category = request.query_params.get('category', None)
    filter_by_supplier = request.query_params.get('supplier', None)

    # Build filter conditions
    filter_conditions = Q()
    if filter_by_category:
        filter_conditions &= Q(category__name__icontains=filter_by_category)
    if filter_by_supplier:
        filter_conditions &= Q(supplier__name__icontains=filter_by_supplier)

    # Apply filtering and sorting
    products = Product.objects.filter(
        Q(name__icontains=search_query) |
        Q(supplier__name__icontains=search_query) |
        Q(category__name__icontains=search_query)
    ).filter(filter_conditions).order_by(sort_by)

    if not products:
        return Response({"detail": "No products found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSearchSerializer(products, many=True)
    return Response(serializer.data)


# Upload Product Photo API:
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def uploadProductPhoto(request, id):
    try:
        product = Product.objects.get(pk=id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check if a photo is included in the request
    if 'photo' not in request.FILES:
        return Response({"detail": "No photo provided in the request"}, status=status.HTTP_400_BAD_REQUEST)

    photo = request.FILES['photo']
    product.photo = photo
    product.save()

    return Response({"detail": "Photo uploaded successfully"}, status=status.HTTP_200_OK)


# Product Details By Barcode API:
@api_view(['GET'])
@permission_classes([AllowAny])
def getProductDetailsByBarcode(request, barcode):
    try:
        product = Product.objects.get(barcode=barcode)
    except Product.DoesNotExist:
        return Response({"detail": "Product with the provided barcode not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CustomProductSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Product name suggerstion in the search API:
@api_view(['GET'])
@permission_classes([AllowAny])
def productSuggestions(request):
    search_query = request.query_params.get('q', '')

    products = Product.objects.filter(name__icontains=search_query)

    suggested_names = products.values_list('name', flat=True).distinct()

    return Response(suggested_names)



