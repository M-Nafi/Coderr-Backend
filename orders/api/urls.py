from django.urls import path

from . import views


urlpatterns = [
    path('orders/', views.OrderListAPIView.as_view(), name='orders'),
    path('orders/<int:pk>/', views.OrderSingleAPIView.as_view(), name='order'),
    path('order-count/<int:pk>/', views.BusinessNotCompletedOrderAPIView.as_view(), name='not-completed'),
    path('completed-order-count/<int:pk>/', views.BusinessCompletedOrderAPIView.as_view(), name='completed'),
]
