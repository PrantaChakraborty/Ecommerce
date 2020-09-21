from django.urls import path
from . import views

urlpatterns = [
    path(r'', views.cart_detail, name='cart_detail'),
    path(r'(?P/add/<product_id>[-\w])/$', views.cart_add, name='cart_add'),
    path(r'(?P/remove/<product_id>[-\w]+)/$', views.cart_remove, name='cart_remove'),
]
