"""
Serializers for User Authentication with CognoDB
"""
from rest_framework import serializers
from users.models import User, UserManager
import re


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration"""
    
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    phone_number = serializers.CharField(required=True, max_length=15)
    password = serializers.CharField(required=True, min_length=6, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        phone_regex = r'^\d{10}$'
        if not re.match(phone_regex, value):
            raise serializers.ValidationError("Phone number must contain exactly 10 digits.")
        return value
    
    def validate(self, data):
        """Validate password confirmation and uniqueness"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match."
            })
        
        # Check email uniqueness
        if UserManager.email_exists(data['email']):
            raise serializers.ValidationError({
                "email": "User with this email already exists."
            })
        
        # Check phone uniqueness
        if UserManager.phone_exists(data['phone_number']):
            raise serializers.ValidationError({
                "phone_number": "User with this phone number already exists."
            })
        
        return data
    
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('confirm_password')
        user = UserManager.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login with email or phone number"""
    
    login_identifier = serializers.CharField(required=False, allow_blank=False)
    username = serializers.CharField(required=False, allow_blank=False, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        """Validate login credentials"""
        login_identifier = (data.get('login_identifier') or data.get('username') or '').strip()
        password = data.get('password')
        
        if not login_identifier or not password:
            raise serializers.ValidationError("Email or phone number and password are required.")
        
        # Try to find user by email or phone number
        user = None
        if '@' in login_identifier:
            user = UserManager.get_user_by_email(login_identifier)
        else:
            user = UserManager.get_user_by_phone(login_identifier)
        
        if not user:
            raise serializers.ValidationError("Invalid email or phone number, or password.")
        
        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or phone number, or password.")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled. Please contact support.")
        
        data['user'] = user
        return data


class UserSerializer(serializers.Serializer):
    """Serializer for user profile"""
    
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    phone_number = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    def to_representation(self, instance):
        """Convert User instance to dictionary"""
        return instance.to_dict()