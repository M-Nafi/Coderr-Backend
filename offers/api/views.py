from rest_framework.exceptions import APIException  
from rest_framework.pagination import PageNumberPagination  
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView  
from offers.models import Offer  
from offers.api.serializers import OfferSerializer  
from rest_framework.permissions import IsAuthenticatedOrReadOnly  
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import SearchFilter, OrderingFilter   
from offers.api.ordering import OrderingHelperOffers  
from django.db.models import Min 
from offers.api.permissions import IsOwnerOrAdmin  
from offers.api.serializers import OfferSingleDetailsSerializer, AllOfferDetailsSerializer, OfferDetailSerializer
from django.shortcuts import get_object_or_404  
from rest_framework.exceptions import PermissionDenied  
from rest_framework.response import Response  
from rest_framework import status  
from rest_framework.views import APIView 
from offers.models import OfferDetail  
from django.utils.timezone import now  
from rest_framework.permissions import AllowAny, IsAuthenticated



class OfferPagination(PageNumberPagination):  
    max_page_size = 6  
    page_size = 6  
    page_size_query_param = 'page_size' 


class BusinessProfileRequired(APIException):  
    status_code = 403  
    default_code = "business_profile_required"  
    default_detail = {"detail": ["Nur Geschäftskunden ist die Erstellung von Angeboten erlaubt."]}  


class OfferListAPIView(ListCreateAPIView):  
    queryset = Offer.objects.annotate(min_price=Min('details__price'))  
    serializer_class = OfferSerializer 
    permission_classes = [IsAuthenticated] 
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]  
    pagination_class = OfferPagination  
    filterset_fields = ['user'] 
    search_fields = ['title', 'description']  


    def get_permissions(self):
        """
        Returns the appropriate permissions for the current request.

        If the request method is GET, it returns a list containing the AllowAny
        permission to allow all users to view offers. For all other request methods,
        it returns the default permissions defined in the parent class.

        :return: A list of permission instances.
        """
        if self.request.method == 'GET': 
            return [AllowAny()]
        return super().get_permissions()
    
    def get_queryset(self):  
        """
        Returns a filtered and ordered queryset of offers.

        The queryset is filtered based on the following query parameters:
        - `creator_id`: the id of the user who created the offer
        - `min_price`: the minimum price of the offer
        - `max_delivery_time`: the maximum delivery time of the offer

        The queryset is ordered by the `ordering` query parameter, which defaults to `updated_at`.
        """
        queryset = Offer.objects.annotate(min_price=Min('details__price'))  
        filters = {  
            'user_id': self.request.query_params.get('creator_id'),  
            'min_price__gte': self.request.query_params.get('min_price'),  
            'details__delivery_time_in_days__lte': self.request.query_params.get('max_delivery_time')  
        }
        for field, value in filters.items():  
            if value:
                queryset = queryset.filter(**{field: value})  

        ordering = self.request.query_params.get('ordering', 'updated_at')  
        return OrderingHelperOffers.apply_ordering(queryset, ordering=ordering)  

    def perform_create(self, serializer): 
        """
        Handles the creation of an offer.

        This method checks if the current user has a business profile before
        allowing the creation of an offer. If the user is not a business user,
        it raises a BusinessProfileRequired exception. If the user is a business
        user, it proceeds to save the offer with the current user as the owner.

        :param serializer: The serializer instance containing the offer data.
        :raises BusinessProfileRequired: If the user does not have a business profile.
        """
        if not self.is_business_user(self.request.user): 
            raise BusinessProfileRequired() 
        serializer.save(user=self.request.user)  

    def is_business_user(self, user):  
        """
        Checks if the given user is a business user.

        This method checks if the given user has a profile and if its type is 'business'.
        If the user is a business user, it returns True, otherwise it returns False.

        :param user: The user to check.
        :return: True if the user is a business user, False otherwise.
        """
        profile = getattr(user, 'profile', None)  
        return profile and profile.type == 'business'  


class OfferDetailAPIView(APIView):  
    permission_classes = [IsAuthenticated]  

    def get(self, request, pk, format=None):  
        offer = get_object_or_404(OfferDetail, id=pk)  
        serializer = OfferSingleDetailsSerializer(offer) 
        return Response(serializer.data, status=status.HTTP_200_OK)  


class OfferDetailsAPIView(RetrieveUpdateDestroyAPIView): 
    queryset = Offer.objects.prefetch_related('details') 
    serializer_class = AllOfferDetailsSerializer 
    permission_classes = [IsAuthenticated] 

    def get_permissions(self): 
        """
        Returns the appropriate permissions for the current request.

        If the request method is PATCH, it returns a list containing the IsOwnerOrAdmin 
        permission. For all other request methods, it returns the default permissions 
        defined in the parent class.

        :return: A list of permission instances.
        """
        if self.request.method == 'PATCH':  
            return [IsOwnerOrAdmin()]  
        return super().get_permissions() 
    
    def get(self, request, pk, format=None):
        offer = get_object_or_404(Offer, id=pk)
        serializer = OfferSerializer(offer)
        data = dict(serializer.data)
        user_details = data.pop("user_details", None)

        return Response(data, status=status.HTTP_200_OK)

        

    def update(self, request, pk, format=None, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', True))
        serializer.is_valid(raise_exception=True)
    
        details_data = request.data.get('details')
        for detail_data in details_data:
            detail_id = detail_data.get('id')
            if detail_id:
                OfferDetail.objects.filter(id=detail_id, offer=instance).update(**detail_data)
        serializer.save()

        instance.updated_at = now()
        

        updated_data = {
            'id': instance.id,
            'title': serializer.validated_data.get('title', instance.title),
            'description': serializer.validated_data.get('description', instance.description),
            'details': OfferDetailSerializer(instance.details.all(), many=True).data,
            'image': instance.image.url if instance.image else None
        }

        return Response(updated_data, status=status.HTTP_200_OK)
        

    def delete(self, request, pk, *args, **kwargs):  
        """
        Deletes the offer with the given ID.

        This method first checks if the requesting user has permission to delete
        the offer. If the user does not have permission, it raises a PermissionDenied
        exception. If the user does have permission, it deletes the offer and returns
        an empty response with a status indicating successful deletion.

        :param request: The incoming request.
        :param pk: The primary key of the offer to delete.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :raises PermissionDenied: If the user does not have permission to delete the offer.
        :return: An empty response with a status indicating successful deletion.
        """
        offer = get_object_or_404(Offer, id=pk)
        if not self.has_permission_to_delete(request.user, offer):  
            raise PermissionDenied({"detail": "Nur der Ersteller oder ein Admin kann dieses Angebot entfernen."})  
        offer.delete() 
        return Response({}, status=status.HTTP_204_NO_CONTENT)  

    def has_permission_to_delete(self, user, offer):  
        """
        Checks if the given user has permission to delete the given offer.

        A user has permission to delete an offer if they are either the creator of
        the offer or an admin with a business profile.

        :param user: The user to check.
        :param offer: The offer to check.
        :return: True if the user has permission to delete the offer, False otherwise.
        """
        return user == offer.user or user.is_staff and (user.profile.type == 'business' or user.is_staff)  