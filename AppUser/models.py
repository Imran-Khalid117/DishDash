from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.

class _BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_deleted = models.BooleanField(default=False)

    # Add more common fields as needed

    class Meta:
        abstract = True


class CustomUser(User):
    # Add any additional fields you need for your user model
    pass


class Meta:
    db_table = "user"
