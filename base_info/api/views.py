from django.db.models import Avg
from rest_framework.response import Response
from rest_framework.views import APIView
from user_auth.models import Profile
from reviews.models import Review
from offers.models import Offer
from rest_framework.permissions import AllowAny


class BaseInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve aggregated statistics.

        This method returns a JSON response containing the following data:
        - average_rating: The average rating of all reviews, rounded to one decimal place.
        - business_profile_count: The total number of business profiles.
        - review_count: The total number of reviews.
        - offer_count: The total number of offers.
        """

        review_count = Review.objects.count()
        rating_aggregation = Review.objects.aggregate(avg_rating =Avg('rating'))
        average_rating = rating_aggregation.get('avg_rating')
        average_rating = round(average_rating, 1) if average_rating is not None else 0
        business_profile_count = Profile.objects.filter(type='business').count()
        offer_count = Offer.objects.count()

        data = {
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "review_count": review_count,            
            "offer_count": offer_count,
        }
        return Response(data)