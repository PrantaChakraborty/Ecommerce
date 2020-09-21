from django.urls import path
from . import views

urlpatterns = [
    path(r'', views.cart_detail, name='cart_detail'),
    path(r'^add/(?P<product_id>\d+)/$', views.cart_add, name='cart_add'),
    path(r'^remove/(?P<product_id>\d+)/$', views.cart_remove, name='cart_remove'),
]
