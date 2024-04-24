from rest_framework import serializers
from .models import CustomUser, OTPViewSet


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'password', 'created_at', 'updated_at',
                  'is_deleted']


class OTPViewSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPViewSet
        fields = ['id', 'user_id', 'otp_str', 'is_expired']
