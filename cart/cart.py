from decimal import Decimal
from django.conf import settings
from shop.models import Product
from coupons.models import Coupon


class Cart:
    def __init__(self, request):
        """
        initializing the cart
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        self.coupon_id = request.session.get('coupon_id')  # getting the coupon id from session
        if not cart:
            # save an empty cart
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    # for add items it cart
    def add(self, product, quantity=1, update_quantity=False):
        """
        add a product to the cart or update it's quality
        """
        product_id = str(product.id)  # converted to string because JSON use only string data
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)
                                     }
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity  # increment the quantity
        self.save()  # saving the state of the quantity after update

    # to save the card
    def save(self):
        # update the session cart
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True  # mark the session as modified

    # to remove item form cart
    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        product_ids = self.cart.keys()
        # get the object and add them to cart
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
            """
             yield is a keyword in Python that is used to return from a
             function without destroying the states of its local 
             variable and when the function is called, the execution 
             starts from the last yield statement.
            """

    def __len__(self):
        # count all items in cart
        return sum(item['quantity'] for item in self.cart.values())

    # total price
    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    # clear the session
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    # for getting the model details
    @property
    def coupon(self):
        if self.coupon_id:
            return Coupon.objects.get(pk=self.coupon_id)

    # calculating total discount amount
    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal('100')) * self.get_total_price()
        return Decimal('0')

    # retuning total cost after applying coupons
    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()


