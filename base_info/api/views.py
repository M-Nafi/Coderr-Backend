from django.db.models import Avg, Count
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BaseInfoSerializer
from ..models import Review, BusinessProfile, Offer
from rest_framework.permissions import AllowAny


class BaseInfoView(APIView):
    permission_classes = [AllowAny] 
    def get(self, request):
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 0
        business_profile_count = BusinessProfile.objects.count()
        offer_count = Offer.objects.count()

        data = {
            "review_count": review_count,
            "average_rating": round(average_rating, 1),  
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }
        serializer = BaseInfoSerializer(data)

        return Response(serializer.data)