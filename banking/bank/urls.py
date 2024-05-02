from django.urls import path
from .views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('userregister/', RegisterAPIView.as_view(), name='user-register'),
    path('login/', LoginAPIView.as_view(), name='bank_login'),
    path('profile/update/', ProfileUpdateAPIView.as_view(), name='profile-update'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),

]
