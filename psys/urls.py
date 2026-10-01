from django.urls import path
from . import views

urlpatterns = [
    path('customer/search/', views.customer_search, name='customer_search'),
    path('customer/register/', views.customer_register, name='customer_register'),
    path('customer/delete/', views.customer_delete, name='customer_delete'),
    path('customer/edit/', views.customer_edit, name='customer_edit'),
]