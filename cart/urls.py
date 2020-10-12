from django.urls import path
from . import views

app_name = 'cart'
urlpatterns = [
    path(r'', views.cart_detail, name='cart_detail'),
    path(r'(/add/<product_id>[-\w])/', views.cart_add, name='cart_add'),
    path(r'(/remove/<product_id>[-\w]+)/', views.cart_remove, name='cart_remove'),
]
