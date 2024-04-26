from rest_framework import serializers
from .models import CustomUser, OTPViewSet, UserProfile, UserType


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
    """
            This class in inherited from serializers.ModelSerializer class.

            Fields to show:
               'id', 'user_id', 'first_name', 'last_name', 'address', 'contact_number','longitude', 'latitude'
            """
    class Meta:
        model = UserProfile
        fields = ['id', 'user_id', 'first_name', 'last_name', 'address', 'contact_number','longitude', 'latitude']


class UserTypeSerializer(serializers.ModelSerializer):
    """
    This class in inherited from serializers.ModelSerializer class.

            Fields to show:
               'id', 'roll_type'

        You don't necessarily need to override the create method in the ModelViewSet if you're using a serializer
        that can handle array fields properly. If your serializer is configured correctly to handle array fields,
        you can rely on it to parse the incoming data and create the instance accordingly.

        Here's how you can handle array fields directly in your serializer without overriding the create method
        in the ModelViewSet:

        Serializer Configuration: Ensure your serializer is configured to handle the Rolls_type field properly.
        If you're using Django REST Framework's ModelSerializer, you may need to customize it to handle array fields
        appropriately. You can use ListField with a CharField for this purpose.

        Data Validation: Make sure your serializer is configured to validate and parse incoming data correctly.
        If the Rolls_type field is required or has specific validation rules, define them in your serializer.
        ModelViewSet Usage: Simply use your ModelViewSet subclass as usual without overriding the create method.
        The ModelViewSet will utilize your serializer's create method to handle the creation of instances.
    """
    # Rolls_type = serializers.ListField(child=serializers.CharField(max_length=50))

    class Meta:
        model = UserType
        fields = ['id', 'roll_type']
