from django.urls import path
from . import views


urlpatterns = [
    path("base-info/", views.BaseInfoView.as_view(), name="base-info"),
]