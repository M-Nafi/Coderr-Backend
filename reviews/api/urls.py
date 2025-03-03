from django.urls import path
from . import views

urlpatterns = [
    path('reviews/', views.ReviewListAPIView.as_view(), name='reviews'),
    path('reviews/<int:pk>/', views.ReviewDetailsAPIView.as_view(), name='review'),
]