from django.contrib import admin
from .models import Order, OrderItem

# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']  # products in site


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'address',
                    'postal_code', 'city', 'country', 'phone',
                    'paid', 'created', 'updated']
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)