from rest_framework import generics
from .serializers import ReviewSerializer
from reviews.models import Review
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class ReviewListAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    ordering_fields = ['updated_at', 'rating']
    filterset_fields = ['business_user_id', 'reviewer_id']
    filter_backends = [filters.Orderingfilter, DjangoFilterBackend]
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        if not self.request.user.profile.type == 'customer':
            raise PermissionDenied("Nur Kunden haben Zugriff auf diese Funktion.")
        serializer.save(reviewer=self.request.user)