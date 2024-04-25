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
