import redis
from django.conf import settings
from .models import Product


# connect to redis
r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)


class Recommender:
    def __int__(self):
        pass

    def get_product_key(self, id):
        return 'product:{}:purchased_with'.format(id)

    def products_bought(self, products):
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # get the other products bought with
                if product_id != with_id:
                    # increment score for product purchased together
                    r.zincrby(self.get_product_key(product_id), with_id, amount=1)

    def suggest_products_for(self, products, max_result=6):
        product_ids = [p.id for p in products]
        if (len(products)) == 1:
            suggestions = r.zrange(self.get_product_key(product_ids[0]), 0, -1, desc=True)[:max_result]
        else:
            # generate a temporary key
            flat_ids = ''.join([str(id) for id in product_ids])
            temp_key = 'tmp_{}'.format(flat_ids)
            # multiple products, combine scores of all products
            # store the resulting sorted set in a temporary key
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(temp_key, keys)
            # remove ids for the products the recommendation is for
            r.zrem(temp_key, *product_ids)
            # get the product id by their score, descendent sort
            suggestions = r.zrange(temp_key, 0, -1, desc=True)[:max_result]
            # remove the temporary key
            r.delete(temp_key)
        suggested_product_ids = [int(id) for id in suggestions]

        # get suggested products and sort by order of appearance
        suggested_product = list(Product.objects.filter(id_in=suggested_product_ids))
        suggested_product.sort(key=lambda x: suggested_product_ids.index(x.id))
        return suggested_product

    def clear_purchase(self):
        for value in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(value))







