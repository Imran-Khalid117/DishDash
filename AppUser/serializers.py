from rest_framework import serializers
from .models import CustomUser, OTPViewSet, UserProfile, UserType, BusinessProfile, BusinessManager


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

        Explaining the code below:
        Rolls_type = serializers.ListField(child=serializers.CharField(max_length=50))
        You don't necessarily need to override the create method in the ModelViewSet if you're using a serializer
        that can handle array fields properly. If your serializer is configured correctly to handle array fields,
        you can rely on it to parse the incoming data and create the instance accordingly.

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


class BusinessProfileSerializer(serializers.ModelSerializer):
    """
        This class in inherited from serializers.ModelSerializer class.

        Fields to show:
           'id', 'business_name', 'address', 'business_contact_number', 'longitude', 'latitude', 'operating_hours'
    """
    class Meta:
        model = BusinessProfile
        fields = ['id', 'business_name', 'address', 'business_contact_number',
                  'longitude', 'latitude', 'operating_hours']


class BusinessManagerSerializer(serializers.ModelSerializer):
    """
          This class in inherited from serializers.ModelSerializer class.

          Fields to show:
            "id", "user_id", "business_pofile_id", "roll_name"
      """
    class Meta:
        model = BusinessManager
        fields = ["id", "user_id", "business_pofile_id", "user_type_id","roll_name"]

