from django.db import models
from shop.models import Product
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

from coupons.models import Coupon

# Create your models here.


class Order(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=11)
    country = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    coupon = models.ForeignKey(Coupon, related_name='orders', null=True, blank=True, on_delete=models.CASCADE)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0),
                                                          MaxValueValidator(0)])

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order {}'.format(self.id)

# used to calculate total price of a user order items
    def get_total_cost(self):
        total_cost = sum(item.get_cost() for item in self.items.all())
        total_cost_after_discount = total_cost - (total_cost * (self.discount / Decimal('100')))
        return total_cost_after_discount

    def get_total_quantity(self):
        return sum(item.get_quantity() for item in self.items.all())

    def get_all_products_name(self):
        product_list = []
        return product_list.append(item.get_product_name() for item in self.items.all())


# oder for every item
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

# used to calculate single item price
    def get_cost(self):
        total = self.price * self.quantity
        return total

# quantity for each product
    def get_quantity(self):
        return self.quantity

# product name
    def get_product_name(self):
        return self.product.name
