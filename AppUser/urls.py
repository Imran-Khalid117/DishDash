from django.urls import path
from AppUser.views import custom_user_create_view

urlpatterns = [
    path("users/", custom_user_create_view, name="users")
]
