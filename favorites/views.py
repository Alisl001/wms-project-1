from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from users.authentication import BearerTokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import status
from backend.models import Favorite, Product
from .serializers import FavoriteSerializer, MyFavoriteSerializer
from django.db.models import Count
from django.contrib.auth.models import User


# Create Favorite API:
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def createFavorite(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    
    if Favorite.objects.filter(customer=request.user, product=product).exists():
        return Response({"detail": "Product already favorited."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = FavoriteSerializer(data={'product': product_id})
    if serializer.is_valid():
        serializer.save(customer=request.user)
        return Response({"detail": "Product favorited successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete Favorite API based on Product ID:
@api_view(['DELETE'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteFavorite(request, product_id):
    try:
        favorite = Favorite.objects.get(customer=request.user, product_id=product_id)
    except Favorite.DoesNotExist:
        return Response({"detail": "Favorite not found for the specified product."}, status=status.HTTP_404_NOT_FOUND)
    
    favorite.delete()
    return Response({"detail": "Favorite deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# My Favorites API:
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def myFavorites(request):
    favorites = Favorite.objects.filter(customer=request.user)
    
    if not favorites:
        return Response({"detail": "Oops! Looks like you haven't favorited any products yet. Start exploring and add some favorites!"}, status=status.HTTP_404_NOT_FOUND)

    serializer = MyFavoriteSerializer(favorites, many=True)
    return Response(serializer.data)


# Top 10 Favorite products:
@api_view(['GET'])
@permission_classes([AllowAny])
def topFavoriteProducts(request):
    top_products = Favorite.objects.values('product').annotate(favorite_count=Count('product')).order_by('-favorite_count')[:10]
    
    # Retrieve the name, photo URL, and price of each product
    product_details = {}
    for item in top_products:
        product_id = item['product']
        product = Product.objects.filter(pk=product_id).first()
        if product:
            product_details[product_id] = {
                'name': product.name,
                'photo_url': product.photo.url if product.photo else None,
                'price': product.price
            }
        else:
            product_details[product_id] = {
                'name': 'Unknown',
                'photo_url': 'Unknown',
                'price': None
            }

    # Construct the response data with product name, photo URL, and price included
    data = [
        {
            'product_id': item['product'],
            'product_name': product_details[item['product']]['name'],
            'product_photo': product_details[item['product']]['photo_url'],
            'product_price': product_details[item['product']]['price'],
            'favorite_count': item['favorite_count']
        } 
        for item in top_products
    ]
    
    return Response(data)    


# Product Favorited By Users API:
@api_view(['GET'])
@permission_classes([AllowAny])
def productFavoritedByUsers(request, product_id):
    user_count = Favorite.objects.filter(product=product_id).values('customer').distinct().count()
    return Response({"product_id": product_id, "user_count": user_count})


# User Favorite Count API:
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def userFavoriteCount(request, user_id):

    user = User.objects.filter(id=user_id).first() 

    if not user:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    
    favorite_count = Favorite.objects.filter(customer=user_id).count()
    
    response_data = {
        "user_id": user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "favorite_count": favorite_count
    }
    
    return Response(response_data)


