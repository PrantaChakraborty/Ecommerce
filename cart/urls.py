from django.urls import path
from . import views

urlpatterns = [
    path(r'', views.cart_detail, name='cart_detail'),
    path(r'add/<product_id>/', views.cart_add, name='cart_add'),
    path(r'remove/<product_id>/', views.cart_remove, name='cart_remove'),
]
