from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from .serializers import CustomUserSerializer
from .models import CustomUser
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password


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
