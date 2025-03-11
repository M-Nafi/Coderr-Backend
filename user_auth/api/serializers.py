from wsgiref import validate
from django.contrib.auth.models import User
from ..models import Profile
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from django.shortcuts import get_object_or_404


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validates the provided username and password.

        This method checks if a user with the given username exists and if the 
        password is correct. If the credentials are invalid, it raises a 
        serializers.ValidationError with a detail message "Falscher Benutzername 
        oder falsches Passwort.". If the credentials are valid, it creates or 
        retrieves an authentication token for the user and adds the user's ID, 
        token, and email to the validated data.

        :param data: The data containing the username and password.
        :return: The validated data updated with the user's ID, token, and email.
        """
        username = data.get("username")
        password = data.get("password")
        user = User.objects.filter(username=username).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError({"detail": ["Falscher Benutzername oder falsches Passwort."]})

        token, _ = Token.objects.get_or_create(user=user)

        data.update({
            "user_id": user.id,
            "token": token.key,
            "email": user.email
        })
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "E-Mail erforderlich.",
            "invalid": "E-Mail ungültig.",
            "unique": "Benutzername oder E-Mail existiert bereits."
        }
    )
    username = serializers.CharField(
        required=True,
        error_messages={"unique": ["Benutzername oder E-Mail existiert bereits."]}
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
    )
    repeated_password = serializers.CharField(
        write_only=True,
        required=True,
    )
    type = serializers.ChoiceField(
        choices=[('customer', 'customer'), ('business', 'business')]
    )
 
    class Meta:
        model = User
        fields = ['username', 'password', 'repeated_password', 'email', 'type']
 
    def validate(self, data):
        """
        Validates the given data and raises a serializers.ValidationError
        if the data is invalid.

        This method checks if the given username and email are unique and if
        the given passwords match. If the username or email already exist,
        it raises a serializers.ValidationError with a detail message
        "Benutzername oder E-Mail existiert bereits.". If the passwords do not
        match, it raises a serializers.ValidationError with a detail message
        "Passwörter stimmt nicht überein.".

        :param data: The given data to validate.
        :return: The validated data.
        :raises serializers.ValidationError: If the data is invalid.
        """
        if User.objects.filter(username=data['username']).exists() or User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                {"detail": ["Benutzername oder E-Mail existiert bereits."]}
            )
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {"detail": ["Passwörter stimmt nicht überein."]}
            )
        return data
    
    def create(self, validated_data):
        """
        Creates a new user and associated profile with the given validated data.

        This method uses the provided validated data to create a new user in the 
        database and then creates an associated profile for the user with the 
        specified type. The user is created using the `create_user` method of the 
        `User` model. A `Profile` instance is created and linked to the user.

        :param validated_data: The validated data containing the username, email, 
                            password, and user type.
        :return: The created `User` instance.
        """
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        user_type = validated_data['type']

        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user, email=email, type=user_type)
        return user
       

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        extra_kwargs = {
            'first_name': {'error_messages': {'blank': "Dieses Feld darf nicht leer sein."}},
            'last_name': {'error_messages': {'blank': "Dieses Feld darf nicht leer sein."}},
            'email': {'error_messages': {'blank': "Dieses Feld darf nicht leer sein.", 'required': "Dieses Feld ist erforderlich.", 'unique': "Email existiert bereits."}},
            'location': {'error_messages': {'blank': "Dieses Feld darf nicht leer sein."}},
            'description': {'error_messages': {'blank': "Dieses Feld darf nicht leer sein."}},
            'working_hours': {'error_messages': {'blank': "Dieses Feld darf nicht leer sein."}},
            'tel': {'error_messages': {'blank': "Dieses Feld darf nicht leer sein."}},
        }
 
    def validate(self, attrs):
        """
        Validates the given data and raises a serializers.ValidationError
        if the data is invalid.

        This method checks that the given data only contains fields that are
        allowed to be updated. If the given data contains fields that are not
        allowed to be updated, it raises a serializers.ValidationError with a
        detail message "Das Feld [field names] kann nicht aktualisiert werden.
        Nur das Feld [allowed fields] darf aktualisiert werden.".

        :param attrs: The given data to validate.
        :return: The validated data.
        :raises serializers.ValidationError: If the data is invalid.
        """
        allowed_fields = {
            'first_name', 
            'last_name', 
            'email',
            'file', 
            'location', 
            'description', 
            'tel', 
            'user', 
            'working_hours',
        }
        extra_fields = [key for key in self.initial_data.keys() if key not in allowed_fields]
 
        if extra_fields:
            raise serializers.ValidationError(
                {"detail": f"Das Feld {', '.join(extra_fields)} kann nicht aktualisiert werden. Nur das Feld {', '.join(allowed_fields)} darf aktualisiert werden."}
            )
        return attrs
 
    def update(self, instance, validated_data):
        """
        Updates the given profile instance with the given validated data.

        This method loops through the validated data and updates the corresponding
        fields of the profile instance. Additionally, it updates the first_name and
        last_name fields of the related User instance. The method returns the updated
        profile instance.

        :param instance: The profile instance to update.
        :param validated_data: The validated data to update the profile with.
        :return: The updated profile instance.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            user = instance.user
            user = get_object_or_404(User, pk=user.id)
            user.first_name = instance.first_name
            user.last_name = instance.last_name
            user.location = instance.location

            user.save()
        instance.save()

        return instance


class BusinessProfilesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name', 
            'tel',
            'location',
            'type', 
            'file', 
            'description', 
            'working_hours', 
        ]
 
    

class CustomerProfilesListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['user', 'type', 'file', 'uploaded_at']
 

 