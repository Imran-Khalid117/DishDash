from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# Create your models here.


class CustomUser(AbstractUser):
    # Add any additional fields you need for your user model
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "user"


class OTPViewSet(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="email_otp")
    otp_str = models.CharField(max_length=6, blank=False, null=False)
    expired_at = models.DateTimeField(default=timezone.now)
    is_expired = models.BooleanField(default=False)

    class Meta:
        db_table = "otp_verification"
