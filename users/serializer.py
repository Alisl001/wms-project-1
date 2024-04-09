from django.contrib.auth.models import User
from rest_framework import serializers




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
