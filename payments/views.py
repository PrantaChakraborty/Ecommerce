from django.conf import settings
from django.shortcuts import render,  get_object_or_404, redirect, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt

from sslcommerz_python.payment import SSLCSession
from orders.models import Order
# Create your views here.


def payment_process(request):
    # get the id from session
    order_id = request.session.get('order_id')
    # get the user from the model using id
    order = get_object_or_404(Order, pk=order_id)
    store_id = settings.STORE_ID  # sandbox order id
    store_password = settings.STORE_PASSWORD  # sandbox order pass
    my_payment = SSLCSession(sslc_is_sandbox=True, sslc_store_id=store_id, sslc_store_pass=store_password)
    status_url = request.build_absolute_uri(reverse('payments:complete'))
    my_payment.set_urls(success_url=status_url, fail_url=status_url, cancel_url=status_url, ipn_url=status_url)
    # get the total cost
    total_cost = order.get_total_cost()
    # get the total items
    total_items = order.get_total_quantity()
    my_payment.set_product_integration(total_amount=Decimal(total_cost), currency='BDT', product_category='Mixed',
                                       product_name='None', num_of_item=total_items, shipping_method='Courier',
                                       product_profile='None')

    # customer info
    my_payment.set_customer_info(name=order.name, email=order.email, address1=order.address,
                                 city=order.city, postcode=order.postal_code, country=order.country,
                                 phone=order.phone)
    # shipping address
    my_payment.set_shipping_info(shipping_to=order.name, address=order.address, city=order.city,
                                 postcode=order.postal_code, country=order.country)

    response_data = my_payment.init_payment()
    print(response_data)
    return redirect(response_data['GatewayPageURL'])


@csrf_exempt
def complete(request):
    if request.method == 'POST' or request.method == 'post':
        payment_data = request.POST
        status = payment_data['status']
        if status == 'VALID':
            val_id = payment_data['val_id']
            tran_id = payment_data['tran_id']
            messages.success(request, "Payment Complete")
            return HttpResponseRedirect(reverse('payments:purchase_complete', kwargs={'val_id': val_id,
                                                                                      'tran_id': tran_id}))
        elif status == 'FAILED':
            messages.success(request, 'Sorry! Payment Failed')
        return render(request, 'payments/complete.html', {})


def purchase_complete(request, val_id, tran_id):
    return render(request, 'payments/done.html', {'validation_id': val_id, 'transaction_id': tran_id})
