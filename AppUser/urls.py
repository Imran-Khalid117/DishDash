from django.urls import path
from rest_framework.routers import SimpleRouter
from AppUser.views import CustomUserViewSets, OTPViewSetCreateAPIView

router = SimpleRouter()
router.register(f'CustomUser', CustomUserViewSets)
router.register(f'OTPViewSet', OTPViewSetCreateAPIView)

urlpatterns = [
    path("CustomUser/signup/", CustomUserViewSets.as_view({'post': 'signup'}), name="signup"),
    path("CustomUser/login/", CustomUserViewSets.as_view({'post': 'login'}), name="login"),
    path("CustomUser/logout/", CustomUserViewSets.as_view({'post': 'logout'}), name="logout"),
    path("OTPViewSet/new_otp/", OTPViewSetCreateAPIView.as_view({'post': 'new_otp'}), name="new_otp"),

]
