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
        """
        Returns the appropriate permissions for the current request.

        If the request method is POST, this method returns a list containing 
        the IsAuthenticated permission to ensure that only authenticated users 
        can create a new review. For all other request methods, it returns the 
        default permissions defined in the parent class.

        :return: A list of permission instances.
        """
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """
        Handles the creation of a review.

        This method checks if the current user is a customer before allowing the creation of a review.
        If the user is not a customer, it raises a PermissionDenied exception. If the user is a customer,
        it proceeds to save the review with the current user as the reviewer.

        :param serializer: The serializer instance containing the review data.
        :raises PermissionDenied: If the user does not have a customer profile.
        """
        if not self.request.user.profile.type == 'customer':
            raise PermissionDenied("Nur Kunden haben Zugriff auf diese Funktion.")
        serializer.save(reviewer=self.request.user)

class ReviewDetailsAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        """
        Returns the appropriate permissions for the current request.

        If the request method is GET, it returns a list containing the AllowAny
        permission to allow all users to view reviews. For all other request methods,
        it returns a list containing the IsAuthenticated permission to ensure that
        only authenticated users can create, update, or delete reviews.

        :return: A list of permission instances.
        """
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def update(self, request, *args, **kwargs):
        """
        Updates a review instance.

        This method checks if the request user is either the reviewer of the review or an admin.
        If the user is not the reviewer or an admin, it raises a PermissionDenied exception.
        If the user is the reviewer or an admin, it proceeds to update the review with the given data.

        :param request: The incoming request.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :raises PermissionDenied: If the user does not have permission to update the review.
        :return: A response containing the updated review data.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        """
        Updates a review instance.

        This method checks if the request user is either the reviewer of the review or an admin.
        If the user is not the reviewer or an admin, it raises a PermissionDenied exception.
        If the user is the reviewer or an admin, it proceeds to save the review with the given data.

        :raises PermissionDenied: If the user does not have permission to update the review.
        """
        if serializer.instance.reviewer != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Nur der Verfasser oder ein Admin darf diese Bewertung bearbeiten.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Deletes a review instance.

        This method checks if the request user is either the reviewer of the review or an admin.
        If the user is not the reviewer or an admin, it raises a PermissionDenied exception.
        If the user is the reviewer or an admin, it proceeds to delete the review.

        :raises PermissionDenied: If the user does not have permission to delete the review.
        """
        if instance.reviewer != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Nur der Verfasser oder ein Admin darf diese Bewertung löschen.")
        instance.delete()

    
