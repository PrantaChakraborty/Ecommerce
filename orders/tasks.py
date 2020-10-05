from celery import shared_task
from django.core.mail import send_mail
from . models import Order


@shared_task
def order_created(order_id):
    """
    task to send email when an order is successfully created
    """
    order = Order.objects.get(pk=order_id)
    subject = 'Order nr. {}'.format(order_id)
    message = 'Dear {}, \n\nYou have successfully placed an order.Your order id is {}.'.format(order.first_name, order.id)
    mail_sent = send_mail(subject,
                          message,
                          'admin@myshop.com',
                          [order.email])
    return mail_sent
