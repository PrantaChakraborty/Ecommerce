from .cart import Cart


# will executed everytime a template in rendered
def cart(request):
    return {'cart': Cart(request)}
