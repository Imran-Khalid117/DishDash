from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from DishDash import settings
from .serializers import CustomUserSerializer, OTPViewSetSerializer, UserProfileSerializer, UserTypeSerializer, \
    BusinessProfileSerializer, BusinessManagerSerializer
from .models import CustomUser, OTPViewSet, UserProfile, UserType, BusinessProfile, BusinessManager
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.contrib.auth.hashers import make_password, check_password
import random
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


class CustomUserViewSets(viewsets.ModelViewSet):
    """
    This class inherits from CreateAPIView generic class, that specifically designed for adding data into database.

    Methods:
        sign up: param(request: HTTPRequest object, **args, **kwargs)
            This is the method that will be called when creating a new user
        login: param (request: Request, pk=None, *args: any, **kwargs: any) -> Response:
            In this method we have implemented the login functionality.
        logout: param (request: Request, pk=None, *args: any, **kwargs: any) -> Response:
            In this method we are setting up logout functionality
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=True, methods=['post'])
    def signup(self, request: Request, *args: any, **kwargs: any) -> Response:
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
        serializer = self.get_serializer(data=data)
        try:
            # Validate the serializer data
            serializer.is_valid(raise_exception=True)
            # Create new object and save it in the database
            self.perform_create(serializer)
        except Exception as e:
            print(f"Unexpected error: {e}")

        # Return response
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def login(self, request: Request, pk=None, *args: any, **kwargs: any) -> Response:
        """
        This method implements the login functionality for user to login. We are also generating the access token,
        refresh token and calculated access token expiry field data and saving it in database.

        In case if user is just created - this method will generate the new access token,
        refresh token and calculated access token expiry field data and saving it in database.

        In case if user has access token it will check the expiry and in case expiry datatime is expired i.e. after 6hrs
        it will again generate a new access token, refresh token and update the access token expiry field.

        In case if access token is not expired based on the datatime saved it will return the same access token,
        refresh token and will not update the expiry datetime field.

        param:
        request: Request (Object) this pertains the request from the POST call from the calling application.
        **args: These are additional parameters
        **kwargs: These are additional - optional keyword parameters

        return:  rest_framework.response object with status of OK of failure to requesting source for this API.
        """
        # Step 1: we are extracting "username" and "password" from request data
        data = {"username": request.data.get('username'), "password": request.data.get('password')}

        # Step 2: In this try catch block we are testing following things.
        # 1) We will check if access token is set and if it expired then generate a new token
        # 2) We will check if access token is not expired then return same access token, refresh token and expiry date.
        # 3) We will also verify if user exists in database.
        try:
            # Step 2.3 extracting user details from DB if not then raise exception
            user = CustomUser.objects.get(username=data.get("username"))
            # Step 2.1 checking if access token of a user is already set
            if user.access_token_expiry:
                time_delta = (user.access_token_expiry - timezone.now()).total_seconds() / 3600
                # if access token is set we authenticate the user.
                if check_password(data.get("password"), user.password):
                    # After authentication, we verify that if token is expired - in case it is expired we generate
                    # a new token and save it
                    if time_delta < 0:
                        # Generate JWT tokens
                        refresh = RefreshToken.for_user(user)
                        access = AccessToken.for_user(user)

                        # Set expiration time for access token (e.g., 1 hour)
                        access_expiry = timezone.now() + timedelta(hours=6)

                        # Update user tokens and access token expiry
                        user.refresh_token = str(refresh)
                        user.access_token = str(access)
                        user.access_token_expiry = access_expiry
                        user.save()

                        return Response({
                            'refresh': str(refresh),
                            'access': str(access),
                            'access_token_expiry': user.access_token_expiry,
                        }, status=status.HTTP_201_CREATED)
                    else:
                        return Response({
                            'refresh': str(user.refresh_token),
                            'access': str(user.access_token),
                            'access_token_expiry': user.access_token_expiry,
                        }, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # This block will fire if user access token expiry is empty, so we create new entry.
                if check_password(data.get("password"), user.password):
                    login_data = {}
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    access = AccessToken.for_user(user)

                    # Set expiration time for access token (e.g., 1 hour)
                    access_expiry = timezone.now() + timedelta(hours=6)

                    # Update user tokens and access token expiry
                    user.refresh_token = str(refresh)
                    user.access_token = str(access)
                    user.access_token_expiry = access_expiry
                    user.save()

                    return Response({
                        'refresh': str(refresh),
                        'access': str(access),
                        'access_token_expiry': user.access_token_expiry,
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except ValueError:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def logout(self, request: Request) -> Response:
        data = {"username": request.data.get('username')}
        user = CustomUser.objects.get(username=data.get("username"))
        print(request.headers['Authorization'])
        jwt_token = None
        if 'Authorization' in request.headers:
            # Get the JWT token from the request headers
            auth_header = request.headers['Authorization']
            # Token should be in the format "Bearer <token>"
            jwt_token = auth_header.split()[1] if auth_header.startswith('Bearer') else None
        try:
            if jwt_token:
                # Blacklist the refresh token
                # token = RefreshToken(user.refresh_token)
                # token.blacklist()
                user.refresh_token = None
                user.access_token_expiry = None
                user.access_token = None
                user.save()
                return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Refresh token not provided"}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)


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

        # STEP1: Retrieving the user id to set the last entry of is_expired to false. For further clarity please
        # consult Project Manager or lead

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
        serializer = self.get_serializer(data=data)
        try:

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
        recipient_list = [email, ]
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


class BusinessProfileViewSet(viewsets.ModelViewSet):
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer

    """
    This class inherits from viewsets.ModelViewSet generic class, that specifically designed for adding, updating and
    retrieving.

    Methods to Access Data:
        To list all objects: GET /BusinessProfile/
        To retrieve a single object by its primary key: GET /BusinessProfile/{pk}/
        To create a new object: POST /BusinessProfile/
        To update an existing object completely: PUT /BusinessProfile/{pk}/
        To update an existing object partially: PATCH /BusinessProfile/{pk}/
        To delete an existing object: DELETE /BusinessProfile/{pk}/
    """


class BusinessManagerViewSet(viewsets.ModelViewSet):
    queryset = BusinessManager.objects.all()
    serializer_class = BusinessManagerSerializer

    """
    This class inherits from viewsets.ModelViewSet generic class, that specifically designed for adding, updating and
    retrieving.

    Methods to Access Data:
        To list all objects: GET /BusinessManager/
        To retrieve a single object by its primary key: GET /BusinessManager/{pk}/
        To create a new object: POST /BusinessManager/
        To update an existing object completely: PUT /BusinessManager/{pk}/
        To update an existing object partially: PATCH /BusinessManager/{pk}/
        To delete an existing object: DELETE /BusinessManager/{pk}/
    """
