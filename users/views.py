from ast import Not
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from users.authentication import BearerTokenAuthentication
from .serializer import UserRegistrationSerializer, CustomAuthTokenSerializer, UserLoginResponseSerializer, CustomUserSerializer, StaffSerializer, UserInfoUpdateSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authentication import TokenAuthentication
from django.utils import timezone


#Register API
@api_view(['POST'])
@permission_classes([AllowAny])
def userRegistration(request):
    first_name = request.data.get('first_name', None)
    last_name = request.data.get('last_name', None)
    email = request.data.get('email', None)
    username = request.data.get('username', None)
    password = request.data.get('password', None)
    confirm_password = request.data.get('confirm_password', None)  
    role = request.data.get('role', None)

    if not all([first_name, last_name, email, username, password, confirm_password, role]):
        return Response({'detail': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)
      
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
    
    token, created = Token.objects.get_or_create(user=user)
    
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

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
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return Response({'detail': 'Authorization header is missing.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        auth_token = auth_header.split(' ')[1]
    except IndexError:
        return Response({'detail': 'Invalid authorization header format.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        token = Token.objects.get(key=auth_token)
    except Token.DoesNotExist:
        return Response({'detail': 'Invalid token.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token.delete()

    return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)



# Password reset request API
@api_view(['POST'])
@permission_classes([AllowAny])
def passwordResetRequest(request):
    email = request.data.get('email', None)
    if email is None:
        return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

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
    codeVlue = "135246"

    if not all([email, code, password, confirm_password]):
        return Response({'detail': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'Email not found in the database.'}, status=status.HTTP_404_NOT_FOUND)

    if code != codeVlue:
        return Response({'detail': 'Invalid code.'}, status=status.HTTP_400_BAD_REQUEST)

    if password != confirm_password:
        return Response({'detail': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(password)
    user.save()
    
    return Response({'detail': 'Password reset successful.'}, status=status.HTTP_200_OK)



#User details by ID API
@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
@authentication_classes([BearerTokenAuthentication])
def retrieveUserById(request, id):
    try:
        user = User.objects.get(pk=id)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CustomUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)



# User Details by token API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated]) 
def myDetails(request):
    user = request.user
    serializer = CustomUserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)



# Change my password API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def changeMyPassword(request):
    user = request.user
    data = request.data

    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_new_password')

    if new_password != confirm_password:
        return Response({'detail': 'New password and confirm password do not match'}, status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(old_password):
        return Response({'detail': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({'detail': 'Password changed successfully'}, status=status.HTTP_200_OK)



# Update user information API
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def updateUserInfo(request):
    user = request.user
    data = request.data

    required_fields = ['first_name', 'last_name', 'email', 'username']
    missing_fields = [field for field in required_fields if field not in data]
    if len(missing_fields) == len(required_fields):
        return Response({'detail': 'At least one of the following fields is required: first_name, last_name, email, username'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserInfoUpdateSerializer(user, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "User info updated successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Delete user by id by admin API
@api_view(['DELETE'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def deleteUserById(request, id):
    try:
        user = User.objects.get(pk=id)
        user.delete()
        return Response({"detail": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# Delete user their own account API
@api_view(['DELETE'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteMyAccount(request):
    user = request.user

    try:
        user.delete()
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'detail': 'User account deleted successfully'}, status=status.HTTP_204_NO_CONTENT)



# Show the staff members API 
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def showStaffMembers(request):
    staff_members = User.objects.filter(is_staff=True)

    serializer = StaffSerializer(staff_members, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)




