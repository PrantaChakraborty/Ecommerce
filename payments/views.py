from django.conf import settings
from django.http import HttpResponse

from django.shortcuts import render,  get_object_or_404, redirect, HttpResponseRedirect
from django.template.loader import get_template

from django.urls import reverse
from django.contrib import messages
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt

from sslcommerz_python.payment import SSLCSession
from xhtml2pdf import pisa

from orders.models import Order
# from .models import Payment  # saving payment instance
# to send email
from django.core.mail import EmailMessage
# Create your views here.


# processing payments
def payment_process(request):
    # get the id from session
    order_id = request.session.get('order_id')
    # get the user from the model using id
    order = get_object_or_404(Order, pk=order_id)
    store_id = settings.STORE_ID  # sandbox order id
    store_password = settings.STORE_PASSWORD  # sandbox order pass
    my_payment = SSLCSession(sslc_is_sandbox=True, sslc_store_id=store_id, sslc_store_pass=store_password)
    success_url = request.build_absolute_uri(reverse('payments:validation_check'))  # for checking the validation
    fail_url = request.build_absolute_uri(reverse('payments:payment_fail'))  # if payment failed
    cancel_url = request.build_absolute_uri(reverse('payments:payment_cancel'))  # if payment cancel
    my_payment.set_urls(success_url=success_url, fail_url=fail_url, cancel_url=cancel_url, ipn_url=success_url)
    # get the total cost
    total_cost = order.get_total_cost()  # get the total cost from the method
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
    # print(response_data)
    return redirect(response_data['GatewayPageURL'])


@csrf_exempt
def validation_check(request):
    if request.method == 'POST' or request.method == 'post':
        payment_data = request.POST
        status = payment_data['status']
        if status == 'VALID':
            val_id = payment_data['val_id']
            tran_id = payment_data['tran_id']
            amount = payment_data['amount']
            messages.success(request, "Payment Complete")
            return HttpResponseRedirect(reverse('payments:payment_complete', kwargs={'val_id': val_id,
                                                                                     'tran_id': tran_id, 'amount': amount}))
        elif status == 'FAILED':
            messages.success(request, 'Sorry! Payment Failed')
        return render(request, 'payments/complete.html', {})


# active if purchase complete
@csrf_exempt
def payment_complete(request, val_id, tran_id, amount):
    # get the id from session
    order_id = request.session.get('order_id')
    # get the user from the model using id
    order = get_object_or_404(Order, pk=order_id)
    order.paid = True  # after successful payment
    order.save()  # saving the instance

    return render(request, 'payments/done.html', {'validation_id': val_id, 'transaction_id': tran_id, 'amount': amount})


# if payment failed
@csrf_exempt
def payment_fail(request):
    return render(request, 'payments/fail.html')


# if payment cancelled
@csrf_exempt
def payment_cancel(request):
    return render(request, 'payments/cancel.html')


def sent_email(order_id):
    order = get_object_or_404(Order, pk=order_id)
    # sending invoice by email after completion payment
    subject = 'My Shop - Invoice no.{}'.format(order.id)
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(subject, message, 'admin@myshop.com', [order.email])
    # generating pdf invoice
    template_path = 'orders/order/invoice.html'
    context = {'order': order}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="order_{}.pdf"'.format(order.id)
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    # if error then show some  view
    if pisa_status.err:
        return HttpResponse('we had some error')
    email.attach(response, 'application/pdf')
    email.send()