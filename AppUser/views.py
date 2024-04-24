from rest_framework.generics import CreateAPIView
from DishDash import settings
from .serializers import CustomUserSerializer, OTPViewSetSerializer
from .models import CustomUser, OTPViewSet
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
import random
from django.core.mail import send_mail


class CustomUserCreateAPIView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        # Access request data
        data = request.data
        # Extract password from request data
        password = data.get("password")
        # Hash the password
        hashed_password = make_password(password)
        # Update the data dictionary with the hashed password
        data["password"] = hashed_password
        # Create a serializer instance with the modified data
        serializer = self.get_serializer(data=data)
        # Validate the serializer data
        serializer.is_valid(raise_exception=True)
        # Save the data
        self.perform_create(serializer)

        # Return response
        return Response(serializer.data, status=status.HTTP_201_CREATED)


custom_user_create_view = CustomUserCreateAPIView.as_view()

# Create your views here.


class OTPViewSetCreateAPIView(CreateAPIView):
    queryset = OTPViewSet.objects.all()
    serializer_class = OTPViewSetSerializer

    def create(self, request, *args, **kwargs):

        otp_random = random.randrange(100000, 1000000)
        data = request.data
        data["otp_str"] = str(otp_random)
        email = data["email"]
        serializer = self.get_serializer(data=data)
        # Validate the serializer data
        serializer.is_valid(raise_exception=True)
        # Save the data
        self.perform_create(serializer)

        subject = 'Your OTP Password'
        message = f'Your OTP password is {otp_random}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email,]
        try:
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            # Handle all exceptions
            print(f"Unexpected error: {e}")

        # Return response
        return Response(serializer.data, status=status.HTTP_201_CREATED)


OTPView_Set_Create_APIView = OTPViewSetCreateAPIView.as_view()
