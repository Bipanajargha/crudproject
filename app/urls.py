from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('',home, name = 'home'),
    path('form/', form , name = 'form'),
    path('list/',list, name = 'list'),
    path('about/', about, name = 'about'),
    path('services/',services, name = 'services'),
    path('delete_data/<int:pk>',delete_data, name="delete_data"),
    path('edit/<int:pk>',edit, name = "edit"),
    path('login/', log_in , name='log_in' ),
    path('register/', register, name ='register'),
    path('reg/user', FormCreate.as_view(), name='api_form'),
    path('list/user', ListReg.as_view(), name ="list_reg"),
    path('details/<int:pk>/', FormDetailApi.as_view(), name='api_form_detail'),

    #register
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),

    # jwt
    path('api/auth/login/', LoginAPIView.as_view(), name='api_auth_login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    #log out
    path('api/auth/logout/', LogoutAPIView.as_view(), name='api_logout'),
]