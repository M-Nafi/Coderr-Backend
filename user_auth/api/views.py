from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from user_auth.models import Profile
from rest_framework import status
from .serializers import RegistrationSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from user_auth.api.serializers import ProfileSerializer, BusinessProfilesListSerializer, CustomerProfilesListSerializer
 

class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        """
        Handles POST requests to register a new user.

        If the request is valid, the user is created and a JSON response
        containing the user's email, username, user_id and an authentication
        token is returned with a 201 Created status code. If the request is
        invalid, a JSON response containing the validation errors is returned
        with a 400 Bad Request status code.

        :param request: The request object.
        :return: A JSON response containing the user's email, username, user_id and an authentication token or a JSON response containing the validation errors.
        """
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "email": user.email,
                "username": user.username,
                "user_id": user.id,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        """
        Handles POST requests to log in a user.

        This method attempts to authenticate a user with the provided credentials.
        If the credentials are valid, it returns a JSON response containing the
        user's id, token, username, and email with a 200 OK status code. If the
        credentials are invalid, it returns a JSON response containing the validation
        errors with a 400 Bad Request status code.

        :param request: The HTTP request object containing user credentials.
        :return: A JSON response with user details and token or validation errors.
        """
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            data = {key: serializer.validated_data[key] for key in ["user_id", "token", "username", "email"]}
            return Response(data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 

class ProfileDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]
 
    def get(self, request, id):  
        """
        Retrieves the profile details for a user with the given ID.

        Fetches the profile associated with the user ID and returns it as a JSON response.
        The 'uploaded_at' field is omitted from the response data.

        :param request: The incoming request.
        :param id: The ID of the user whose profile is to be retrieved.
        :return: A JSON response containing the profile details with a 200 status code.
        :raises Http404: If the profile does not exist.
        """
        profile = get_object_or_404(Profile, user__id=id)
        serializer = ProfileSerializer(profile)
        data = serializer.data
        data.pop('uploaded_at', None)

        return Response(data, status=status.HTTP_200_OK)
 
    def patch(self, request, id, format=None):  
        """
        Partially updates the profile details for a user with the given ID.

        This method allows the authenticated user to update specific fields of their profile. 
        Only the fields specified in 'allowed_fields' can be updated. If any field outside 
        this list is provided, the request will return a 400 error with details of the invalid fields.

        :param request: The incoming request containing the data to update.
        :param id: The ID of the user whose profile is to be updated.
        :param format: The format of the request, default is None.
        :return: A JSON response containing the updated profile details with a 200 status code.
                 Returns a 400 status code with error details if the request is invalid.
        :raises PermissionDenied: If the authenticated user does not own the profile.
        """
        profile = get_object_or_404(Profile, user__id=id)
        if profile.user != request.user:
            raise PermissionDenied("Dir fehlt die Berechtigung, dieses Profil zu bearbeiten.")
        
        allowed_fields = {'username', 'first_name', 'last_name', 'email', 'location', 'description', 'working_hours', 'tel', 'file'}
        invalid_fields = [key for key in request.data if key not in allowed_fields]

        if invalid_fields:
            return Response({"detail": [f"Das Feld {', '.join(invalid_fields)} ist nicht erlaubt."]}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {key: value for key, value in request.data.items() if key in allowed_fields}
        serializer = ProfileSerializer(profile, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
 

class ProfileListBusiness(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get(self, request):
        """
        Returns a list of all business profiles.

        This method returns a JSON response containing a list of business profiles.
        Each profile is represented by a dictionary with the following keys:
        - `id`: The ID of the profile.
        - `user`: A dictionary with the user details.
        - `type`: The type of the profile (business or customer).
        - `file`: The path to the profile picture.
        - `uploaded_at`: The time when the profile picture was uploaded.
        - `description`: The description of the business.
        - `working_hours`: The working hours of the business.
        - `tel`: The phone number of the business.
        - `location`: The location of the business.

        :return: A JSON response containing the list of business profiles with a 200 status code.
        """
        profiles = Profile.objects.filter(type='business')
        serializer = BusinessProfilesListSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ProfileListCustomers(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get(self, request):
        """
        Retrieves a list of all customer profiles.

        This method queries the database for profiles with a type of 'customer' and returns
        them as a JSON response. Each profile includes user details, first and last name,
        profile picture URL (if available), upload timestamp, and profile type.

        :param request: The incoming HTTP request.
        :return: A JSON response containing a list of customer profiles with a 200 status code.
                Returns a 500 status code with an error message if an exception occurs.
        """
        try:
            profiles = Profile.objects.filter(type='customer')
            data = [
                {
                    "user": profile.user.id,
                    "username": profile.user.username,
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "file": profile.file.url if profile.file else None,
                    "uploaded_at": profile.uploaded_at,
                    "type": profile.type,
                }
                for profile in profiles
            ]
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)