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
        """
        Returns a list of all orders for the currently authenticated user, 
        which are either created by the user or assigned to the user.
        """
        orders = self.get_user_orders(request.user)
        return Response(OrderListSerializer(orders, many=True).data, status=status.HTTP_200_OK)
    
    def get_user_orders(self, user):
        """
        Returns all orders for the given user, either created by the user or assigned to the user.
        
        :param user: The user whose orders are to be returned.
        :return: A QuerySet of orders.
        """
        if not user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(Q(business_user=user) | Q(customer_user=user)).order_by('-created_at')
    
    def post(self, request):
        """
        Creates a new order with the given data.

        The request body should contain the data for the new order, which must contain the following fields:
        - `title`: The title of the order.
        - `offer_type`: The type of the offer.
        - `offer_detail_id`: The ID of the offer detail.
        - `features`: A JSON object containing additional features of the order.
        - `revisions`: The number of revisions for the order.

        The order will be assigned to the currently authenticated user.

        :return: The newly created order with a 201 status code, or a 400 status code if the data is invalid.
        """
        if not self.is_customer(request.user):
            return Response({'detail': ['Nur Kunden können Aufträge erteilen']}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrderPostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def is_customer(self, user):
        """
        Checks if the given user is a customer.

        This method checks if the given user is authenticated and if its profile type is 'customer'.
        If the user is a customer, it returns True, otherwise it returns False.

        :param user: The user to check.
        :return: True if the user is a customer, False otherwise.
        """
        return user.is_authenticated and getattr(user.profile, 'type', None) == 'customer'
    

class OrderSingleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    
    def get(self, request, pk):
        order = Order.objects.get(pk=pk)
        serializer = OrderListSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if order.business_user != request.user:
            return Response({"detail": ["Nur der Business-Nutzer kann den Status einer Bestellung ändern."]}, status=status.HTTP_403_FORBIDDEN)

        status_value = request.data.get('status')
        if status_value not in ['in_progress', 'completed', 'cancelled']:
            return Response({"detail": ["Ungültiger Status. Erlaubte Werte: 'in_progress', 'completed', 'cancelled'."]}, status=status.HTTP_400_BAD_REQUEST)

        order.status = status_value
        order.save()

        full_serializer = OrderListSerializer(order)
        return Response(full_serializer.data, status=status.HTTP_200_OK)


    def delete(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        
        if not request.user.is_staff:
            return Response({"detail": ["Nur Admin-Benutzer können Bestellungen löschen."]}, status=status.HTTP_403_FORBIDDEN)
        
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class BusinessNotCompletedOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        """
        Returns the number of non-completed orders for the business user with the given ID.

        The response will be a JSON object with a single key-value pair, where the key is `order_count`
        and the value is the number of orders.

        If the user does not exist, a 404 status code will be returned with a JSON object containing
        a single error message.

        :param request: The incoming request.
        :param pk: The ID of the business user.
        :return: A JSON object with the number of non-completed orders with a 200 status code, or a 404 status code if the user does not exist.
        """
        try:
            business_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": ["Der angegebene Nutzer existiert nicht."]}, status=status.HTTP_404_NOT_FOUND)
        orders = Order.objects.filter(business_user=business_user, status='in_progress')
        return Response({'order_count': orders.count()})
    

class BusinessCompletedOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        """
        Returns the number of completed orders for the business user with the given ID.

        The response will be a JSON object with a single key-value pair, where the key is `completed_order_count`
        and the value is the number of orders.

        If the user does not exist, a 404 status code will be returned with a JSON object containing
        a single error message.

        :param request: The incoming request.
        :param pk: The ID of the business user.
        :return: A JSON object with the number of completed orders with a 200 status code, or a 404 status code if the user does not exist.
        """
        try:
            business_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": ["Der angegebene Nutzer existiert nicht."]}, status=status.HTTP_404_NOT_FOUND)
        orders = Order.objects.filter(business_user=business_user, status='completed')
        return Response({'completed_order_count': orders.count()}, status=status.HTTP_200_OK)