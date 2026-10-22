from django.urls import path
from . import views

urlpatterns = [
    path('customer/search/', views.customer_search, name='customer_search'),
    path('customer/register/', views.customer_register, name='customer_register'),
    path('customer/delete/', views.customer_delete, name='customer_delete'),
    path('customer/edit/', views.customer_edit, name='customer_edit'),
    path('customer/list/',views.customer_list,name='customer_list'),
    path('order/monthly/',views.monthly_order_summary,name='monthly_order_summary'),
    path('order/yearly/',views.yearly_order_summary,name='yearly_order_summary'),
    path('order/product/',views.product_order_summary,name='product_order_summary'),
]