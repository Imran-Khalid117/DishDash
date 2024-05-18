import random
from datetime import timedelta

import boto3
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from DishDash import settings
from DishDash.general_functions import error_message, success_message
from .models import CustomUser, OTPVerification, UserProfile, BusinessProfile, BusinessManager, UserType, \
    SMSOTPVerification
from .serializers import CustomUserSerializer, OTPViewSetSerializer, UserProfileSerializer, BusinessProfileSerializer, \
    BusinessManagerSerializer, UserTypeSerializer, SMSOTPVerificationSerializer
from twilio.rest import Client


class PublicUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['post'])
    def signup(self, request: Request, *args, **kwargs) -> Response:
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
        response_status = status.HTTP_400_BAD_REQUEST
        try:
            request_data = request.data
            serializer = self.get_serializer(data=request_data)
            if not serializer.is_valid(raise_exception=True):
                response_dictionary = error_message('An error has occurred with message ')
                return Response(response_dictionary, status=response_status)

            new_user = CustomUser.objects.create_user(**request_data)
            serializer = CustomUserSerializer(instance=new_user, fields=["id", "username", "email"])

            response_status = status.HTTP_201_CREATED
            response_dictionary = success_message('user created', serializer.data, response_status)
        except Exception as e:
            response_dictionary = error_message('An error has occurred with message ' + str(e))
        return Response(response_dictionary, status=response_status)

    @action(methods=['POST'], detail=False)
    def login(self, request: Request, *args, **kwargs) -> Response:
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
        request_data = request.data
        # Step 2: In this try catch block we are testing following things.
        # 1) We will check if access token is set and if it expired then generate a new token
        # 2) We will check if access token is not expired then return same access token, refresh token and expiry date.
        # 3) We will also verify if user exists in database.

        try:
            # Step 2.3 extracting user details from DB if not then raise exception
            user = CustomUser.objects.get(username=request_data.get("username"))
            # Step 2.1 checking if access token of a user is already set
            if user.access_token_expiry:
                time_delta = (user.access_token_expiry - timezone.now()).total_seconds() / 3600
                # if access token is set we authenticate the user.
                if check_password(request_data.get("password"), user.password):
                    # After authentication, we verify that if token is expired - in case it is expired we generate
                    # a new token and save it.
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
                        response_status = status.HTTP_202_ACCEPTED
                        response_dictionary = success_message("User Authenticated and new Token generated",
                                                              data={'refresh': str(refresh), 'access': str(access),
                                                                    'access_token_expiry': user.access_token_expiry,
                                                                    })
                        return Response(response_dictionary, status=response_status)
                    else:
                        response_status = status.HTTP_202_ACCEPTED
                        response_dictionary = success_message("User Authenticated and new Token generated",
                                                              data={'refresh': str(user.refresh_token),
                                                                    'access': str(user.access_token),
                                                                    'access_token_expiry': user.access_token_expiry,
                                                                    })
                        return Response(response_dictionary, status=response_status)
                else:
                    response_status = status.HTTP_401_UNAUTHORIZED
                    response_dictionary = error_message('User not authenticated')
                    return Response(response_dictionary, status=response_status)
            else:
                # This block will fire if user access token expiry is empty, so we add new tokens and expiry date and
                # time.
                if check_password(request_data.get("password"), user.password):
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

                    response_status = status.HTTP_202_ACCEPTED
                    response_dictionary = success_message("User Authenticated and new Token generated",
                                                          data={'refresh': str(refresh), 'access': str(access),
                                                                'access_token_expiry': user.access_token_expiry,
                                                                })
                    return Response(response_dictionary, status=response_status)
                else:
                    response_status = status.HTTP_401_UNAUTHORIZED
                    response_dictionary = error_message('User not authenticated')
                    return Response(response_dictionary, status=response_status)
        except ValueError as e:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def logout(self, request: Request, *args, **kwargs) -> Response:
        """
            In this method we have implemented the logout functionality. This method will only be accessible
            if user is authenticated. This function receives username in request body and access token in request
            header.

            We filter out the user based on the username and extract the access token from the header. Access token
            is passed in header so that to make sure that user is authenticated user.

            Params:
            request: HTTP Request object - you can access all fields from this variable
            **args: These are additional parameters
            **kwargs: These are additional - optional keyword parameters

            return:  rest_framework.response object with status of OK of failure to requesting source for this API
        """
        request_data = request.data
        # extracting the user from database with respect to username provided in request body.
        user = CustomUser.objects.get(username=request_data.get("username"))
        jwt_token = None
        # We are checking here if application has provided access token if that is so then request header
        # will have Authorization key in request dictionary
        if 'Authorization' in request.headers:
            # Get the JWT token from the request headers
            auth_header = request.headers['Authorization']
            # Token should be in the format "Bearer <token>"
            jwt_token = auth_header.split()[1] if auth_header.startswith('Bearer') else None
        try:
            # If we have access token then we set all token and expiry field to none.
            if jwt_token:
                user.refresh_token = None
                user.access_token_expiry = None
                user.access_token = None
                user.save()
                response_status = status.HTTP_200_OK
                response_dictionary = success_message("Logout successful")
                return Response(response_dictionary, status=response_status)
            else:
                response_status = status.HTTP_400_BAD_REQUEST
                response_dictionary = error_message("Refresh token not provided")
                return Response(response_dictionary, status=response_status)
        except ObjectDoesNotExist:
            response_status = status.HTTP_404_NOT_FOUND
            response_dictionary = error_message("User does not exist")
            return Response(response_dictionary, status=response_status)
        except Exception as e:
            response_status = status.HTTP_401_UNAUTHORIZED
            response_dictionary = error_message("Invalid token")
            return Response(response_dictionary, status=response_status)


class OTPViewSetCreateAPIView(viewsets.ModelViewSet):
    """
    This class inherits from CreateAPIView generic class, that specifically designed for adding data into database.

    Methods:
        create: param(request: HTTPRequest object, **args, **kwargs) This method is override in order to process data
        before adding into database.
    """
    queryset = OTPVerification.objects.all()
    serializer_class = OTPViewSetSerializer

    @action(detail=False, methods=['post'])
    def new_email_otp(self, request: Request, *args: any, **kwargs: any) -> Response:
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
        request_data = request.data

        # Filter the OTPViewSet objects based on the user_id and get the last one
        ot_data = OTPVerification.objects.filter(user_id=request_data.get("user_id")).last()

        # Update the 'is_expired' field of the retrieved object
        if ot_data:
            if not ot_data.is_expired:
                ot_data.is_expired = True
                ot_data.save()  # Saving the is_expired value in database.

        "STEP2: We are generating the 6 digit otp and setting up the data to be saved"
        otp_random = random.randrange(100000, 1000000)
        request_data["otp_str"] = str(otp_random)
        email = request_data["email"]

        "STEP3: We are getting the correct serializer instance, validating the data and then saving it in database."
        serializer = self.get_serializer(data=request_data)
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

    @action(detail=False, methods=['post'])
    def verify_email_otp(self, request: Request, *args: any, **kwargs: any) -> Response:
        """
        In this method we are verifying the OTP provided by application through request body with entry in
        the database.

        Params:
        request: HTTP Request object - you can access all fields from this variable
        **args: These are additional parameters
        **kwargs: These are additional - optional keyword parameters

        return:  rest_framework.response object with status of OK of failure to requesting source for this API
        """
        # STEP1: Retrieving the user id to set the last entry of is_expired to false. For further clarity please
        # consult Project Manager or lead

        # STEP 2: We verify the OTP code provided by application with OTP entry in database

        # Retrieve the data from the request
        request_data = request.data

        # STEP1: Filter the OTPViewSet objects based on the user_id and get the last one
        ot_data = OTPVerification.objects.filter(user_id=request_data.get("user_id")).last()

        # STEP 2: This check should always be true as we are getting the last entry of OTP created, and it will have
        # active OTP.
        if not ot_data.is_expired:
            # comparing the OTP from request with OTP in database
            if request_data.get("otp") == ot_data.otp_str:
                # if they are matched we are going to expire this OTP entry in the database
                ot_data.is_expired = True
                ot_data.save()  # Saving the is_expired value in database.
                response_status = status.HTTP_200_OK
                response_dictionary = success_message("OTP MATCHED")
                return Response(response_dictionary, status=response_status)
            else:
                response_status = status.HTTP_404_NOT_FOUND
                response_dictionary = success_message("OTP DOES NOT MATCH")
                return Response(response_dictionary, status=response_status)
        else:
            response_status = status.HTTP_400_BAD_REQUEST
            response_dictionary = error_message("NO ACTIVE OTP FOUND")
            return Response(response_dictionary, status=response_status)

    @action(detail=False, methods=['post'])
    def new_sms_otp(self, request: Request, *args: any, **kwargs: any) -> Response:
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
        request_data = request.data
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_phone_number = settings.TWILIO_PHONE_NUMBER

        # Filter the OTPViewSet objects based on the user_id and get the last one
        ot_data = SMSOTPVerification.objects.filter(user_id=request_data.get("user_id")).last()
        # Update the 'is_expired' field of the retrieved object
        if ot_data:
            ot_data.is_expired = True
            ot_data.save()  # Saving the is_expired value in database.

        "STEP2: We are generating the 6 digit otp and setting up the data to be saved"
        otp_random = random.randrange(100000, 1000000)
        request_data["otp_str"] = str(otp_random)
        phone_no = request_data["phone_no"]

        "STEP3: We are getting the correct serializer instance, validating the data and then saving it in database."
        serializer = SMSOTPVerificationSerializer(data=request_data)
        try:
            # Validate the serializer data
            serializer.is_valid(raise_exception=True)
            # Creating new entry against the user id provided for OTP.
            serializer.save()
        except Exception as e:
            response_status = status.HTTP_400_BAD_REQUEST
            response_dictionary = error_message("OTP NOT SAVED" + str(e))
            return Response(response_dictionary, response_status)

        client = Client(account_sid, auth_token)

        try:
            message = client.messages.create(
                body=f"Your OTP for Quick Serve is : {otp_random}",
                from_=twilio_phone_number,
                to=phone_no
            )
            response_status = status.HTTP_200_OK
            response_dictionary = success_message("OTP SENT")
            return Response(response_dictionary, response_status)
        except Exception as e:
            response_status = status.HTTP_400_BAD_REQUEST
            response_dictionary = error_message("SMS NOT SENT" + str(e))
            return Response(response_dictionary, response_status)

    @action(detail=False, methods=['post'])
    def verify_sms_otp(self, request: Request, *args: any, **kwargs: any) -> Response:
        """
        In this method we are verifying the OTP provided by application through request body with entry in
        the database.

        Params:
        request: HTTP Request object - you can access all fields from this variable
        **args: These are additional parameters
        **kwargs: These are additional - optional keyword parameters

        return:  rest_framework.response object with status of OK of failure to requesting source for this API
        """
        # STEP1: Retrieving the user id to set the last entry of is_expired to false. For further clarity please
        # consult Project Manager or lead

        # STEP 2: We verify the OTP code provided by application with OTP entry in database

        # Retrieve the data from the request
        request_data = request.data

        # STEP1: Filter the OTPViewSet objects based on the user_id and get the last one
        ot_data = SMSOTPVerification.objects.filter(user_id=request_data.get("user_id")).last()

        # STEP 2: This check should always be true as we are getting the last entry of OTP created, and it will have
        # active OTP.
        if ot_data:
            if not ot_data.is_expired:
                # comparing the OTP from request with OTP in database
                if request_data.get("otp") == ot_data.otp_str:
                    # if they are matched we are going to expire this OTP entry in the database
                    ot_data.is_expired = True
                    ot_data.save()  # Saving the is_expired value in database.
                    response_status = status.HTTP_200_OK
                    response_dictionary = success_message("OTP MATCHED")
                    return Response(response_dictionary, status=response_status)
                else:
                    response_status = status.HTTP_404_NOT_FOUND
                    response_dictionary = success_message("OTP DOES NOT MATCH")
                    return Response(response_dictionary, status=response_status)
            else:
                response_status = status.HTTP_400_BAD_REQUEST
                response_dictionary = error_message("NO ACTIVE OTP FOUND")
                return Response(response_dictionary, status=response_status)


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

    @action(detail=False, methods=['post'])
    def add_profile(self, request: Request, *args: any, **kwargs: any) -> Response:
        request_data = request.data
        file = request.FILES["profile_image"]
        AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
        AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
        AWS_STORAGE_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
        AWS_S3_REGION_NAME = settings.AWS_S3_REGION_NAME
        file_name = "user_profile_image/" + file.name

        try:
            # Upload file to S3
            s3 = boto3.client('s3',
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                              region_name=AWS_S3_REGION_NAME)

            s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, file_name)
            file_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name}"
            request_data["profile_image"] = file_url
        except Exception as e:
            response_status = status.HTTP_400_BAD_REQUEST
            response_dictionary = error_message("NOT ABLE TO UPLOAD PICTURE ON S3" + str(e))
            return Response(response_dictionary, status=response_status)
        try:
            serializer = self.get_serializer(data=request_data)
            # Validate the serializer data
            serializer.is_valid(raise_exception=True)
            # Creating new entry against the user id provided for OTP.
            self.perform_create(serializer)
            response_status = status.HTTP_200_OK
            response_dictionary = success_message("PROFILE CREATED", serializer.data)
            return Response(response_dictionary, status=response_status)
        except Exception as e:
            response_status = status.HTTP_400_BAD_REQUEST
            response_dictionary = error_message("NOT ABLE TO SAVE PROFILE DATA" + str(e))
            return Response(response_dictionary, status=response_status)


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

    @action(detail=False, methods=['post'])
    def add_profile(self, request: Request, *args: any, **kwargs: any) -> Response:
        request_data = request.data
        file = request.FILES["business_profile_image"]
        AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
        AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
        AWS_STORAGE_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME
        AWS_S3_REGION_NAME = settings.AWS_S3_REGION_NAME
        file_name = "business_image/" + file.name

        try:
            # Upload file to S3
            s3 = boto3.client('s3',
                              aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                              region_name=AWS_S3_REGION_NAME)

            s3.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, file_name)
            file_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name}"
            request_data["business_profile_image"] = file_url
        except Exception as e:
            response_status = status.HTTP_400_BAD_REQUEST
            response_dictionary = error_message("NOT ABLE TO UPLOAD PICTURE ON S3" + str(e))
            return Response(response_dictionary, status=response_status)
        try:
            serializer = self.get_serializer(data=request_data)
            # Validate the serializer data
            serializer.is_valid(raise_exception=True)
            # Creating new entry against the user id provided for OTP.
            self.perform_create(serializer)
            response_status = status.HTTP_200_OK
            response_dictionary = success_message("PROFILE CREATED", serializer.data)
            return Response(response_dictionary, status=response_status)
        except Exception as e:
            response_status = status.HTTP_400_BAD_REQUEST
            response_dictionary = error_message("NOT ABLE TO SAVE PROFILE DATA" + str(e))
            return Response(response_dictionary, status=response_status)


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
