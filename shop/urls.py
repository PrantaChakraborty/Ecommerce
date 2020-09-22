from django.urls import path
from .views import product_list, product_detail


urlpatterns = [
    path(r'', product_list, name='product_list'),
    path(r'(<category_slug>[-\w]+)/', product_list, name='product_list_by_category'),
    path(r'(<id>\d+)/(<slug>[-\w]+)/', product_detail, name='product_detail'),
]
