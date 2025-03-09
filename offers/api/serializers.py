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
        """
        Returns a URL to the detail view of the offer.
        
        :param obj: The offer to generate the URL for.
        :return: A URL to the detail view of the offer.
        """
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
        """
        Customizes the serialized representation of an Offer instance.

        This method removes certain fields from the serialized data when
        handling a POST request. Specifically, it removes the 'created_at',
        'updated_at', 'min_price', 'min_delivery_time', 'user_details', and
        'user' fields. For other request methods, it returns the default
        representation.

        :param instance: The Offer instance being serialized.
        :return: A dictionary representing the serialized data of the instance,
                with specified fields removed for POST requests.
        """
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'POST':
            for field in ['created_at', 'updated_at', 'min_price', 'min_delivery_time', 'user_details', 'user']:
                data.pop(field, None)
        return data

    def validate(self, attrs):
        """
        Validates the 'details' data provided in the initial data.

        This method checks if each detail in the 'details' list is valid using the
        `OfferDetailSerializer`. If any detail is invalid, it collects the errors
        and raises a `ValidationError` with the details of all errors encountered.
        If all details are valid, it adds the validated details to the `attrs`
        dictionary under the key 'validated_details'.

        :param attrs: The attributes to validate.
        :return: The validated attributes with 'validated_details' added.
        :raises serializers.ValidationError: If any detail is invalid.
        """
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
        """
        Returns a serialized representation of the OfferDetails associated with the Offer instance.

        When handling a POST request, it uses the `OfferDetailSerializer` to serialize the
        `OfferDetail` instances. Otherwise, it uses the `OfferUrlSerializer` to serialize the
        `OfferDetail` instances, which only includes the 'id' and 'url' fields.

        :param obj: The Offer instance being serialized.
        :return: A list of serialized `OfferDetail` instances.
        """
        request = self.context.get('request')
        serializer_class = OfferDetailSerializer if request and request.method == 'POST' else OfferUrlSerializer
        return serializer_class(obj.details.all(), many=True).data

    def get_min_price(self, obj):
        """
        Returns the minimum price of the offer details associated with the offer.

        This method returns the minimum price of the offer details associated with the offer.
        If there are no offer details associated with the offer, it returns `None`.

        :param obj: The offer instance being serialized.
        :return: The minimum price of the offer details associated with the offer.
        """
        return obj.details.aggregate(models.Min('price'))['price__min']

    def get_min_delivery_time(self, obj):
        """
        Returns the minimum delivery time in days of the offer details associated with the offer.

        This method returns the minimum delivery time in days of the offer details associated with the offer.
        If there are no offer details associated with the offer, it returns `None`.

        :param obj: The offer instance being serialized.
        :return: The minimum delivery time in days of the offer details associated with the offer.
        """
        return obj.details.aggregate(models.Min('delivery_time_in_days'))['delivery_time_in_days__min']

    def get_user_details(self, obj):
        """
        Retrieves the details of the user associated with the offer.

        This method fetches the profile of the user related to the provided offer
        instance and constructs a dictionary containing the user's first name, 
        last name, and username.

        :param obj: The offer instance containing the user information.
        :return: A dictionary with the user's first name, last name, and username.
        """
        profile = obj.user.profile
        return {"first_name": profile.first_name, "last_name": profile.last_name, "username": profile.username}

    def create(self, validated_data):
        """
        Creates an offer and its related offer details.

        This method creates an offer from the validated data and then creates all
        related offer details from the validated details data in the 'validated_details'
        key of the validated data dictionary. The method returns the created offer.

        :param validated_data: The validated data from the request.
        :return: The created offer instance.
        """
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
        """
        Validates that the given delivery time is at least 1 day.

        :param value: The given delivery time to validate.
        :return: The validated delivery time.
        :raises serializers.ValidationError: If the given delivery time is less than 1 day.
        """
        if value < 1:
            raise serializers.ValidationError("Eingegebene Lieferzeit muss mindestens 1 Tag betragen.")
        return value

    def validate_price(self, value):
        """
        Validates that the given price is greater than 1.

        :param value: The given price to validate.
        :return: The validated price.
        :raises serializers.ValidationError: If the given price is less than or equal to 1.
        """
        if value <= 1:
            raise serializers.ValidationError("Eingegebener Preis muss höher als 1 sein.")
        return value

    def validate_revisions(self, value):
        """
        Validates that the given number of revisions is at least -1.

        :param value: The given number of revisions to validate.
        :return: The validated number of revisions.
        :raises serializers.ValidationError: If the given number of revisions is less than -1.
        """
        if value < -1:
            raise serializers.ValidationError("Eingegebene Anzahl der Revisionen muss eine positive Zahl sein.")
        return value

    def validate_features(self, value):
        """
        Validates that the features field is not empty.

        :param value: The given features to validate.
        :return: The validated features.
        :raises serializers.ValidationError: If the features field is empty.
        """
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
        """
        Returns the minimum price of the offer details of the given offer.

        :param obj: The given offer.
        :return: The minimum price of the offer details.
        """
        return obj.details.aggregate(min_price=models.Min('price'))['min_price']

    def get_min_delivery_time(self, obj):
        """
        Returns the minimum delivery time in days of the offer details of the given offer.

        :param obj: The given offer.
        :return: The minimum delivery time in days of the offer details.
        """
        return obj.details.aggregate(min_delivery=models.Min('delivery_time_in_days'))['min_delivery']

    def get_user_details(self, obj):
        """
        Returns the user details of the given offer.

        :param obj: The given offer.
        :return: A dictionary containing the user details of the given offer.
        """
        user = obj.user
        profile = user.profile
        return {
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "username": profile.username
        }

    def validate(self, attrs):
        """
        Validates the given data and returns a dictionary with the validated details.

        This method checks that the given data contains valid offer details. It loops
        through the given details and validates each one using the OfferDetailSerializer.
        If any detail is invalid, it appends the errors to the errors list. If the list
        of errors is not empty after validation, it raises a serializers.ValidationError
        with the list of errors.

        If all details are valid, it sets the validated_details key in the attrs dictionary
        to a list of validated details and returns the attrs dictionary.

        :param attrs: The given data.
        :return: A dictionary with the validated details.
        """
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
        """
        Updates an offer and its related offer details.

        This method loops through the validated data and updates the corresponding
        fields of the offer instance. If the validated data contains a 'details' key,
        it calls the `_update_details` method to update the related offer details.

        :param instance: The offer instance to update.
        :param validated_data: The validated data to update the offer with.
        :return: The updated offer instance.
        """
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if details_data:
            self._update_details(instance, details_data)
        instance.save()
        return instance

    def _update_details(self, instance, details_data):
        """
        Updates the offer details for the given offer instance.

        This method iterates through the provided `details_data` to update the
        existing offer details associated with the `instance`. If a detail with
        a matching ID is found, it updates the existing detail using the
        `_update_detail_instance` method. If no matching ID is found, it creates
        a new offer detail. Any existing offer details not present in the
        `details_data` are deleted.

        :param instance: The offer instance whose details are being updated.
        :param details_data: A list of dictionaries containing the data for
                            each detail to update or create.
        """

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
        """
        Updates the given offer detail instance with the provided data.

        This method iterates through the given `detail_data` and sets the
        corresponding attribute on the `detail_instance` using the provided value.
        Finally, it saves the updated offer detail instance.

        :param detail_instance: The offer detail instance being updated.
        :param detail_data: A dictionary containing the data to update the
                            offer detail instance with.
        """
        for attr, value in detail_data.items():
            setattr(detail_instance, attr, value)
        detail_instance.save()