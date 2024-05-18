from django.urls import path
from AppUser.views import PublicUserViewSet, OTPViewSetCreateAPIView, UserProfileViewSet, \
    BusinessProfileViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(f'user', PublicUserViewSet)
router.register(f"otp", OTPViewSetCreateAPIView)
router.register(f"userprofile", UserProfileViewSet)
router.register(f"business_profile", BusinessProfileViewSet)

urlpatterns = router.urls

