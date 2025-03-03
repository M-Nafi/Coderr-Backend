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
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)