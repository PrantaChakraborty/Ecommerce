from django.urls import path
from . import views

app_name = 'payments'
urlpatterns = [
    path('', views.payment_process, name='process'),
    path('status/', views.complete, name='complete'),
    path('confirm/<val_id>/<tran_id>/', views.purchase_complete, name='purchase_complete'),


]