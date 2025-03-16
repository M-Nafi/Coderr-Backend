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
            "id", "customer_user", "business_user", "offer_detail_id", "title", "revisions",  
            "delivery_time_in_days", "price", "features", "offer_type",
            "status", "created_at", "updated_at"
        ]

    def get_features(self, obj):
        return obj.offer_detail_id.features if hasattr(obj.offer_detail_id, 'features') else []
    

class OrderPostSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.PrimaryKeyRelatedField(queryset=OfferDetail.objects.all())
    customer_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    business_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    features = serializers.SerializerMethodField()
    title = serializers.CharField(required=False)  

    class Meta:
        model = Order
        fields = [
            "id", "customer_user", "business_user", "title", "revisions", 
            "delivery_time_in_days", "price", "features", "offer_type", "status", 
            "created_at", "updated_at", "offer_detail_id"
        ]

    def create(self, validated_data):
        """
        Create a new order and assign it to the authenticated user (as customer_user).
        """
        request = self.context.get("request")
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError({"detail": ["Request context fehlt oder ungültig."]})

        offer_detail = validated_data.get("offer_detail_id")
        title = offer_detail.title if offer_detail else "Unbekanntes Angebot"
        price = offer_detail.price if offer_detail else 0
        offer_type = offer_detail.offer_type if offer_detail else "basic"
        
        order = Order.objects.create(
            customer_user=request.user,  
            title=title,
            price=price,
            offer_type=offer_type,
            **validated_data  
        )
        return order

    def get_features(self, obj):
        """
        Retrieves the features associated with the offer detail of the order.

        This method checks if the `offer_detail_id` of the provided order object
        has a `features` attribute. If it does, it returns the features. If not,
        it returns an empty list.

        :param obj: The order instance being serialized.
        :return: A list of features associated with the offer detail, or an empty list if none exist.
        """

        return obj.offer_detail_id.features if hasattr(obj.offer_detail_id, 'features') else []



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