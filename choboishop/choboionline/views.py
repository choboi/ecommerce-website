from django.shortcuts import get_object_or_404, render
from .models import Category, Product
from cart.forms import CartAddProductForm


def product_list(request, category_slug=None):
    """
    Display a list of products. Optionally filter by category.

    Args:
        request: The HTTP request object.
        category_slug (str, optional): The slug of the category to filter products by.

    Returns:
        HttpResponse: Rendered HTML page with the list of products.
    """
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(
        request,
        'shop/product/list.html',
        {
            'category': category,
            'categories': categories,
            'products': products,
        }
    )


def product_detail(request, id, slug):
    """
    Display details of a single product.

    Args:
        request: The HTTP request object.
        id (int): The ID of the product.
        slug (str): The slug of the product.

    Returns:
        HttpResponse: Rendered HTML page with product details.
    """
    product = get_object_or_404(
        Product, id=id, slug=slug, available=True
    )
    cart_product_form = CartAddProductForm()
    return render(
        request,
        'shop/product/detail.html',
        {'product': product, 'cart_product_form': cart_product_form}
    )
