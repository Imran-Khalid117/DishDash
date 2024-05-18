from rest_framework import serializers
from .models import CustomUser, UserProfile, UserType, BusinessProfile, BusinessManager, OTPVerification, \
    SMSOTPVerification


class CustomUserSerializer(serializers.ModelSerializer):
    """
    This class in inherited from serializers.ModelSerializer class.

    Fields to show:
        'id', 'email', 'username', 'password', 'created_at', 'updated_at', 'is_deleted'

    """

    def __init__(self, *args, **kwargs):
        # Get the context passed during serialization
        fields_to_serialize = kwargs.pop('fields', None)

        super().__init__(*args, **kwargs)

        if fields_to_serialize:
            # Filter the fields based on the scenario
            allowed = set(fields_to_serialize)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

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
        model = OTPVerification
        fields = ['id', 'user_id', 'otp_str', 'is_expired']


class SMSOTPVerificationSerializer(serializers.ModelSerializer):
    """
        This class in inherited from serializers.ModelSerializer class.

        Fields to show:
           'id', 'user_id', 'otp_str', 'is_expired'

        """

    class Meta:
        model = SMSOTPVerification
        fields = ['id', 'user_id', 'otp_str', 'is_expired']


class UserProfileSerializer(serializers.ModelSerializer):
    """
            This class in inherited from serializers.ModelSerializer class.

            Fields to show:
               'id', 'user_id', 'profile_image', 'first_name', 'last_name', 'address', 'contact_number','longitude', 'latitude'
            """

    class Meta:
        model = UserProfile
        fields = ['id', 'user_id', 'first_name', 'last_name', 'address', 'contact_number',
                  'longitude', 'latitude', 'profile_image']


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
           'id', 'business_name', 'address', 'business_contact_number', 'longitude', 'latitude', 'operating_hours',
           'business_profile_image'
    """

    class Meta:
        model = BusinessProfile
        fields = ['id', 'business_name', 'address', 'business_contact_number',
                  'longitude', 'latitude', 'operating_hours', 'business_profile_image']


class BusinessManagerSerializer(serializers.ModelSerializer):
    """
          This class in inherited from serializers.ModelSerializer class.

          Fields to show:
            "id", "user_id", "business_pofile_id", "roll_name"
      """

    class Meta:
        model = BusinessManager
        fields = ["id", "user_id", "business_pofile_id", "user_type_id", "roll_name"]
