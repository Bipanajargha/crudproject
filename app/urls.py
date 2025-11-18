from django.urls import path
from .views import *

urlpatterns = [
    path('',home, name = 'home'),
    path('form/', form , name = 'form'),
    path('list/',list, name = 'list'),
    path('delete_data/<int:pk>',delete_data, name="delete_data"),
    path('edit/<int:pk>',edit, name = "edit"),
    
    path('reg/user', FormCreate.as_view(), name='api_form'),
    path('list/user', ListReg.as_view(), name ="list_reg"),
    path('details/<int:pk>/', FormDetailApi.as_view(), name='api_form_detail'),
]