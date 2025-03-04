from rest_framework import generics
from .serializers import ReviewSerializer
from reviews.models import Review
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

class ReviewListAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    ordering_fields = ['updated_at', 'rating']
    filterset_fields = ['business_user_id', 'reviewer_id']
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        if not self.request.user.profile.type == 'customer':
            raise PermissionDenied("Nur Kunden haben Zugriff auf diese Funktion.")
        serializer.save(reviewer=self.request.user)

class ReviewDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        if serializer.instance.reviewer != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Nur der Verfasser oder ein Admin darf diese Bewertung bearbeiten.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.reviewer != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Nur der Verfasser oder ein Admin darf diese Bewertung löschen.")
        instance.delete()

    
