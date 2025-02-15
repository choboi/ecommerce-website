import redis
from django.conf import settings
from .models import Product

# Connect to Redis
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)


class Recommender:
    def get_product_key(self, id):
        return f'product:{id}:purchased_with'

    def products_bought(self, products):
        """
        This function updates Redis with product pairs bought together.
        """
        product_ids = [p.id for p in products]

        for product_id in product_ids:
            for with_id in product_ids:
                # Avoid self-referencing a product as being bought with itself
                if product_id != with_id:
                    # Increment the score for products purchased together
                    r.zincrby(self.get_product_key(product_id), 1, with_id)

    def suggest_products_for(self, products, max_results=6):
        """
        Suggest products based on previous purchases.

        Args:
            products (list): List of Product objects.
            max_results (int): Maximum number of suggestions.

        Returns:
            list: List of recommended Product objects.
        """
        if not products:
            return []  # Return empty list if no products are given

        product_ids = [p.id for p in products]

        if len(products) == 1:
            # Only one product
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]), 0, -1, desc=True
            )[:max_results]
        else:
            # Generate a temporary key
            flat_ids = '_'.join(map(str, product_ids))  # Fixing key formatting
            tmp_key = f'tmp_{flat_ids}'
            # Multiple products: Combine scores of all products
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(tmp_key, keys)
            # Remove IDs for the products the recommendation is for
            r.zrem(tmp_key, *product_ids)
            # Get the product IDs by their score, sorted in descending order
            suggestions = r.zrange(
                tmp_key, 0, -1, desc=True
            )[:max_results]
            # Remove the temporary key
            r.delete(tmp_key)

        suggested_product_ids = [int(id) for id in suggestions]
        # Get suggested products and sort by order of appearance
        suggested_products = list(
            Product.objects.filter(id__in=suggested_product_ids)
        )
        suggested_products.sort(
            key=lambda x: suggested_product_ids.index(x.id)
        )

        return suggested_products

    def clear_purchases(self):
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))
