from django.urls import path
from AppUser.views import CustomUserCreateAPIView, OTPViewSetCreateAPIView

urlpatterns = [
    path("users/", CustomUserCreateAPIView.as_view(), name="users"),
    path("generate_otp/", OTPViewSetCreateAPIView.as_view(), name="generate_otp"),

]
