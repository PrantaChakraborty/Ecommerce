import os
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect

from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created
from .models import Order
# for pdf
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

# staff member to view order
from django.contrib.admin.views.decorators import staff_member_required


# Create your views here.


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # clear the cart
            cart.clear()
            order_created.delay(order.id)  # for sending confirmation email asynchronous task
            request.session['order_id'] = order.id  # storing the user id using session
            return redirect(reverse('payments:process'))  # redirect to the payment app

    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'cart': cart, 'form': form})


# view for staff members
@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})


# for handling static files
def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path

@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    template_path = 'orders/order/pdf.html'
    context = {'order': order}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="order_{}.pdf"'.format(order.id)
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    # if error then show some  view
    if pisa_status.err:
        return HttpResponse('we had some error')
    return response
