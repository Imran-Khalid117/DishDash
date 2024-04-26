from rest_framework.generics import CreateAPIView
from rest_framework.request import Request
from DishDash import settings
from .serializers import CustomUserSerializer, OTPViewSetSerializer, UserProfileSerializer, UserTypeSerializer
from .models import CustomUser, OTPViewSet, UserProfile, UserType
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.hashers import make_password
import random
from django.core.mail import send_mail


class CustomUserCreateAPIView(CreateAPIView):
    """
    This class inherits from CreateAPIView generic class, that specifically designed for adding data into database.

    Methods:
        create: param(request: HTTPRequest object, **args, **kwargs) This method is override in order to process
        data before adding into database.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request: Request, *args: any, **kwargs: any) -> Response:
        """
        In this method we are getting the email, username and password from calling function. This is sent in
        request body as a JSON object. Create method extracts the data provided process it and create a new user
        in the application. Where username is mandatory field in the user database.

        STEP 1: In this step we are extracting the user password from request object, hashing the object, and updating
        data object with new hashed password.

        STEP 2: we are creating user and saving it in the database.

        param:
        request: Request (Object) this pertains the request from the POST call from the calling application.
        **args: These are additional parameters
        **kwargs: These are additional - optional keyword parameters

        return:  rest_framework.response object with status of OK of failure to requesting source for this API
        """
        "STEP 1: "
        # Access request data
        data = request.data
        # Extract password from request data
        password = data.get("password")
        # Hash the password
        hashed_password = make_password(password)
        # Update the data dictionary with the hashed password
        data["password"] = hashed_password
        "STEP 2:"
        # Create a serializer instance with the modified data
        try:
            serializer = self.get_serializer(data=data)
            # Validate the serializer data
            serializer.is_valid(raise_exception=True)
            # Create new object and save it in the database
            self.perform_create(serializer)
        except Exception as e:
            print(f"Unexpected error: {e}")

        # Return response
        return Response(serializer.data, status=status.HTTP_201_CREATED)


custom_user_create_view = CustomUserCreateAPIView.as_view()

# Create your views here.


class OTPViewSetCreateAPIView(CreateAPIView):
    """
    This class inherits from CreateAPIView generic class, that specifically designed for adding data into database.

    Methods:
        create: param(request: HTTPRequest object, **args, **kwargs) This method is override in order to process data
        before adding into database.
    """
    queryset = OTPViewSet.objects.all()
    serializer_class = OTPViewSetSerializer

    def create(self, request: Request, *args: any, **kwargs: any) -> Response:
        """
        In this view method we are taking HTTP request from system, that provides user id and email.

        In Step 1 Retrieving the user id to set the last entry os is_expired to false.

        In step 2 we extra the user email to send the otp to user. We also generate the OTP.

        In step 3 we are validating and adding the otp in database against the user id.

        In step 4 we are emailing the otp on provided user email.

        In step 5 we are sending the response back to calling program.

        Params:
        request: HTTP Request object - you can access all fields from this variable
        **args: These are additional parameters
        **kwargs: These are additional - optional keyword parameters

        return:  rest_framework.response object with status of OK of failure to requesting source for this API
        """

        "STEP1: Retrieving the user id to set the last entry of is_expired to false. For further clarity please"\
            "consult Project Manager or lead"
        # Retrieve the data from the request
        data = request.data

        # Filter the OTPViewSet objects based on the user_id and get the last one
        ot_data = OTPViewSet.objects.filter(user_id=data.get("user_id")).last()

        # Update the 'is_expired' field of the retrieved object
        if ot_data:
            ot_data.is_expired = True
            ot_data.save()  # Saving the is_expired value in database.

        "STEP2: We are generating the 6 digit otp and setting up the data to be saved"
        otp_random = random.randrange(100000, 1000000)
        data["otp_str"] = str(otp_random)
        email = data["email"]

        "STEP3: We are getting the correct serializer instance, validating the data and then saving it in database."
        try:
            serializer = self.get_serializer(data=data)
            # Validate the serializer data
            serializer.is_valid(raise_exception=True)
            # Creating new entry against the user id provided for OTP.
            self.perform_create(serializer)
        except Exception as e:
            print(f"Unexpected error: {e}")

        "STEP4: Sending OTP to user email "
        subject = 'Your OTP Password'
        message = f'Your OTP password is {otp_random}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email,]
        try:
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            # Handle all exceptions
            print(f"Unexpected error: {e}")

        "STEP5: Returning status response back to calling program"
        # Return response
        return Response(serializer.data, status=status.HTTP_201_CREATED)


OTPView_Set_Create_APIView = OTPViewSetCreateAPIView.as_view()


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    """
    This class inherits from viewsets.ModelViewSet generic class, that specifically designed for adding, updating and
    retrieving.
    
    Methods to Access Data:
        To list all objects: GET /UserProfile/
        To retrieve a single object by its primary key: GET /UserProfile/{pk}/
        To create a new object: POST /UserProfile/
        To update an existing object completely: PUT /UserProfile/{pk}/
        To update an existing object partially: PATCH /UserProfile/{pk}/
        To delete an existing object: DELETE /UserProfile/{pk}/
    """


class UserTypeViewSet(viewsets.ModelViewSet):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer

    """
    This class inherits from viewsets.ModelViewSet generic class, that specifically designed for adding, updating and
    retrieving.

    Methods to Access Data:
        To list all objects: GET /UserType/
        To retrieve a single object by its primary key: GET /UserType/{pk}/
        To create a new object: POST /UserType/
        To update an existing object completely: PUT /UserType/{pk}/
        To update an existing object partially: PATCH /UserType/{pk}/
        To delete an existing object: DELETE /UserType/{pk}/
    """