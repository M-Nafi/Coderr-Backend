from rest_framework import serializers
from orders.models import Order
from offers.models import OfferDetail
from django.contrib.auth.models import User


class OrderListSerializer(serializers.ModelSerializer):
    customer_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    business_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    offer_detail_id = serializers.PrimaryKeyRelatedField(queryset=OfferDetail.objects.all())
    
    class Meta:
        model = Order
        fields = '__all__'


class OrderPostSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.PrimaryKeyRelatedField(queryset=OfferDetail.objects.all())

    class Meta:
        model = Order
        fields = ['offer_detail_id']  

    def create(self, validated_data):
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
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance