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
      
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            data = {key: serializer.validated_data[key] for key in ["user_id", "token", "username", "email"]}
            return Response(data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 

class ProfileDetailsAPIView(APIView):
    permission_classes = [AllowAny]
 
    def get(self, request, id):  
        
        profile = get_object_or_404(Profile, user__id=id)
        serializer = ProfileSerializer(profile)
        data = serializer.data
        data.pop('uploaded_at', None)

        return Response(data, status=status.HTTP_200_OK)
 
    def patch(self, request, id, format=None):  
    
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

        return Response({**{key: serializer.data[key] for key in data}, "user": id}, status=status.HTTP_200_OK)
 

class ProfileListBusiness(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get(self, request):
        profiles = Profile.objects.filter(type='business')
        serializer = BusinessProfilesListSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ProfileListCustomers(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get(self, request):
        profiles = Profile.objects.filter(type='customer')
        serializer = CustomerProfilesListSerializer(profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)