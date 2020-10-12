from django.shortcuts import render
from django.urls import reverse

from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created

from django.shortcuts import render, redirect

# staff member to view order
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from .models import Order

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
