from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'confirm_password', 'role', 'location']

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        # Auto-generate a username if not provided
        username = validated_data.get('username')
        email = validated_data['email']
        if not username:
            username = email.split('@')[0]

        # Ensure the username is unique
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            role=validated_data.get('role', 'SUPPLIER'),
            location=validated_data.get('location', '')
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active', 'location', 'cooperative_center']
        read_only_fields = ['id']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'location', 'cooperative_center', 'role']
        read_only_fields = ['id', 'username', 'email', 'role']


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        email = data.get('email')
        password = data.get('password')
        
        # Explicitly fetch the user by email
        user = User.objects.filter(email=email).first()

        # Verify the user exists and the password is correct
        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")
            
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")

        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        # Enforces strong passwords as defined in settings.AUTH_PASSWORD_VALIDATORS
        validate_password(value)
        return value

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"token": "Invalid reset link"})

        if not PasswordResetTokenGenerator().check_token(user, attrs['token']):
            raise serializers.ValidationError({"token": "Invalid or expired reset link"})

        attrs['user'] = user
        return attrs