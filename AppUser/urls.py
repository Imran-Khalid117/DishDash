from django.urls import path
from AppUser.views import custom_user_create_view, OTPView_Set_Create_APIView

urlpatterns = [
    path("users/", custom_user_create_view, name="users"),
    path("generate_otp/", OTPView_Set_Create_APIView, name="generate_otp"),

]
