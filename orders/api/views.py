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
        """
        Returns a single order by its ID.

        The order will be returned with a 200 status code. If the order does not exist, a 404 status code will be returned.

        :param request: The request object.
        :param pk: The ID of the order to retrieve.
        :return: The retrieved order with a 200 status code, or a 404 status code if the order does not exist.
        """
        order = Order.objects.get(pk=pk)
        serializer = OrderListSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        """
        Updates an existing order with the given data.

        The request body should contain the data to update the order with. The
        data can be partial, meaning that only the fields provided will be
        updated.

        Only the creator of the order or an administrator can update the order.

        :param request: The incoming request.
        :param pk: The ID of the order to update.
        :return: The updated order with a 200 status code, or a 400 status code if the data is invalid.
        """
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
        """
        Deletes the order with the given ID.

        Only the creator of the order or an administrator can delete the order.

        :param request: The incoming request.
        :param pk: The ID of the order to delete.
        :return: An empty response with a status indicating successful deletion.
        """
        if not request.user.is_staff:
            return Response({"detail": ["Nur der Anbieter oder ein Admin kann dieses löschen."]}, status=status.HTTP_403_FORBIDDEN)
        order = get_object_or_404(Order, pk=pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class BusinessNotCompletedOrderAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
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
    permission_classes = [IsAuthenticatedOrReadOnly]
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