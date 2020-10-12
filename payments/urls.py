from django.urls import path
from . import views

app_name = 'payments'
urlpatterns = [
    path('', views.payment_process, name='process'),
    path('status/', views.validation_check, name='validation_check'),
    path('confirm/<val_id>/<tran_id>/', views.payment_complete, name='payment_complete'),
    path('fail/', views.payment_fail, name='payment_fail'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),


]