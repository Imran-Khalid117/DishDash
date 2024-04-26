from rest_framework import serializers
from .models import CustomUser, OTPViewSet, UserProfile


class CustomUserSerializer(serializers.ModelSerializer):
    """
    This class in inherited from serializers.ModelSerializer class.

    Fields to show:
        'id', 'email', 'username', 'password', 'created_at', 'updated_at', 'is_deleted'

    """

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'password', 'created_at', 'updated_at',
                  'is_deleted']


class OTPViewSetSerializer(serializers.ModelSerializer):
    """
        This class in inherited from serializers.ModelSerializer class.

        Fields to show:
           'id', 'user_id', 'otp_str', 'is_expired'

        """

    class Meta:
        model = OTPViewSet
        fields = ['id', 'user_id', 'otp_str', 'is_expired']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user_id', 'first_name', 'last_name', 'address', 'contact_number','longitude', 'latitude',
                  'operating_hours']
