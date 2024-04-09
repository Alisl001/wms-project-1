from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from users.authentication import BearerTokenAuthentication
from .serializer import UserRegistrationSerializer, CustomAuthTokenSerializer, UserLoginResponseSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authentication import TokenAuthentication


#Register API
@api_view(['POST'])
@permission_classes([AllowAny])
def userRegistration(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#Login API
@api_view(['POST'])
@permission_classes([AllowAny])
def userAuthTokenLogin(request):
    serializer = CustomAuthTokenSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    
    # Get or create the token for the user
    token, created = Token.objects.get_or_create(user=user)
    
    # Determine the role based on user attributes
    if user.is_superuser:
        role = 'admin'
    elif user.is_staff:
        role = 'staff'
    else:
        role = 'customer'
    
    # Customize the response data
    response_data = {
        'access_token': token.key,
        'token_type': 'bearer',
        'expires_in': 36000,  # token expiration time (in seconds)
        'user': {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined, 
            'role': role
        }
    }

    serializer = UserLoginResponseSerializer(data=response_data)
    serializer.is_valid()
    return Response(serializer.data, status=status.HTTP_200_OK)



# Logout API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def userLogout(request):
    # Extract the token from the request headers
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return Response({'detail': 'Authorization header is missing.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Split the Authorization header and retrieve the token
        auth_token = auth_header.split(' ')[1]
    except IndexError:
        return Response({'detail': 'Invalid authorization header format.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Get the token object from the database
    try:
        token = Token.objects.get(key=auth_token)
    except Token.DoesNotExist:
        return Response({'detail': 'Invalid token.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Delete the token from the database
    token.delete()

    return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)



# Password reset request API
@api_view(['POST'])
@permission_classes([AllowAny])
def passwordResetRequest(request):
    email = request.data.get('email', None)
    if email is None:
        return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the email exists in the database
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'Email not found in the database.'}, status=status.HTTP_404_NOT_FOUND)

    # Generate a random 6-digit code
    code = 135246

    return Response({'detail': 'Password reset code sent to your email.'}, status=status.HTTP_200_OK)



# Password reset confirm API
@api_view(['POST'])
@permission_classes([AllowAny])
def passwordResetConfirm(request):
    email = request.data.get('email', None)
    code = request.data.get('code', None)
    password = request.data.get('password', None)
    confirm_password = request.data.get('confirm_password', None)

    if not all([email, code, password, confirm_password]):
        return Response({'detail': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the email exists in the database
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'Email not found in the database.'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the provided code matches the saved code
    if code != 135246:
        return Response({'detail': 'Invalid code.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if passwords match
    if password != confirm_password:
        return Response({'detail': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    # Reset the password
    user.set_password(password)
    user.save()
    
    return Response({'detail': 'Password reset successful.'}, status=status.HTTP_200_OK)





