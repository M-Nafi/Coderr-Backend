from rest_framework import serializers
from reviews.models import Review
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'business_user', 'rating', 'description', 'reviewer', 'created_at', 'updated_at']
        read_only_fields = ['reviewer', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validates that the reviewer is authenticated and that he has not already rated
        the business profile. If the reviewer is not authenticated, it raises a
        serializers.ValidationError with a detail message "Bitte melde dich an, um eine
        Bewertung abzugeben.". If the reviewer has already rated the business profile,
        it raises a serializers.ValidationError with a detail message "Du kannst nur
        eine Bewertung pro Geschäftsprofil abgeben.".
        """
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError({"detail": ["Bitte melde dich an, um eine Bewertung abzugeben."]})
        if 'reviewer' in self.initial_data and int(self.initial_data['reviewer']) != user.id:
            raise serializers.ValidationError({"detail": ["Du kannst nur Bewertungen in deinem Namen abgeben."]})
        business_user = data.get('business_user')
        if self.instance is None and Review.objects.filter(reviewer=user, business_user=business_user).exists():
            raise serializers.ValidationError({"detail": ["Du kannst nur eine Bewertung pro Geschäftsprofil abgeben."]})
        return data

    def create(self, validated_data):
        """
        Creates a new review with the given validated data and the user from the request context.

        This method is overridden to set the reviewer field of the review to the user from the
        request context before calling the parent's create method.

        :param validated_data: The validated data to create the review with.
        :return: The created review instance.
        """
        
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)