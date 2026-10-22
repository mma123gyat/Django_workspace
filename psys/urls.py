from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.employee_login, name='employee_login'),
    path('logout/', views.employee_logout, name='employee_logout'),

    path(
        'customer/search/',
        views.employee_login_required(views.customer_search),
        name='customer_search'
    ),
    path(
        'customer/register/',
        views.employee_login_required(views.customer_register),
        name='customer_register'
    ),
    path(
        'customer/delete/',
        views.employee_login_required(views.customer_delete),
        name='customer_delete'
    ),
    path(
        'customer/edit/',
        views.employee_login_required(views.customer_edit),
        name='customer_edit'
    ),
    path(
        'customer/list/',
        views.employee_login_required(views.customer_list),
        name='customer_list'
    ),
    path(
        'order/monthly/',
        views.employee_login_required(views.monthly_order_summary),
        name='monthly_order_summary'
    ),
    path(
        'order/yearly/',
        views.employee_login_required(views.yearly_order_summary),
        name='yearly_order_summary'
    ),
    path(
        'order/product/',
        views.employee_login_required(views.product_order_summary),
        name='product_order_summary'
    ),
]