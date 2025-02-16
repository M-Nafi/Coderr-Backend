from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from orders.api.serializers import OrderListSerializer, OrderPostSerializer, OrderPatchSerializer
from orders.models import Order
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

class OrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = self.get_user_orders(request.user)
        return Response(OrderListSerializer(orders, many=True).data, status=status.HTTP_200_OK)
    
    def get_user_orders(self, user):
        if not user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(Q(business_user=user) | Q(customer_user=user)).order_by('-created_at')
    
    def post(self, request):
        if not self.is_customer(request.user):
            return Response({'detail': ['Nur Kunden können Aufträge erteilen']}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrderPostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def is_customer(self, user):
        return user.is_authenticated and getattr(user.profile, 'type', None) == 'customer'
    

class OrderSingleAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        serializer = OrderListSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        is_company = order.business_user == request.user
        is_admin = request.user.is_staff
        if not (is_company or is_admin):
            return Response({"detail": ["Nur der Ersteller oder ein Admin kann diese Aufgabe bearbeiten."]}, status=status.HTTP_403_FORBIDDEN)
        serializer = OrderPatchSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            full_serializer = OrderListSerializer(order)
            return Response(full_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({"detail": ["Nur der Anbieter oder ein Admin kann dieses löschen."]}, status=status.HTTP_403_FORBIDDEN)
        order = get_object_or_404(Order, pk=pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class BusinessNotCompletedOrderAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, pk):
        try:
            business_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": ["Der angegebene Nutzer existiert nicht."]}, status=status.HTTP_404_NOT_FOUND)
        orders = Order.objects.filter(business_user=business_user, status='in_progress')
        return Response({'order_count': orders.count()}, status=status.HTTP_200_OK)
    

class BusinessCompletedOrderAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self, request, pk):
        try:
            business_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": ["Der angegebene Nutzer existiert nicht."]}, status=status.HTTP_404_NOT_FOUND)
        orders = Order.objects.filter(business_user=business_user, status='completed')
        return Response({'completed_order_count': orders.count()}, status=status.HTTP_200_OK)