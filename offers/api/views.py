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
    permission_classes = [IsAuthenticatedOrReadOnly] 
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]  
    pagination_class = OfferPagination  
    filterset_fields = ['user'] 
    search_fields = ['title', 'description']  

    def get_permissions(self): 
        return [IsOwnerOrAdmin()] if self.request.method == 'POST' else super().get_permissions()  

    def get_queryset(self):  
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
        if not self.is_business_user(self.request.user): 
            raise BusinessProfileRequired() 
        serializer.save(user=self.request.user)  

    def is_business_user(self, user):  
        profile = getattr(user, 'profile', None)  
        return profile and profile.type == 'business'  


class OfferDetailAPIView(APIView):  
    permission_classes = [IsAuthenticatedOrReadOnly]  

    def get(self, request, pk, format=None):  
        offer = get_object_or_404(OfferDetail, id=pk)  
        serializer = OfferSingleDetailsSerializer(offer) 
        return Response(serializer.data, status=status.HTTP_200_OK)  


class OfferDetailsAPIView(RetrieveUpdateDestroyAPIView): 
    queryset = Offer.objects.prefetch_related('details') 
    serializer_class = AllOfferDetailsSerializer 
    permission_classes = [IsAuthenticatedOrReadOnly] 

    def get_permissions(self): 
        if self.request.method == 'PATCH':  
            return [IsOwnerOrAdmin()]  
        return super().get_permissions() 

    def update(self, request, *args, **kwargs):  
        instance = self.get_object() 
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))  
        serializer.is_valid(raise_exception=True)  
        serializer.save()  

        instance.updated_at = now()  
        instance.refresh_from_db()  

        updated_data = {  
            'id': instance.id,
            'title': serializer.validated_data.get('title', instance.title),
            'description': serializer.validated_data.get('description', instance.description),
            'details': OfferDetailSerializer(instance.details.all(), many=True).data,  
            'image': instance.image.url if instance.image else None  
        }
        return Response(updated_data, status=status.HTTP_200_OK)  

    def delete(self, request, pk, *args, **kwargs):  
        offer = get_object_or_404(Offer, id=pk)
        if not self.has_permission_to_delete(request.user, offer):  
            raise PermissionDenied({"detail": "Nur der Ersteller oder ein Admin kann dieses Angebot entfernen."})  
        offer.delete() 
        return Response({}, status=status.HTTP_200_OK)  

    def has_permission_to_delete(self, user, offer):  
        return user == offer.user or user.is_staff and (user.profile.type == 'business' or user.is_staff)  