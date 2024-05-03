from django.urls import path
from rest_framework.routers import SimpleRouter
from AppUser.views import CustomUserViewSets, OTPViewSetCreateAPIView

router = SimpleRouter()
router.register(f'CustomUser', CustomUserViewSets)

urlpatterns = [
    path("CustomUser/signup/", CustomUserViewSets.as_view({'post': 'signup'}), name="signup"),
    path("CustomUser/login/", CustomUserViewSets.as_view({'post': 'login'}), name="login"),
    path("generate_otp/", OTPViewSetCreateAPIView.as_view(), name="generate_otp"),

]
