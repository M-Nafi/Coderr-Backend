from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('registration/', views.RegistrationAPIView.as_view()),
    path('profile/<int:id>/', views.ProfileDetailsAPIView.as_view()),
    path('profiles/business/', views.ProfileListBusiness.as_view()),
    path('profiles/customer/', views.ProfileListCustomers.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)