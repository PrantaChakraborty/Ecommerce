import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Order, OrderItem


# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']  # products in site


# converting order into csv
def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)

    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # write the first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # write data in rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = 'Export to CSV'


# for view each order in another page
def order_detail(obj):
    return mark_safe("<a href='{}'>View</a>".format(reverse('orders:admin_order_detail', args=[obj.id])))


order_detail.allow_tags = True


# for printing invoice
def order_pdf(obj):
    return mark_safe("<a href='{}'>PDF</a>".format(reverse('orders:admin_order_pdf', args=[obj.id])))


order_pdf.allow_tags = True
order_pdf.short_description = 'PDF invoice'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'address',
                    'postal_code', 'city', 'country', 'phone',
                    'paid', 'created', 'updated', order_detail, order_pdf]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    actions = [export_to_csv]  # added export to csv function


admin.site.register(Order, OrderAdmin)
