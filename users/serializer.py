from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.serializers import AuthTokenSerializer




class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    role = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'confirm_password', 'role')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        role = validated_data.pop('role')
        user = User.objects.create_user(
            **validated_data,
            is_staff=(role == 'staff' or role == 'admin'),
            is_superuser=(role == 'admin'), 
        )
        return user


UserModel = get_user_model()

class CustomAuthTokenSerializer(serializers.Serializer):
    
    username_or_email = serializers.CharField(label="Username or Email")
    password = serializers.CharField(label="Password", style={'input_type': 'password'})

    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')

        user = None

        # Check if the input is an email
        if '@' in username_or_email:
            try:
                user = UserModel.objects.get(email=username_or_email)
            except UserModel.DoesNotExist:
                pass  # User with the provided email doesn't exist

        # If the user is not found by email, try to authenticate with username
        if not user:
            user = authenticate(request=self.context.get('request'), username=username_or_email, password=password)

        if not user:
            msg = 'Unable to log in with provided credentials.'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class UserLoginResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()
    user = serializers.DictField(child=serializers.CharField())

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user']['date_joined'] = instance.user.date_joined.isoformat()
        return representation


class CustomUserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}  # Hide password field in responses

    def get_role(self, obj):
        if obj.is_superuser:
            return 'admin'
        elif obj.is_staff:
            return 'staff'
        else:
            return 'customer'

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class UserInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def validate(self, data):
        username = data.get('username')
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise serializers.ValidationError("Username is already in use.")

        email = data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise serializers.ValidationError("Email is already in use.")

        return data


