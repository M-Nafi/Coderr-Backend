from rest_framework import serializers
from django.urls import reverse
from offers.models import Offer, OfferDetail
from django.db import models


class OfferUrlSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        return reverse('offerdetails', args=[obj.id])


class OfferSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at',
            'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details'
        ]
        extra_kwargs = {'user': {'read_only': True}}

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'POST':
            for field in ['created_at', 'updated_at', 'min_price', 'min_delivery_time', 'user_details', 'user']:
                data.pop(field, None)
        return data

    def validate(self, attrs):
        details_data = self.initial_data.get('details', [])
        errors = []
        validated_details = [
            detail_serializer.validated_data
            for detail in details_data
            if (detail_serializer := OfferDetailSerializer(data=detail)).is_valid()
            or errors.append(detail_serializer.errors)
        ]
        if errors:
            raise serializers.ValidationError({"detail": [errors]})
        attrs['validated_details'] = validated_details
        return attrs

    def get_details(self, obj):
        request = self.context.get('request')
        serializer_class = OfferDetailSerializer if request and request.method == 'POST' else OfferUrlSerializer
        return serializer_class(obj.details.all(), many=True).data

    def get_min_price(self, obj):
        return obj.details.aggregate(models.Min('price'))['price__min']

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(models.Min('delivery_time_in_days'))['delivery_time_in_days__min']

    def get_user_details(self, obj):
        profile = obj.user.profile
        return {"first_name": profile.first_name, "last_name": profile.last_name, "username": profile.username}

    def create(self, validated_data):
        validated_details = validated_data.pop('validated_details', [])
        offer = Offer.objects.create(**validated_data)
        OfferDetail.objects.bulk_create([OfferDetail(offer=offer, **detail) for detail in validated_details])
        return offer


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'id']
        extra_kwargs = {
            'id': {'read_only': True},
            'delivery_time_in_days': {'error_messages': {
                'invalid': "Der eingegebene Wert ist ungültig.",
                'min_value': "Die Lieferzeit muss mindestens 1 Tag betragen.",
                'required': "Dieses Feld darf nicht leer sein."
            }},
            'price': {'error_messages': {
                'invalid': "Der eingegebene Wert ist ungültig.",
                'min_value': "Der eingegebene Preis muss höher als 1 sein.",
                'required': "Dieses Feld darf nicht leer sein."
            }},
            'revisions': {'error_messages': {
                'invalid': "Der eingegebene Wert ist ungültig.",
                'min_value': "Die Anzahl der Revisionen muss eine positive Zahl sein.",
                'required': "Dieses Feld darf nicht leer sein."
            }},
        }

    def validate_delivery_time_in_days(self, value):
        if value < 1:
            raise serializers.ValidationError("Eingegebene Lieferzeit muss mindestens 1 Tag betragen.")
        return value

    def validate_price(self, value):
        if value <= 1:
            raise serializers.ValidationError("Eingegebener Preis muss höher als 1 sein.")
        return value

    def validate_revisions(self, value):
        if value < -1:
            raise serializers.ValidationError("Eingegebene Anzahl der Revisionen muss eine positive Zahl sein.")
        return value

    def validate_features(self, value):
        if not value:
            raise serializers.ValidationError("Mindestens eine Feature muss vorhanden sein.")
        return value
    
    
class OfferSingleDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

class AllOfferDetailsSerializer(serializers.ModelSerializer):
    details = OfferSingleDetailsSerializer(many=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'user_details', 'image', 'title', 'description', 
            'details', 'min_price', 'min_delivery_time', 'created_at', 'updated_at'
        ]

    def get_min_price(self, obj):
        return obj.details.aggregate(min_price=models.Min('price'))['min_price']

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(min_delivery=models.Min('delivery_time_in_days'))['min_delivery']

    def get_user_details(self, obj):
        user = obj.user
        profile = user.profile
        return {
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "username": profile.username
        }

    def validate(self, attrs):
        details_data = self.initial_data.get('details', [])
        errors = []
        for detail in details_data:
            detail_serializer = OfferDetailSerializer(data=detail)
            if not detail_serializer.is_valid():
                errors.append(detail_serializer.errors)

        if errors:
            raise serializers.ValidationError({"detail": errors})

        attrs['validated_details'] = [
            detail_serializer.validated_data 
            for detail_serializer in (OfferDetailSerializer(data=d) for d in details_data) 
            if detail_serializer.is_valid()
        ]
        return attrs

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if details_data:
            self._update_details(instance, details_data)
        instance.save()
        return instance

    def _update_details(self, instance, details_data):
        existing_details = {detail.id: detail for detail in instance.details.all()}

        for detail_data in details_data:
            detail_id = detail_data.get('id')
            if detail_id and detail_id in existing_details:
                self._update_detail_instance(existing_details.pop(detail_id), detail_data)
            else:
                OfferDetail.objects.create(offer=instance, **detail_data)

        for remaining_detail in existing_details.values():
            remaining_detail.delete()

    def _update_detail_instance(self, detail_instance, detail_data):
        for attr, value in detail_data.items():
            setattr(detail_instance, attr, value)
        detail_instance.save()