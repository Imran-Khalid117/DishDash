from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# Create your models here.


class CustomUser(AbstractUser):
    """
    This class in inherited from AbstractUser class so that we can leverage already created fields in user model.

    Fields:
        created_at: DateTime field - do not need to set, it has default value
        updated_at: DateTime field - do not need to set, it has default value
        is_deleted: Boolean field - do not need to set, it has default value
    """
    # Add any additional fields you need for your user model
    refresh_token = models.CharField(max_length=400, blank=True, null=True)
    access_token = models.CharField(max_length=400, blank=True, null=True)
    access_token_expiry = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "user"


class OTPViewSet(models.Model):
    """
        This class in inherited from models.Model class

        Fields:
            created_at: DateTime field - do not need to set, it has default value
            updated_at: DateTime field - do not need to set, it has default value
            is_deleted: Boolean field - do not need to set, it has default value
            user_id: Foreign Key from CustomUser model - Mandatory field
            otp_str: CharField - OTP will be saved in this field - Mandatory field
            expired_at: DateTime field - do not need to set, it has default value
            is_expired: Boolean field - do not need to set, it has default value
        """
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="email_otp")
    otp_str = models.CharField(max_length=6, blank=False, null=False)
    expired_at = models.DateTimeField(default=timezone.now)
    is_expired = models.BooleanField(default=False)

    class Meta:
        db_table = "otp_verification"


class UserProfile(models.Model):
    """
        This class in inherited from models.Model class

        Fields:
            user_id: Foreign Key from CustomUser model - Mandatory field
            first_name: CharField - First name - Mandatory field
            last_name: CharField - last_name - Mandatory field
            address: CharField - address - Mandatory field
            contact_number: CharField - contact_number - Mandatory field
            longitude: CharField - longitude - Mandatory field
            latitude: CharField - latitude - Mandatory field
            operating_hours: CharField - operating_hours - Mandatory field
            created_at: DateTime field - do not need to set, it has default value
            updated_at: DateTime field - do not need to set, it has default value
            is_deleted: Boolean field - do not need to set, it has default value
    """
    user_id = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="user_profile")
    first_name = models.CharField(max_length=20, blank=False, null=False)
    last_name = models.CharField(max_length=20, blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)
    contact_number = models.CharField(max_length=15, blank=False, null=False)
    longitude = models.CharField(max_length=30, blank=False, null=False)
    latitude = models.CharField(max_length=30, blank=False, null=False)
    # operating_hours = models.CharField(max_length=500, blank=False, null=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "user_profile"


class UserType(models.Model):
    """
        This class in inherited from models.Model class

        Fields:
            roll_type: CharField - roll_type - Mandatory field
            created_at: DateTime field - do not need to set, it has default value
            updated_at: DateTime field - do not need to set, it has default value
            is_deleted: Boolean field - do not need to set, it has default value
    """

    roll_type = models.CharField(max_length=20, blank=False, null=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "user_type"


class BusinessProfile(models.Model):
    """
           This class in inherited from models.Model class

           Fields:
               business_name: CharField - business_name- Mandatory field
               address: CharField - address - Mandatory field
               business_contact_number: CharField - contact_number - Mandatory field
               longitude: CharField - longitude - Mandatory field
               latitude: CharField - latitude - Mandatory field
               operating_hours: CharField - operating_hours - Mandatory field
               created_at: DateTime field - do not need to set, it has default value
               updated_at: DateTime field - do not need to set, it has default value
               is_deleted: Boolean field - do not need to set, it has default value
       """
    business_name = models.CharField(max_length=20, blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)
    business_contact_number = models.CharField(max_length=15, blank=False, null=False)
    longitude = models.CharField(max_length=30, blank=False, null=False)
    latitude = models.CharField(max_length=30, blank=False, null=False)
    operating_hours = models.CharField(max_length=500, blank=False, null=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "business_profile"


class BusinessManager(models.Model):
    """
       This class in inherited from models.Model class

       Fields:
            user_id: Foreign Key from CustomUser model - Mandatory field
            business_pofile_id: Foreign Key from BusinessProfile model - Mandatory field
            roll_name: CharField - roll_name - Mandatory field
            created_at: DateTime field - do not need to set, it has default value
            updated_at: DateTime field - do not need to set, it has default value
            is_deleted: Boolean field - do not need to set, it has default value
    """
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_business_manager_id")
    business_pofile_id = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE,
                                           related_name="business_manager_id")
    user_type_id = models.ForeignKey(UserType, on_delete=models.CASCADE, related_name="user_business_manager_id")
    roll_name = models.CharField(max_length=20, blank=False, null=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "business_manager"
