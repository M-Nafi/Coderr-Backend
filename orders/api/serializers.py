from rest_framework import serializers
from orders.models import Order
from offers.models import OfferDetail
from django.contrib.auth.models import User


class OrderListSerializer(serializers.ModelSerializer):
    customer_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    business_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    offer_detail_id = serializers.PrimaryKeyRelatedField(queryset=OfferDetail.objects.all())
    features = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            "id", "customer_user", "business_user", "title", "revisions",
            "delivery_time_in_days", "price", "features", "offer_type",
            "status", "created_at", "updated_at"
        ]

    def get_features(self, obj):
        return obj.offer_detail_id.features if hasattr(obj.offer_detail_id, 'features') else []
    


class OrderPostSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.PrimaryKeyRelatedField(queryset=OfferDetail.objects.all())

    class Meta:
        model = Order
        fields = ['offer_detail_id']  

    def create(self, validated_data):
        """
        Creates a new order with the given validated data and the user from the request context.
        
        :param validated_data: The validated data to create the order with.
        :raises serializers.ValidationError: If the request context is missing or invalid.
        :return: The created order instance.
        """
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError({"detail": "Request context fehlt oder ungültig."})

        return Order.objects.create(
            customer_user=request.user,  
            **validated_data  
        )
    

class OrderPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def update(self, instance, validated_data):
        """
        Updates the given order instance with the given validated data.

        This method updates the `status` field of the given order instance with the value
        provided in the validated data. If the `status` key is not present in the validated
        data, it does not update the `status` field.

        :param instance: The order instance to update.
        :param validated_data: The validated data to update the order with.
        :return: The updated order instance.
        """
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance