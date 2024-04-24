from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from .serializers import CustomUserSerializer
from .models import CustomUser


class CustomUserCreateAPIView(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


custom_user_create_view = CustomUserCreateAPIView.as_view()

# Create your views here.
