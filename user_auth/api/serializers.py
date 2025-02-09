from wsgiref import validate
from django.contrib.auth.models import User
from ..models import Profile
from rest_framework.authtoken.models import Token
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
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
       
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class BusinessProfilesListSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    class Meta:
        model = Profile
        fields = [
            'user', 
            'tel',
            'location',
            'type', 
            'file', 
            'description', 
            'working_hours', 
        ]
 
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        user_representation = representation['user']
        user_representation['pk'] = user_representation.pop('id')
        user_representation['first_name'] = instance.first_name
        user_representation['last_name'] = instance.last_name

        return representation
    
class CustomerProfilesListSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    class Meta:
        model = Profile
        fields = ['user', 'type', 'file', 'uploaded_at']
 
    def to_representation(self, instance):
       
        representation = super().to_representation(instance)
        user_representation = representation['user']
        user_representation['pk'] = user_representation.pop('id')

        return representation
 