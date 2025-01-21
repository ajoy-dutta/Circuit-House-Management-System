from .models import *
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password


class HonourBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = HonourBoard
        fields = '__all__'

    def validate(self, data):
        """
        Perform validation on ending_date and joining_date together.
        """
        joining_date = data.get('joining_date')
        ending_date = data.get('ending_date')

        if ending_date and joining_date and ending_date <= joining_date:
            raise serializers.ValidationError({
                "ending_date": "Ending date must be after the joining date."
            })

        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password=serializers.CharField(write_only=True)
    class Meta:
        model=get_user_model()
        fields=('username','profile_picture','email','password','confirm_password')

    def validate(self,data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Password doesn't match")
        return data

        # try:
        #     validate_password(data['password'])
        # except ValidationError as e:
        #     raise serializers.ValidationError({"password":e.messages})

        

    def create(self, validated_data):
        # logging.info(f"Validated data: {validated_data}")
        validated_data.pop('confirm_password')
        User = get_user_model()
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
        )
        if 'profile_picture' in validated_data:
            user.profile_picture = validated_data['profile_picture']
        user.is_approved = False
        user.save()
        return user


class StaffApproveSerializer(serializers.ModelSerializer):    
    class Meta:
        model=get_user_model()
        fields=('id','username','email','is_approved','role')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Check if the user is approved
        if not user.is_approved:
            raise AuthenticationFailed("Your account has not been approved yet.")

        return data

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        user = self.context['request'].user

        # Validate current password
        if not check_password(data['current_password'], user.password):
            raise serializers.ValidationError({"current_password": "Current password is incorrect"})

        # Validate new password and confirmation match
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "New passwords do not match"})

        # Validate password complexity
        try:
            validate_password(data['new_password'], user=user)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})

        return data
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_approved', 'profile_picture']
        

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email','phone', 'message', 'created_at']
        
        
class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffProfile
        fields = '__all__'

class MediaSerializer(serializers.ModelSerializer):
    class Meta:
            model = Media
            fields ='__all__'